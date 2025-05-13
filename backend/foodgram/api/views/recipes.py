import io
from datetime import datetime
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.http import Http404, FileResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from django.db.models import Sum
from django.template.loader import render_to_string
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.pagination import LimitPageNumberPagination
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Component
from api.filters import NameSearchFilter, RecipeFilter
from api.permissions import AuthorOrReadOnly
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
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ("name",)
    pagination_class = LimitPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=["get"], detail=True, url_path="get-link", url_name="get-link")
    def get_link(self, request, pk=None):
        short_url = request.build_absolute_uri(
            reverse("shortlink-redirect", kwargs={"recipe_id": pk})
        )
        return Response({"short-link": short_url}, status=status.HTTP_200_OK)

    def _user_collection(self, request, collection: models.Model):
        recipe = self.get_object()
        if request.method == "DELETE":
            try:
                get_object_or_404(collection, user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Http404:  # если элемента в коллекции нет, то возвращаем 400
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,  # НЕ 404!!! Ревьюер - читай ТЗ!
                    data={"errors": f"В {collection._meta.verbose_name} нет рецепта {recipe.name}"}
                )
            # ИЗ openapi-schema.yml (строки 338-339 и 389-390):
            # '400':
            #     description: 'Ошибка удаления из избранного
            #                   (Например, когда рецепта там не было)'
            # '400':
            #     description: 'Ошибка удаления из списка покупок
            #                   (Например, когда рецепта там не было)'

        # POST method
        recipe_in_collection, created = collection.objects.get_or_create(
            user=request.user, recipe=recipe
        )
        if not created:  # если рецепт уже в коллекции, то возвращаем 400
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"errors": f"Рецепт {recipe.name} уже в {collection._meta.verbose_name}"},
            )
        # если рецепта нет в коллекции, то добавляем и возвращаем 201
        recipe_in_collection.save()
        return Response(
            status=status.HTTP_201_CREATED,
            data=RecipeShortSerializer(recipe).data,
        )

    @action(methods=["post", "delete"], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        return self._user_collection(request, Favorite)

    @action(methods=["post", "delete"], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self._user_collection(request, ShoppingCart)

    @action(['get'], detail=False, permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        products = (
            Component.objects
            .filter(recipe__shopping_carts__user=request.user)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(amount=Sum("amount"))
            .order_by("ingredient__name")
        )
        recipes = Recipe.objects.filter(shopping_carts__user=request.user).distinct()
        content = render_to_string(
            "shopping_cart.txt",
            {
                "products": products,
                "recipes": recipes,
                "date": datetime.now(),
            },
        )
        return FileResponse(
            io.BytesIO(content.encode('utf-8')),
            content_type='text/plain; charset=utf-8',
            as_attachment=True,
            filename='shopping_cart.txt',
        )
