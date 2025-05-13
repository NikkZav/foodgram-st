# recipes/serializers.py
from recipes.models import Component, Ingredient, Recipe
from rest_framework import serializers
from api.serializers.users import FoodgramUserSerializer
from ..image import Base64ImageField


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class ComponentSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source="ingredient", queryset=Ingredient.objects.all())
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(source="ingredient.measurement_unit", read_only=True)
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = Component
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeReadOnlySerializer(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""
    id = serializers.IntegerField(read_only=True)
    author = FoodgramUserSerializer(read_only=True)
    ingredients = ComponentSerializer(source="components", many=True, read_only=True)
    image = Base64ImageField(read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )
        read_only_fields = fields

    def get_is_favorited(self, recipe):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return recipe.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, recipe):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return recipe.shopping_carts.filter(user=user).exists()


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для рецептов. Вывод делегируется RecipeReadOnlySerializer."""
    ingredients = ComponentSerializer(source="components", many=True, required=True)
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = (
            "name",
            "image",
            "text",
            "cooking_time",
            "ingredients",
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Нужно указать ингредиенты")
        ingredients_list = [component["ingredient"].id for component in value]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError("Ингредиенты должны быть уникальными")
        return value

    def validate(self, data):
        # Проверяем, что это PATCH-запрос и поле ingredients отсутствует
        if self.context["request"].method == "PATCH" and "components" not in data:
            raise serializers.ValidationError(
                {"ingredients": "Поле ingredients обязательно для обновления"}
            )
        return super().validate(data)

    def create_components(self, recipe, components):
        """Создание компонентов рецепта."""
        Component.objects.bulk_create(
            Component(
                recipe=recipe,
                ingredient=component["ingredient"],
                amount=component["amount"]
            ) for component in components
        )

    def create(self, validated_data):
        # Чтобы не передать components в super().create
        components = validated_data.pop("components")  # Нужен именно pop !
        recipe = super().create(validated_data)
        self.create_components(recipe, components)
        return recipe

    def update(self, recipe, validated_data):
        # Чтобы не передать components в super().update
        components = validated_data.pop("components")  # Нужен именно pop !
        recipe.components.all().delete()
        self.create_components(recipe, components)
        recipe = super().update(recipe, validated_data)
        return recipe

    def to_representation(self, instance):
        """Возвращает данные в формате RecipeReadSerializer."""
        return RecipeReadOnlySerializer(instance, context=self.context).data
