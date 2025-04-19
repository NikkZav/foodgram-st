from rest_framework import serializers
from recipes.models import Ingredient, Recipe, Component
from users.serializers import AuthorSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class ComponentSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', read_only=True)
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit', read_only=True)

    class Meta:
        model = Component
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = ComponentSerializer(source='components',
                                      many=True, read_only=True)
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients',
                #   'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text',
                  'cooking_time')
