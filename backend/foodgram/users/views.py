from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer
from utils.pagination import LimitPageNumberPagination

from .serializers.base import (
    BaseUserSerializer, AvatarSerializer
)
from .serializers.user import (
    AuthorSerializer, UserCreateSerializer,
    UserWithRecipesSerializer,
)
from .models import Subscription


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        if self.action == 'me':
            return User.objects.filter(id=self.request.user.id)
        if self.action == 'subscriptions':
            return User.objects.filter(following__user=self.request.user)
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
        if self.action == 'subscriptions' or self.action == 'subscribe':
            return UserWithRecipesSerializer
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

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(['post', 'delete'], detail=True)
    def subscribe(self, request, *args, **kwargs):
        user_to_subscribe = self.get_object()
        if request.method == 'POST':
            if user_to_subscribe == request.user:
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'errors': 'Вы не можете подписаться на себя'})
            if Subscription.objects.filter(user=request.user,
                                           subscribed_to=user_to_subscribe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'errors': 'Вы уже подписаны на этого пользователя'})
            Subscription.objects.create(user=request.user, subscribed_to=user_to_subscribe)
            serialize_user_to_subscribe = UserWithRecipesSerializer(user_to_subscribe,
                                                                    context={'request': request})
            return Response(status=status.HTTP_201_CREATED,
                            data=serialize_user_to_subscribe.data)
        elif request.method == 'DELETE':
            if not Subscription.objects.filter(user=request.user,
                                               subscribed_to=user_to_subscribe).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST,
                                data={'errors': 'Вы не подписаны на этого пользователя'})
            Subscription.objects.filter(user=request.user, subscribed_to=user_to_subscribe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
