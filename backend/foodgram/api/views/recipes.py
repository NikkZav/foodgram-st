from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .gen_utils import generate_unique_urn
from api.pagination import LimitPageNumberPagination
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart
from api.views.shopping_list import download_shopping_cart_txt
from api.filters import NameSearchFilter, RecipeFilter
from api.permissions import UserPermission
from api.serializers.recipes.recipe import IngredientSerializer, RecipeSerializer
from api.serializers.recipes.shared import RecipeShortSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (
        DjangoFilterBackend,
        NameSearchFilter,
        filters.OrderingFilter,
    )
    search_fields = ("^name",)
    ordering = ("id",)
    pagination_class = None  # Отключаем пагинацию для ингредиентов


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-publish_date")
    serializer_class = RecipeSerializer
    permission_classes = (UserPermission,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ("name",)
    pagination_class = LimitPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["get"], detail=True, url_path="get-link", url_name="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        if not recipe.urn:  # если у рецепта нет urn, то генерируем и сохраняем его
            recipe.urn = generate_unique_urn(recipe)
            recipe.save(update_fields=["urn"])
        short_url = request.build_absolute_uri(f"/s/{recipe.urn}/")
        return Response({"short-link": short_url}, status=status.HTTP_200_OK)

    def _user_collection(self, request, collection: models.Model):
        recipe = self.get_object()
        if request.method == "POST":
            recipe_in_collection, created = collection.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:  # если рецепта нет в коллекции, то добавляем и возвращаем 201
                recipe_in_collection.save()
                return Response(
                    status=status.HTTP_201_CREATED,
                    data=RecipeShortSerializer(recipe).data,
                )
            # если рецепт уже в коллекции, то возвращаем 400
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": "Рецепт уже в избранном"},
            )
        # метод DELETE
        if not collection.objects.filter(user=request.user, recipe=recipe).exists():
            # если элемента в коллекции нет, то возвращаем 400 (НЕ 404!!! по ТЗ!)
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={"errors": f"В избранном нет рецепта {recipe.name}"})
        get_object_or_404(collection, user=request.user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=["post", "delete"], detail=True)
    def favorite(self, request, pk=None):
        return self._user_collection(request, Favorite)

    @action(methods=["post", "delete"], detail=True)
    def shopping_cart(self, request, pk=None):
        return self._user_collection(request, ShoppingCart)

    @action(methods=["get"], detail=False)
    def download_shopping_cart(self, request, pk=None):
        return download_shopping_cart_txt(request)


def redirect_to_recipe(request, urn):
    recipe = get_object_or_404(Recipe, urn=urn)
    return redirect(f"/recipes/{recipe.pk}/")
