from rest_framework import viewsets

from recipes.models import (
    Ingredient, Recipe
)
from .serializers import (
    IngredientSerializer, RecipeSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
