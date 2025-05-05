# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

from utils.serializers import Base64ImageField


User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields: tuple[str, ...] = ('avatar',)


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields: tuple[str, ...] = ('email', 'username',
                                   'first_name', 'last_name')


class UserWithAvatarSerializer(BaseUserSerializer, AvatarSerializer):
    class Meta(BaseUserSerializer.Meta, AvatarSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + AvatarSerializer.Meta.fields
