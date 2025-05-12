#  backend/foodgram/api/urls.py
from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from .views.recipes import IngredientViewSet, RecipeViewSet
from rest_framework.routers import DefaultRouter
from .views.users import FoodgramUserViewSet

router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("users", FoodgramUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", TokenCreateView.as_view(), name="login"),
    path("auth/token/logout/", TokenDestroyView.as_view(), name="logout"),
]
