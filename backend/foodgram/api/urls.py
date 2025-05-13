#  backend/foodgram/api/urls.py
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views.recipes import IngredientViewSet, RecipeViewSet
from .views.users import FoodgramUserViewSet


router = DefaultRouter()
router.register("ingredients", IngredientViewSet, basename="ingredients")
router.register("recipes", RecipeViewSet, basename="recipes")
router.register("users", FoodgramUserViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
