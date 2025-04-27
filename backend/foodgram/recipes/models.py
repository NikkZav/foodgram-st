from django.db import models
from django.contrib.auth import get_user_model
from utils.gen_utils import generate_unique_urn


User = get_user_model()


class Recipe(models.Model):
    urn = models.SlugField(unique=True, max_length=10,
                           verbose_name="Уникальный идентификатор",
                           blank=True, null=True)
    name = models.CharField(max_length=200, verbose_name="Название")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="recipes", verbose_name="Автор")
    image = models.ImageField(upload_to="recipes/images/",
                              null=True, blank=True, verbose_name="Изображение")
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveSmallIntegerField(verbose_name="Время приготовления (в минутах)")
    ingredients = models.ManyToManyField("Ingredient", through="Component",
                                         verbose_name="Ингредиенты")
    publish_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-publish_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название")
    measurement_unit = models.CharField(max_length=15, verbose_name="Единица измерения")

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Component(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="components",
        verbose_name="Ингредиенты",
    )
    amount = models.PositiveSmallIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"

    def __str__(self):
        return f"{self.ingredient.name} - {self.amount}"


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Рецепты",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_favorite")
        ]
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_cart",
        verbose_name="Рецепты",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
