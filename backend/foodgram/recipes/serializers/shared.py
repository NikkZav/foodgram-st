# recipes/serializers.py
from recipes.models import Recipe
from rest_framework import serializers
from utils.serializers import Base64ImageField


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")
