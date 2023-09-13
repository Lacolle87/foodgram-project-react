from rest_framework import routers
from django.urls import path, include
from api.views import (
    IngredientViewSet,
    CustomUserViewSet,
    TagViewSet,
    RecipeViewSet
)

router = routers.DefaultRouter()
router.register('users', CustomUserViewSet)
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register(r'ingredients', IngredientViewSet)

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
