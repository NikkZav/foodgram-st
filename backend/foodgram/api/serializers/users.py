from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer
from rest_framework import serializers
from .recipes.shared import RecipeShortSerializer
from users.models import Subscription
from .image import Base64ImageField

User = get_user_model()


RECIPES_LIMIT = 10**10


class FoodgramUserSerializer(UserSerializer):
    """Сериализатор для пользователей с аватаром и подписками."""
    avatar = Base64ImageField(required=False, allow_null=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields: tuple[str, ...] = ('id', 'email', 'username',
                                   'first_name', 'last_name',
                                   'avatar', 'is_subscribed')

    def get_is_subscribed(self, user):
        """Проверяет, подписан ли текущий пользователь на данного пользователя."""
        request = self.context.get('request')
        return (
            request
            and request.user.is_authenticated
            and Subscription.objects.filter(user=request.user, subscribed_to=user).exists()
        )


class UserWithRecipesSerializer(FoodgramUserSerializer):
    """Сериализатор для пользователей с рецептами."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source='recipes.count', read_only=True)

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes(self, user):
        """Возвращает список рецептов с учётом параметра recipes_limit."""
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit', RECIPES_LIMIT)
        try:
            limit = int(recipes_limit)
        except ValueError:
            limit = RECIPES_LIMIT
        return RecipeShortSerializer(user.recipes.all()[:limit], many=True).data


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для управления аватаром."""
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)
