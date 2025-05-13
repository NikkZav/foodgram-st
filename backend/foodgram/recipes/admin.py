from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from django.db.models import Min, Max
from .models import Component, Ingredient, Recipe


# Inline-класс для компонентов
class ComponentInline(admin.TabularInline):
    model = Component
    extra = 1
    autocomplete_fields = ["ingredient"]


# Кастомный фильтр по времени готовки
class CookingTimeFilter(SimpleListFilter):
    title = "Время готовки"
    parameter_name = "cooking_time"

    def calculate_thresholds(self, queryset):
        """Вычисляет пороговые значения для фильтрации."""
        if not queryset.exists():
            return None, None

        min_time = queryset.aggregate(Min("cooking_time"))["cooking_time__min"]
        max_time = queryset.aggregate(Max("cooking_time"))["cooking_time__max"]

        if min_time == max_time:
            return None, None

        total_recipes = queryset.count()
        ordered_recipes = queryset.order_by("cooking_time")
        fast_threshold = ordered_recipes[total_recipes // 3].cooking_time
        medium_threshold = ordered_recipes[2 * total_recipes // 3].cooking_time
        return fast_threshold, medium_threshold

    def lookups(self, request, model_admin):
        """Возвращает варианты фильтра с количеством рецептов."""
        queryset = model_admin.get_queryset(request)
        self.fast_threshold, self.medium_threshold = self.calculate_thresholds(queryset)

        if self.fast_threshold is None or self.medium_threshold is None:
            return []

        fast_count = queryset.filter(cooking_time__lte=self.fast_threshold).count()
        medium_count = queryset.filter(
            cooking_time__gt=self.fast_threshold,
            cooking_time__lte=self.medium_threshold
        ).count()
        long_count = queryset.filter(cooking_time__gt=self.medium_threshold).count()

        return (
            ("fast", f"Быстрые (до {self.fast_threshold} мин) ({fast_count})"),
            ("medium", f"Средние (до {self.medium_threshold} мин) ({medium_count})"),
            ("long", f"Долгие (более {self.medium_threshold} мин) ({long_count})"),
        )

    def queryset(self, request, queryset):
        """Фильтрует рецепты по времени готовки."""
        if not hasattr(self, 'fast_threshold') or self.fast_threshold is None:
            return queryset

        if self.value() == "fast":
            return queryset.filter(cooking_time__lte=self.fast_threshold)
        if self.value() == "medium":
            return queryset.filter(
                cooking_time__gt=self.fast_threshold,
                cooking_time__lte=self.medium_threshold
            )
        if self.value() == "long":
            return queryset.filter(cooking_time__gt=self.medium_threshold)
        return queryset


# Админ-класс для Recipe
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "image_preview",
        "id",
        "name",
        "cooking_time",
        "author",
        "favorites_count",
        "ingredients_list",
    )
    search_fields = ("name", "author__username")
    list_filter = ("author", CookingTimeFilter)
    inlines = [ComponentInline]

    @admin.display(description="В избранном")
    def favorites_count(self, obj):
        return obj.favorites.count()

    @admin.display(description="Продукты")
    @mark_safe
    def ingredients_list(self, obj):
        ingredients = obj.components.all()
        return "<br>".join(
            f"{c.ingredient.name} ({c.amount} {c.ingredient.measurement_unit})"
            for c in ingredients
        ) if ingredients else "Нет ингредиентов"

    @admin.display(description="Картинка")
    @mark_safe
    def image_preview(self, obj):
        return f'<img src="{obj.image.url}" width="50" height="50" />' if obj.image else ""


# Админ-класс для Ingredient
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit", "recipes_count")
    search_fields = ("name", "measurement_unit")
    list_filter = ("measurement_unit",)

    @admin.display(description="Рецепты")
    def recipes_count(self, obj):
        return obj.components.count()
