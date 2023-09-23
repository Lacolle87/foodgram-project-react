from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from api.pagination import CustomPagination
from users.models import Subscription
from users.serializers import SubscribeSerializer, UserCustomSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = UserCustomSerializer
    queryset = User.objects.all()
    pagination_class = CustomPagination

    @action(detail=False, serializer_class=SubscribeSerializer)
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(paginated_queryset, many=True)
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        serializer_class=SubscribeSerializer
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, id=id)

        if self.request.method == 'POST':
            if user.id == author.id:
                return Response(
                    {'errors': 'Нельзя подписаться на себя.'},
                    status=status.HTTP_400_BAD_REQUEST)
            if Subscription.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны.'},
                    status=status.HTTP_400_BAD_REQUEST)
            Subscription.objects.create(user=user, author=author)
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if not Subscription.objects.filter(user=user, author=author).exists():
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
        return Response('Вы отписались', status=status.HTTP_204_NO_CONTENT)
