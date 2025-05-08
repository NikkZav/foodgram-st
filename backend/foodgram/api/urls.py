#  backend/foodgram/api/urls.py
from django.urls import include, path
from djoser.views import TokenCreateView, TokenDestroyView
from recipes.views import IngredientViewSet, RecipeViewSet
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet

router_v1 = DefaultRouter()
router_v1.register("ingredients", IngredientViewSet, basename="ingredients")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register("users", CustomUserViewSet, basename="users")

urlpatterns = [
    path("", include(router_v1.urls)),
    path("auth/token/login/", TokenCreateView.as_view(), name="login"),
    path("auth/token/logout/", TokenDestroyView.as_view(), name="logout"),
]
