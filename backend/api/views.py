import hashlib

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeListSerializer,
    TagSerializer
)
from api.utils import convert_pdf
from recipes.models import (
    Favorite,
    Ingredient,
    RecipeIngredient,
    Recipe,
    ShoppingCart,
    Tag
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed('POST')

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PUT')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')

    def destroy(self, request, *args, **kwargs):
        raise MethodNotAllowed('DELETE')

    def finalize_response(self, request, response, *args, **kwargs):
        if (
                response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
                and request.method not in ['GET']
        ):
            response = Response(
                {'detail': 'Method Not Allowed.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )
        return super().finalize_response(request, response, *args, **kwargs)


class RecipeViewSet(ModelViewSet):
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == 'favorite' or self.action == 'cart':
            return FavoriteSerializer
        return RecipeCreateSerializer

    def get_queryset(self):
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist('tags', [])

        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()

        if self.request.user.is_authenticated:
            author = self.request.user

            if self.request.GET.get('is_favorited'):
                favorite_recipes_ids = Favorite.objects.filter(
                    user=author).values('recipe_id')
                return queryset.filter(pk__in=favorite_recipes_ids)

            if self.request.GET.get('is_in_shopping_cart'):
                cart_recipes_ids = ShoppingCart.objects.filter(
                    user=author).values('recipe_id')
                return queryset.filter(pk__in=cart_recipes_ids)

            author_id = self.request.query_params.get('author')
            if author_id:
                queryset = queryset.filter(author_id=author_id)

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            raise PermissionDenied("У вас нет прав на удаление этого рецепта.")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def post_list(model, user, pk):
        if model.objects.filter(user=user, recipe__id=pk).exists():
            return Response(
                {'errors': f'Рецепт уже добавлен в {model.__name__}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            recipe = Recipe.objects.get(pk=pk)
        except ObjectDoesNotExist:
            return Response(
                {'errors': 'Рецепт не существует'},
                status=status.HTTP_400_BAD_REQUEST
            )

        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeListSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_list(model, user, pk):
        try:
            recipe = Recipe.objects.get(id=pk)
        except ObjectDoesNotExist:
            return Response(
                {'errors': 'Рецепт не существует'},
                status=status.HTTP_404_NOT_FOUND
            )

        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'errors': f'Рецепт не добавлен в {model.__name__}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.post_list(Favorite, request.user, pk)
        return self.delete_list(Favorite, request.user, pk)

    @action(methods=['POST', 'DELETE'],
            detail=True,
            permission_classes=(IsAuthenticated,)
            )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.post_list(ShoppingCart, request.user, pk)
        return self.delete_list(ShoppingCart, request.user, pk)

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Прикол конечно у вас тут с названием файла, часа 3 сидел не мог понять
        почему Content-Disposition не задает имя, хотя все уходит и приходит.
        Оказывается на фронте название файла захардкожено. Я поменял в react,
        теперь название файла задается.
        """
        ingredient_list = {}
        recipe_ingredients = RecipeIngredient.objects.filter(
            recipe__cart__user=request.user
        ).values_list(
            'ingredient__name', 'ingredient__measurement_unit', 'amount'
        )
        for item in recipe_ingredients:
            name = item[0]
            if name not in ingredient_list:
                ingredient_list[name] = {
                    'measurement_unit': item[1],
                    'amount': item[2]
                }
            else:
                ingredient_list[name]['amount'] += item[2]

        pdf_buffer = convert_pdf(ingredient_list,
                                 'Список покупок',
                                 font='Arial',
                                 font_size=12)

        if pdf_buffer:
            ingredient_list_str = str(ingredient_list)
            hash_suffix = hashlib.md5(
                ingredient_list_str.encode()).hexdigest()[:5]
            filename = f'shopping_list_{hash_suffix}.pdf'

            response = FileResponse(
                pdf_buffer,
                as_attachment=True,
                filename=filename,
            )
        else:
            response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return response
