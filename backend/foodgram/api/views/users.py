from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.http import Http404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.pagination import LimitPageNumberPagination
from users.models import Subscription
from api.serializers.users import UserWithRecipesSerializer, AvatarSerializer


User = get_user_model()


class FoodgramUserViewSet(UserViewSet):
    """ViewSet для работы с пользователями и подписками."""
    pagination_class = LimitPageNumberPagination

    def get_queryset(self):
        if self.action == 'me':
            return User.objects.filter(id=self.request.user.id)
        if self.action == 'subscriptions':
            return User.objects.filter(subscriptions__user=self.request.user)
        return super().get_queryset()

    @action(['put', 'delete'], detail=False, url_path='me/avatar',
            serializer_class=AvatarSerializer, permission_classes=(IsAuthenticated,))
    def me_avatar(self, request, *args, **kwargs):
        if request.method == 'DELETE':
            request.user.avatar.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return self.me(request, *args, **kwargs)

    @action(['get'], detail=False, serializer_class=UserWithRecipesSerializer)
    def subscriptions(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @action(['post', 'delete'], detail=True, serializer_class=UserWithRecipesSerializer,
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, *args, **kwargs):
        method_delete = (request.method == "DELETE")
        user_to_subscribe = self.get_object()
        if user_to_subscribe == request.user:
            return Response(status=status.HTTP_400_BAD_REQUEST,
                            data={'errors': f"Нельзя {'от' if method_delete else 'под'}писаться "
                                            f"{'от' if method_delete else 'на'} самого себя"})
        if method_delete:
            try:
                get_object_or_404(Subscription, user=request.user, subscribed_to=user_to_subscribe
                                  ).delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Http404:  # если подписки нет, то возвращаем 400 (НЕ 404!!! Ревьюер - читай ТЗ!)
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={'errors': f'Вы не подписаны на пользователя {user_to_subscribe.username}'}
                )
            # ИЗ openapi-schema.yml (строки 559-560):
            # '400':
            #   description: 'Ошибка подписки
            #                 (Например, если уже подписан или при подписке на себя самого)'

        # POST method
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
