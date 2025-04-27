from django_filters import (
    FilterSet, TypedChoiceFilter, NumberFilter
)
from rest_framework.filters import SearchFilter
from recipes.models import Recipe


BOOLEAN_PARAMS = {
    'choices': (('1', 'True'), ('0', 'False')),
    'coerce': lambda x: x == '1'
}


class RecipeFilter(FilterSet):
    is_favorited = TypedChoiceFilter(**BOOLEAN_PARAMS,
                                     method='filter_is_favorited')
    is_in_shopping_cart = TypedChoiceFilter(**BOOLEAN_PARAMS,
                                            method='filter_is_in_cart')
    author = NumberFilter(field_name='author')

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author')

    def filter_is_favorited(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_cart(self, queryset, name, value):
        if self.request.user.is_anonymous:
            return queryset.none()
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class NameSearchFilter(SearchFilter):
    search_param = 'name'
