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


# Кастомные фильтры
class HasRecipesFilter(SimpleListFilter):
    title = "Есть рецепты"
    parameter_name = "has_recipes"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Да"),
            ("no", "Нет"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(recipes__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(recipes__isnull=True)


class HasSubscriptionsFilter(SimpleListFilter):
    title = "Есть подписки"
    parameter_name = "has_subscriptions"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Да"),
            ("no", "Нет"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(subscriptions__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(subscriptions__isnull=True)


class HasFollowersFilter(SimpleListFilter):
    title = "Есть подписчики"
    parameter_name = "has_followers"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Да"),
            ("no", "Нет"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(followers__isnull=False).distinct()
        if self.value() == "no":
            return queryset.filter(followers__isnull=True)


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

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @mark_safe
    def avatar_image(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" width="50" height="50" />'
        return "Нет аватара"

    def recipes_count(self, obj):
        return obj.recipes.count()

    def subscriptions_count(self, obj):
        return obj.subscriptions.count()

    def followers_count(self, obj):
        return obj.followers.count()

    setattr(full_name, "short_description", "ФИО")
    setattr(avatar_image, "short_description", "Аватар")
    setattr(recipes_count, "short_description", "Рецепты")
    setattr(subscriptions_count, "short_description", "Подписки")
    setattr(followers_count, "short_description", "Подписчики")
