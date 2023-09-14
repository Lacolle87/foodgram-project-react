from rest_framework import filters
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from recipes.models import Tag, Recipe, Ingredient
from api.serializer import (
    TagSerializer,
    RecipeSerializer,
    IngredientSerializer
)


class CustomUserViewSet(UserViewSet):
    pass


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    filter_fields = ('name', 'color')

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredients__ingredient', 'tags'
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'description', 'tags__name')
    pagination_class = 'rest_framework.pagination.PageNumberPagination'


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
