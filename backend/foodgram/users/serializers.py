from rest_framework import serializers
from django.contrib.auth import get_user_model
from users.models import Subscription

User = get_user_model()


class BaseUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields: tuple[str, ...] = ('email', 'username',
                                   'first_name', 'last_name', 'avatar')


class AuthorSerializer(BaseUserSerializer):
    id = serializers.IntegerField(read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('id', 'is_subscribed')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, subscribed_to=obj
        ).exists()


class UserCreateSerializer(BaseUserSerializer):
    id = serializers.IntegerField(read_only=True)
    password = serializers.CharField(write_only=True)

    class Meta(BaseUserSerializer.Meta):
        fields = BaseUserSerializer.Meta.fields + ('id', 'password')

    def create(self, validated_data):
        # обязательно используем set_password
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user
