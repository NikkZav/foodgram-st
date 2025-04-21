import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer

from .serializers import (
    AuthorSerializer, UserCreateSerializer, BaseUserSerializer,
    AvatarSerializer
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
        if self.action == 'me_avatar':
            return AvatarSerializer
        return BaseUserSerializer

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            # GET+POST /api/users/ и GET /api/users/{id}/ — доступны всем
            return (AllowAny(),)
        # остальные — только для авторизованных
        return (IsAuthenticated(),)

    @action(['put', 'delete'], detail=False, url_path='me/avatar')
    def me_avatar(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return self.me(request, *args, **kwargs)
