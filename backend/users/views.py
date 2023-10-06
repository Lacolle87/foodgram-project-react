from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from api.pagination import CustomPagination
from users.models import Subscription
from users.serializers import (
    SubscribeSerializer,
    UserCustomSerializer,
    UserCustomCreateSerializer,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = UserCustomSerializer

    @action(['GET'],
            detail=False,
            permission_classes=(IsAuthenticated,))
    def me(self, request, *args, **kwargs):
        serializer_class = UserCustomSerializer
        serializer = serializer_class(request.user,
                                      context={'request': request})
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = UserCustomCreateSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            user.set_password(
                serializer.validated_data['password'])
            user.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED,
                            headers=headers)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, serializer_class=SubscribeSerializer)
    def subscriptions(self, request):
        if request.user.is_authenticated:
            user = request.user
            queryset = User.objects.filter(following__user=user)
            paginated_queryset = self.paginate_queryset(queryset)
            serializer = self.get_serializer(
                paginated_queryset,
                many=True
            )
            return self.get_paginated_response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=SubscribeSerializer
    )
    def subscribe(self, request, id):
        if request.user.is_authenticated:
            user = request.user
            author = get_object_or_404(User, id=id)

            if self.request.method == 'POST':
                if user.id == author.id:
                    return Response(
                        {'errors': 'Нельзя подписаться на себя.'},
                        status=status.HTTP_400_BAD_REQUEST)
                if Subscription.objects.filter(
                        user=user,
                        author=author
                ).exists():
                    return Response(
                        {'errors': 'Вы уже подписаны.'},
                        status=status.HTTP_400_BAD_REQUEST)
                Subscription.objects.create(user=user, author=author)
                serializer = self.get_serializer(author)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            if not Subscription.objects.filter(
                    user=user,
                    author=author
            ).exists():
                if not User.objects.filter(id=id).exists():
                    return Response(
                        {'errors': 'Пользователь не существует.'},
                        status=status.HTTP_400_BAD_REQUEST)
                return Response(
                    {'errors': 'Вы не подписаны, либо отписались.'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription = get_object_or_404(
                Subscription,
                user=user,
                author=author)
            subscription.delete()
            return Response(
                'Вы отписались',
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
