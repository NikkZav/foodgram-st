# users/serializers.py
import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from utils.serializers import Base64ImageField

User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields: tuple[str, ...] = ("avatar",)


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: tuple[str, ...] = (
            "email",
            "username",
            "first_name",
            "last_name",
        )

    def validate_username(self, value):
        if re.match(r"^[\w.@+-]+\Z", value) is None:
            raise serializers.ValidationError("Имя пользователя содержит недопустимые символы")
        return value


class UserWithAvatarSerializer(BaseUserSerializer, AvatarSerializer):
    class Meta(BaseUserSerializer.Meta, AvatarSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + AvatarSerializer.Meta.fields
