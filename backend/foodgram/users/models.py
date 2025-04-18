# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    avatar = models.ImageField('Аватар', upload_to='users/avatars/',
                               null=True, blank=True)


class Subscription(models.Model):
    user = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Пользователь')
    subscribed_to = models.ForeignKey(FoodgramUser, on_delete=models.CASCADE,
                                      related_name='following',
                                      verbose_name='Подписан на')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'subscribed_to'],
                                    name='unique_subscription')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
