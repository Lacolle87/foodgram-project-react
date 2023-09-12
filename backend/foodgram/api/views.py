from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet

from recipes.models import Tag
from api.serializer import TagSerializer


def index(request):
    return HttpResponse('index')

class CustomUserViewSet(UserViewSet):
    pass

class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
