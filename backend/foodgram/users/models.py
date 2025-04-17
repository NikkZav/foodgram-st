# users/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class FoodgramUser(AbstractUser):
    avatar = models.ImageField('Аватар', upload_to='users/avatars/',
                               null=True, blank=True)
