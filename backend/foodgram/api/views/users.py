from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from api.pagination import LimitPageNumberPagination
from users.models import Subscription
from api.serializers.users import UserWithRecipesSerializer, AvatarSerializer
from api.permissions import UserPermission


User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """ViewSet для работы с пользователями и подписками."""
    pagination_class = LimitPageNumberPagination
    permission_classes = (UserPermission,)

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            # GET+POST /api/users/ и GET /api/users/{id}/ — доступны всем
            return (AllowAny(),)
        # остальные — только для авторизованных
        return (IsAuthenticated(),)

    def get_queryset(self):
        if self.action == 'me':
            return User.objects.filter(id=self.request.user.id)
        if self.action == 'subscriptions':
            return User.objects.filter(subscriptions__user=self.request.user)
        return User.objects.all()

    @action(['put', 'delete'], detail=False, url_path='me/avatar',
            serializer_class=AvatarSerializer)
    def me_avatar(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        print(self.serializer_class)
        return self.me(request, *args, **kwargs)

    @action(['get'], detail=False, serializer_class=UserWithRecipesSerializer)
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(['post', 'delete'], detail=True, serializer_class=UserWithRecipesSerializer)
    def subscribe(self, request, *args, **kwargs):
        user_to_subscribe = self.get_object()
        if request.method == 'POST':
            if user_to_subscribe == request.user:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'errors': 'Нельзя подписаться на самого себя'},
                )
            subscription, created = Subscription.objects.get_or_create(
                user=request.user,
                subscribed_to=user_to_subscribe
            )
            if not created:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'errors': f'Вы уже подписаны на пользователя {user_to_subscribe.username}'
                    },
                )
            serializer = UserWithRecipesSerializer(user_to_subscribe, context={'request': request})
            return Response(status=status.HTTP_201_CREATED, data=serializer.data)
        # DELETE method
        if not Subscription.objects.filter(user=request.user,
                                           subscribed_to=user_to_subscribe).exists():
            # если подписки нет, то возвращаем 400 (НЕ 404!!! по ТЗ!)
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'errors': 'Вы не подписаны на этого пользователя'})
        get_object_or_404(
            Subscription,
            user=request.user,
            subscribed_to=user_to_subscribe
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
