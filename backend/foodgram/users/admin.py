from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.contrib.admin import SimpleListFilter
from recipes.models import Favorite, ShoppingCart
from .models import FoodgramUser, Subscription


# Inline-классы для связанных моделей
class ShoppingCartAdmin(admin.TabularInline):
    model = ShoppingCart
    extra = 1
    autocomplete_fields = ["recipe"]


class FavoriteAdmin(admin.TabularInline):
    model = Favorite
    extra = 1
    autocomplete_fields = ["recipe"]


class SubscriptionAdmin(admin.TabularInline):
    model = Subscription
    fk_name = "user"
    extra = 1


# Базовый класс для фильтров
class BaseRelationFilter(SimpleListFilter):
    relation_field = None  # Задаётся в наследниках
    LOOKUP_CHOICES = (
        ("yes", "Да"),
        ("no", "Нет"),
    )

    def lookups(self, request, model_admin):
        return self.LOOKUP_CHOICES

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(**{f"{self.relation_field}__isnull": False}).distinct()
        if self.value() == "no":
            return queryset.filter(**{f"{self.relation_field}__isnull": True})
        return queryset


# Кастомные фильтры
class HasRecipesFilter(BaseRelationFilter):
    title = "Есть рецепты"
    parameter_name = "has_recipes"
    relation_field = "recipes"


class HasSubscriptionsFilter(BaseRelationFilter):
    title = "Есть подписки"
    parameter_name = "has_subscriptions"
    relation_field = "subscriptions"


class HasFollowersFilter(BaseRelationFilter):
    title = "Есть подписчики"
    parameter_name = "has_followers"
    relation_field = "authors"


# Регистрация админ-класса через декоратор
@admin.register(FoodgramUser)
class FoodgramUserAdmin(BaseUserAdmin):
    list_display = (
        "avatar_image",
        "id",
        "username",
        "full_name",
        "email",
        "recipes_count",
        "subscriptions_count",
        "followers_count",
    )
    search_fields = ("username", "email")
    list_filter = (HasRecipesFilter, HasSubscriptionsFilter, HasFollowersFilter)
    inlines = [ShoppingCartAdmin, FavoriteAdmin, SubscriptionAdmin]
    fieldsets = BaseUserAdmin.fieldsets + (("Дополнительно", {"fields": ("avatar",)}),)

    @admin.display(description="ФИО")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.display(description="Аватар")
    @mark_safe
    def avatar_image(self, obj):
        return f'<img src="{obj.avatar.url}" width="50" height="50" />' if obj.avatar else ""

    @admin.display(description="Рецепты")
    def recipes_count(self, obj):
        return obj.recipes.count()

    @admin.display(description="Подписки")
    def subscriptions_count(self, obj):
        return obj.subscriptions.count()

    @admin.display(description="Подписчики")
    def followers_count(self, obj):
        return obj.authors.count()
