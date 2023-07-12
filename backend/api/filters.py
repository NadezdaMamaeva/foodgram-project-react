from django_filters.rest_framework import FilterSet, filters
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter

from prescripts.models import Component, Recipe, Tag


class ComponentFilter(SearchFilter):
    search_param = 'name'

    class Meta:
        model = Component
        fields = ('name',)


class PrescriptorFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug',
    )
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            raise ValidationError({'error': 'Пользователь неавторизован'})
        if value is not None:
            if value == 1:
                return queryset.filter(favorites__user=user)
            elif value == 0:
                return queryset.exclude(favorites__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not user.is_authenticated:
            raise ValidationError({'error': 'Пользователь неавторизован'})
        if value is not None:
            if value == 1:
                return queryset.filter(cart__user=user)
            elif value == 0:
                return queryset.exclude(cart__user=user)
        return queryset
