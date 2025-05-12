from django_filters import FilterSet, NumberFilter, TypedChoiceFilter
from recipes.models import Recipe
from rest_framework.filters import SearchFilter

BOOLEAN_PARAMS = {
    "choices": (("1", "True"), ("0", "False")),
    "coerce": lambda x: x == "1",
}


class RecipeFilter(FilterSet):
    is_favorited = TypedChoiceFilter(**BOOLEAN_PARAMS, method="filter_is_favorited")
    is_in_shopping_cart = TypedChoiceFilter(**BOOLEAN_PARAMS, method="filter_is_in_cart")
    author = NumberFilter(field_name="author")

    class Meta:
        model = Recipe
        fields = ("is_favorited", "is_in_shopping_cart", "author")

    def filter_is_favorited(self, recipes, name, value):
        if self.request.user.is_anonymous:
            return recipes.none()
        if value:
            return recipes.filter(favorites__user=self.request.user)
        return recipes

    def filter_is_in_cart(self, recipes, name, value):
        if self.request.user.is_anonymous:
            return recipes.none()
        if value:
            return recipes.filter(shopping_cart__user=self.request.user)
        return recipes


class NameSearchFilter(SearchFilter):
    search_param = "name"
