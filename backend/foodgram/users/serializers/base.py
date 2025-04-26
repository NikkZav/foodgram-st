# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model

from utils.serializers import Base64ImageField


User = get_user_model()


class AvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = User
        fields = ('avatar',)


class BaseUserSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields: tuple[str, ...] = ('email', 'username',
                                   'first_name', 'last_name', 'avatar')
