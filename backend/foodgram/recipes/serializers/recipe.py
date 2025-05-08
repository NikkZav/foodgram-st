# recipes/serializers.py
from rest_framework import serializers
from recipes.models import Ingredient, Recipe, Component
from users.serializers.user import AuthorSerializer
from utils.serializers import Base64ImageField, set_if_changed


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class ComponentSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source="ingredient", queryset=Ingredient.objects.all()
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )

    def validate_measurement_unit(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Количество ингредиента должно быть больше 0"
            )
        return value

    class Meta:
        model = Component
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    ingredients = ComponentSerializer(source="components", many=True, required=True)
    author = AuthorSerializer(read_only=True)
    image = Base64ImageField(required=True)
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

    def get_is_favorited(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context["request"].user
        if user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=user).exists()

    def validate_cooking_time(self, value):
        if value < 1:
            raise serializers.ValidationError(
                "Время приготовления должно быть больше 0"
            )
        return value

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError("Нужно указать ингредиенты")
        ingredients_list = [
            (component["ingredient"], component["amount"]) for component in value
        ]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise serializers.ValidationError("Ингредиенты должны быть уникальными")
        if any(ingredient["amount"] < 1 for ingredient in value):
            raise serializers.ValidationError(
                "Количество ингредиентов должно быть больше 0"
            )
        return value

    def validate(self, data):
        # Проверяем, что это PATCH-запрос и поле ingredients отсутствует
        if self.context["request"].method == "PATCH" and "components" not in data:
            raise serializers.ValidationError(
                {"ingredients": "Поле ingredients обязательно для обновления"}
            )
        return super().validate(data)

    def create(self, validated_data):
        components = validated_data.pop("components")
        recipe = Recipe.objects.create(**validated_data)

        for component in components:
            Component.objects.create(
                recipe=recipe,
                ingredient=component["ingredient"],
                amount=component["amount"],
            )
        return recipe

    def update(self, instance, validated_data):
        components = validated_data.pop("components", None)

        is_modified = False
        for attr, value in validated_data.items():
            is_modified |= set_if_changed(instance, attr, value)
        if is_modified:
            instance.save()

        if components is not None:
            # Подготовим удобную структуру из новых компонентов
            new_components_map = {
                comp["ingredient"].id: comp["amount"] for comp in components
            }
            # Текущие компоненты из базы
            current_components = {c.ingredient.id: c for c in instance.components.all()}
            # Обновим и добавим новые
            for ingr_id, new_amount in new_components_map.items():
                if ingr_id in current_components:  # Уже есть в базе
                    comp = current_components[ingr_id]
                    if comp.amount != new_amount:  # Изменилось количество
                        comp.amount = new_amount
                        comp.save()
                else:  # Новый ингредиент
                    Component.objects.create(
                        recipe=instance, ingredient_id=ingr_id, amount=new_amount
                    )
            # Удалим те, которых больше нет
            for ingr_id in current_components:
                if ingr_id not in new_components_map:
                    current_components[ingr_id].delete()

        return instance
