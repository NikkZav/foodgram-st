from django.contrib import admin
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
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

    def lookups(self, request, model_admin):
        recipes = model_admin.get_queryset(request)
        if not recipes.exists():
            return []

        fast_threshold = 15
        medium_threshold = 30

        fast_count = recipes.filter(cooking_time__lte=fast_threshold).count()
        medium_count = recipes.filter(cooking_time__gt=fast_threshold,
                                      cooking_time__lte=medium_threshold).count()
        long_count = recipes.filter(cooking_time__gt=medium_threshold).count()

        return (
            ("fast", f"Быстрые (до {fast_threshold} мин) ({fast_count})"),
            ("medium", f"Средние (до {medium_threshold} мин) ({medium_count})"),
            ("long", f"Долгие (более {medium_threshold} мин) ({long_count})"),
        )

    def queryset(self, request, queryset):
        if self.value() == "fast":
            return queryset.filter(cooking_time__lte=15)
        if self.value() == "medium":
            return queryset.filter(cooking_time__gt=15, cooking_time__lte=30)
        if self.value() == "long":
            return queryset.filter(cooking_time__gt=30)
        return queryset


# Админ-класс для Recipe
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ("urn",)
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

    def favorites_count(self, obj):
        return obj.favorites.count()

    setattr(favorites_count, "short_description", "В избранном")

    @mark_safe
    def ingredients_list(self, obj):
        ingredients = obj.components.all()
        if ingredients:
            return "<br>".join([
                f"{c.ingredient.name} ({c.amount} {c.ingredient.measurement_unit})"
                for c in ingredients
            ])
        return "Нет ингредиентов"
    ingredients_list.short_description = "Продукты"

    @mark_safe
    def image_preview(self, obj):
        if obj.image:
            return f'<img src="{obj.image.url}" width="50" height="50" />'
        return "Нет картинки"
    image_preview.short_description = "Картинка"


# Админ-класс для Ingredient
@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)
