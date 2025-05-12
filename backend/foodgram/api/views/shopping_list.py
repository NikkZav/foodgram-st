from django.http import HttpResponse
from django.db.models import Sum
from recipes.models import Component, Recipe
from datetime import datetime


def get_products(request):
    """Получает список продуктов для списка покупок пользователя."""
    user = request.user
    products = (
        Component.objects.filter(recipe__shopping_cart__user=user)
        .values("ingredient__name", "ingredient__measurement_unit")
        .annotate(amount=Sum("amount"))
        .order_by("ingredient__name")
    )
    return products


def download_shopping_cart_txt(request):
    """Формирует текстовый файл со списком покупок."""
    products = get_products(request)
    recipes = Recipe.objects.filter(shopping_cart__user=request.user).distinct()

    content = '\n'.join([
        f"Список покупок от {datetime.now():%d.%m.%Y (%H:%M)}",
        "",
        "Продукты:",
        *[f"{idx}. {product['ingredient__name'].capitalize()} — "
          f"{product['amount']} {product['ingredient__measurement_unit']}"
          for idx, product in enumerate(products, start=1)],
        "",
        "Рецепты:",
        *[f"- {recipe.name} (автор: {recipe.author.username})" for recipe in recipes],
    ])

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="shopping_cart.txt"'
    return response
