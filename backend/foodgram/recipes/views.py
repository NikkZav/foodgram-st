from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from shopping_list.views import download_shopping_cart_pdf
from utils.gen_utils import generate_unique_urn
from utils.pagination import LimitPageNumberPagination

from .filters import NameSearchFilter, RecipeFilter
from .models import Favorite, Ingredient, Recipe, ShoppingCart
from .permissions import IsAuthor
from .serializers.recipe import IngredientSerializer, RecipeSerializer
from .serializers.shared import RecipeShortSerializer


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
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ("name",)
    pagination_class = LimitPageNumberPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_permissions(self):
        if self.action in ("list", "retrieve", "get_link"):
            # GET+POST /api/users/ и GET /api/users/{id}/ — доступны всем
            return (AllowAny(),)
        if self.action in ("update", "partial_update", "destroy"):
            # PATCH /api/users/{id}/ и DELETE /api/users/{id}/ — только для автора
            return (IsAuthor(),)
        # остальные — только для авторизованных
        return (IsAuthenticated(),)

    @action(methods=["get"], detail=True, url_path="get-link", url_name="get-link")
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        if not recipe.urn:  # если у рецепта нет urn, то генерируем и сохраняем его
            recipe.urn = generate_unique_urn(recipe)
            recipe.save(update_fields=["urn"])
        short_url = request.build_absolute_uri(f"/s/{recipe.urn}/")
        return Response({"short-link": short_url}, status=status.HTTP_200_OK)

    @action(methods=["post", "delete"], detail=True)
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        if request.method == "POST":
            recipe_in_favorite, created = Favorite.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:  # если рецепта нет в избранном, то добавляем и возвращаем 201
                recipe_in_favorite.save()
                return Response(
                    status=status.HTTP_201_CREATED,
                    data=RecipeShortSerializer(recipe).data,
                )
            else:  # если рецепт уже в избранном, то возвращаем 400
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"errors": "Рецепт уже в избранном"},
                )
        elif request.method == "DELETE":
            if Favorite.objects.filter(user=request.user, recipe=recipe).exists():
                Favorite.objects.filter(user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:  # если рецепта нет в избранном, то возвращаем 400
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"errors": "Рецепта нет в избранном"},
                )

    @action(methods=["post", "delete"], detail=True)
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        if request.method == "POST":
            recipe_in_cart, created = ShoppingCart.objects.get_or_create(
                user=request.user, recipe=recipe
            )
            if created:  # если рецепта нет в корзине, то добавляем и возвращаем 201
                recipe_in_cart.save()
                return Response(
                    status=status.HTTP_201_CREATED,
                    data=RecipeShortSerializer(recipe).data,
                )
            else:  # если рецепт уже в корзине, то возвращаем 400
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"errors": "Рецепт уже в корзине"},
                )
        elif request.method == "DELETE":
            if ShoppingCart.objects.filter(user=request.user, recipe=recipe).exists():
                ShoppingCart.objects.filter(user=request.user, recipe=recipe).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:  # если рецепта нет в корзине, то возвращаем 400
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={"errors": "Рецепта нет в корзине"},
                )

    @action(methods=["get"], detail=False)
    def download_shopping_cart(self, request, pk=None):
        return download_shopping_cart_pdf(request)


def redirect_to_recipe(request, urn):
    recipe = get_object_or_404(Recipe, urn=urn)
    return redirect(f"/recipes/{recipe.pk}/")
