from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer

from .serializers import (
    AuthorSerializer, UserCreateSerializer, BaseUserSerializer
)


User = get_user_model()


class CustomUserViewSet(UserViewSet):

    def get_queryset(self):
        return User.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action in ('list', 'retrieve', 'me'):
            return AuthorSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return BaseUserSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            # GET+POST /api/users/ и GET /api/users/{id}/ — доступны всем
            return (AllowAny(),)
        # остальные — только для авторизованных
        return (IsAuthenticated(),)
