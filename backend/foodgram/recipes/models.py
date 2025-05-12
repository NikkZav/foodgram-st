from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

User = get_user_model()


class Recipe(models.Model):
    urn = models.SlugField(
        unique=True,
        max_length=10,
        verbose_name="Уникальный идентификатор",
        blank=True,
        null=True,
    )
    name = models.CharField(max_length=256, verbose_name="Название")
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор",
    )
    image = models.ImageField(
        upload_to="recipes/images/",
        null=True,
        blank=True,
        verbose_name="Изображение",
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveBigIntegerField(
        verbose_name="Время готовки (мин)",
        validators=[MinValueValidator(1)],
    )
    ingredients = models.ManyToManyField(
        "Ingredient", through="Component", verbose_name="Ингредиенты"
    )
    publish_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        default_related_name = "recipes"
        ordering = ("-publish_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    measurement_unit = models.CharField(max_length=15, verbose_name="Единица измерения")

    class Meta:
        constraints = [models.UniqueConstraint(fields=["name", "measurement_unit"],
                                               name="unique_ingredient")]
        ordering = ("name",)
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Component(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиенты",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        validators=[MinValueValidator(1)],
    )

    class Meta:
        default_related_name = "components"
        constraints = [models.UniqueConstraint(fields=["recipe", "ingredient"],
                                               name="unique_component")]
        ordering = ("recipe",)
        verbose_name = "Ингредиент для рецепта"
        verbose_name_plural = "Ингредиенты для рецепта"

    def __str__(self):
        return f"{self.ingredient.name} - {self.amount}"


class UserRecipeRelationModel(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепты",
    )

    class Meta:
        abstract = True
        constraints = [models.UniqueConstraint(fields=["user", "recipe"], name="unique_%(class)s")]

    def __str__(self):
        return f"{self.user.username} - {self.recipe.name}"


class Favorite(UserRecipeRelationModel):

    class Meta(UserRecipeRelationModel.Meta):
        default_related_name = "favorites"
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class ShoppingCart(UserRecipeRelationModel):

    class Meta(UserRecipeRelationModel.Meta):
        default_related_name = "shopping_cart"
        verbose_name = "Список покупок"
        verbose_name_plural = "Списки покупок"
