# users/serializers.py
from django.contrib.auth import get_user_model
from recipes.serializers.shared import RecipeShortSerializer
from rest_framework import serializers
from users.models import Subscription
from users.serializers.base import BaseUserSerializer, UserWithAvatarSerializer

User = get_user_model()


class AuthorSerializer(UserWithAvatarSerializer):
    id = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserWithAvatarSerializer.Meta):
        fields = UserWithAvatarSerializer.Meta.fields + ("id", "is_subscribed")

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(user=request.user, subscribed_to=obj).exists()


class UserCreateSerializer(BaseUserSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ("id", "password")

    def create(self, validated_data):
        # обязательно используем set_password
        password = validated_data.pop("password")
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class UserWithRecipesSerializer(AuthorSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ("recipes", "recipes_count")

    def get_recipes_count(self, obj):
        return obj.recipes.count()

    def get_recipes(self, obj):
        recipes_limit = self.context.get("request").query_params.get("recipes_limit")
        if recipes_limit is not None and recipes_limit.isdigit():
            return RecipeShortSerializer(obj.recipes.all()[: int(recipes_limit)], many=True).data
        return RecipeShortSerializer(obj.recipes.all(), many=True).data
