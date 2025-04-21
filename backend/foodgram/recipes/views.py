from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from .filters import RecipeFilter

from .models import (
    Ingredient, Recipe
)
from .serializers import (
    IngredientSerializer, RecipeSerializer
)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    search_fields = ('name',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
