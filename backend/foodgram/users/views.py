from rest_framework import viewsets
from users.models import FoodgramUser
from .serializers import (
    AuthorSerializer, UserCreateSerializer, BaseUserSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = FoodgramUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('list', 'retrieve'):
            return AuthorSerializer
        return BaseUserSerializer
