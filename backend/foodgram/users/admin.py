from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import FoodgramUser, Subscription
from recipes.models import ShoppingCart, Favorite


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


class FoodgramUserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "first_name", "last_name")
    search_fields = ("username", "email")
    list_filter = ("username", "email")
    inlines = [ShoppingCartAdmin, FavoriteAdmin, SubscriptionAdmin]

    fieldsets = BaseUserAdmin.fieldsets + (("Дополнительно", {"fields": ("avatar",)}),)


admin.site.register(FoodgramUser, FoodgramUserAdmin)
