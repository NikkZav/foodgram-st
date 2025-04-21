from django.urls import path, include
from djoser.views import (
    TokenCreateView, TokenDestroyView
)
from rest_framework.routers import DefaultRouter
from .views import IngredientViewSet, RecipeViewSet
from users.views import CustomUserViewSet


router_v1 = DefaultRouter()
router_v1.register('ingredients', IngredientViewSet)
router_v1.register('recipes', RecipeViewSet)
router_v1.register('users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('', include(router_v1.urls)),

    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path('auth/token/logout/', TokenDestroyView.as_view(), name='logout'),
]
