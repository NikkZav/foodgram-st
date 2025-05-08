from django.contrib import admin

from .models import Component, Ingredient, Recipe


class ComponentInline(admin.TabularInline):  # или admin.StackedInline
    model = Component
    extra = 1  # сколько пустых форм отобразить
    autocomplete_fields = ["ingredient"]  # удобно, если ингредиентов много


class RecipeAdmin(admin.ModelAdmin):
    readonly_fields = ("urn",)
    list_display = ("name", "author")
    search_fields = ("name", "author__username")
    list_filter = ("author",)
    inlines = [ComponentInline]  # 👈 вот тут добавляется возможность


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
