import django_filters.rest_framework as df
from django.db.models import IntegerField, Value

from recipes.models import FavouritesItem, Ingredient, Recipe, ShoppingCart


class IngredientSearchFilter(df.FilterSet):
    name = df.CharFilter(method='search_by_name')

    class Meta:
        model = Ingredient
        fields = ('name',)

    def search_by_name(self, queryset, name, value):
        if not value:
            return queryset
        start_with_queryset = (
            queryset.filter(name__istartswith=value).annotate(
                order=Value(0, IntegerField())
            )
        )
        contain_queryset = (
            queryset.filter(name__icontains=value).exclude(
                pk__in=start_with_queryset.values_list('pk')
            ).annotate(
                order=Value(1, IntegerField())
            )
        )
        return start_with_queryset.union(contain_queryset).order_by('order')


class RecipeFilter(df.FilterSet):
    is_favorited = df.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = df.BooleanFilter(method='get_is_in_shopping_cart')
    tags = df.AllValuesMultipleFilter(field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ('author',)

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if not value or not user.is_authenticated:
            return queryset
        try:
            favorite_recipes = user.favouritesitem.recipes.all()
        except FavouritesItem.DoesNotExist:
            return Recipe.objects.none()
        return queryset.filter(
            pk__in=favorite_recipes.values_list('pk')
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if not value or not user.is_authenticated:
            return queryset
        try:
            shopping_cart = user.shoppingcart.recipes.all()
        except ShoppingCart.DoesNotExist:
            return Recipe.objects.none()
        return queryset.filter(
            pk__in=shopping_cart.values_list('pk')
        )
