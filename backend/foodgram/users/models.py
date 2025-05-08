# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    email = models.EmailField(
        "Электронная почта", max_length=254, null=False, blank=False, unique=True
    )
    username = models.CharField(
        "Имя пользователя", max_length=150, null=False, blank=False, unique=True
    )
    first_name = models.CharField("Имя", max_length=150, null=False, blank=False)
    last_name = models.CharField("Фамилия", max_length=150, null=False, blank=False)
    avatar = models.ImageField(
        "Аватар", upload_to="users/avatars/", null=True, blank=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]


class Subscription(models.Model):
    user = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
    )
    subscribed_to = models.ForeignKey(
        FoodgramUser,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписан на",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscribed_to"], name="unique_subscription"
            )
        ]
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
