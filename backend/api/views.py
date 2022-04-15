from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
)
from rest_framework.viewsets import (
    GenericViewSet,
    ModelViewSet,
    ReadOnlyModelViewSet,
)
from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from recipes.models import (
    FavouritesItem,
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
)
from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import FoodgramPagination
from .serializers.recipes_main import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)
from .serializers.recipes_misc import RecipeLiteSerializer
from .serializers.users_main import SubscriptionUserSerializer
from users.models import Follow, User


class FollowViewSet(GenericViewSet):
    serializer_class = SubscriptionUserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['author__username', 'user__username']
    pagination_class = FoodgramPagination

    @action(detail=False)
    def subscriptions(self, request):
        following = User.objects.filter(followers__user=request.user)
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = SubscriptionUserSerializer(
                page, context={'request': request}, many=True
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionUserSerializer(
            following, context={'request': request}, many=True
        )
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        if author == request.user:
            return Response(
                {'errors': 'Can\'t follow self.'},
                status=HTTP_400_BAD_REQUEST
            )
        try:
            Follow.objects.create(user=request.user, author=author)
        except IntegrityError:
            return Response(
                {'errors': 'Already subscribed to this user.'},
                status=HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(author)
        return Response(serializer.data, status=HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        try:
            Follow.objects.get(
                user=request.user.id,
                author=author.id
            ).delete()
        except Follow.DoesNotExist:
            return Response(
                {'errors': 'Not following this author.'},
                status=HTTP_400_BAD_REQUEST
            )
        return Response(status=HTTP_204_NO_CONTENT)


class TagsViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientSearchFilter


class RecipesViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = FoodgramPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    COLLECTIONS = {
        'shopping_cart': (ShoppingCart, 'shopping cart'),
        'remove_from_shopping_cart': (ShoppingCart, 'shopping cart'),
        'favorite': (FavouritesItem, 'favourites'),
        'remove_from_favourites': (FavouritesItem, 'favourites')
    }

    def add_recipe(self, request, pk=None):
        """ Validates the recipe vs. collection & adds if doesn't exist. """
        model_type, name = self.COLLECTIONS.get(self.action)
        recipe = get_object_or_404(Recipe, id=pk)
        collection, _ = model_type.objects.get_or_create(user=request.user)
        if collection.recipes.filter(id__exact=recipe.id).exists():
            return Response(
                {'errors': f'Already in the {name}.'},
                status=HTTP_400_BAD_REQUEST
            )
        collection.recipes.add(recipe)
        return recipe

    def remove_recipe(self, request, pk=None) -> None:
        """Validates the recipe vs. collection & removes if present."""

        model_type, name = self.COLLECTIONS.get(self.action)
        recipe = get_object_or_404(Recipe, id=pk)
        collection, _ = model_type.objects.get_or_create(user=request.user)
        if not collection.recipes.filter(id__exact=recipe.id).exists():
            return Response(
                {'errors': f'Not in {name}.'},
                status=HTTP_400_BAD_REQUEST
            )
        collection.recipes.remove(recipe)
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=True, name="Add to shopping cart", methods=['POST'])
    def shopping_cart(self, request, pk=None):
        """Adds a recipe to the shopping cart."""

        recipe = self.add_recipe(request, pk=pk)
        return Response(RecipeLiteSerializer(recipe).data)

    @shopping_cart.mapping.delete
    def remove_from_shopping_cart(self, request, pk=None):
        """Removes a recipe from the shopping cart."""

        return self.remove_recipe(request, pk=pk)

    @action(detail=True, name="Add to favourites", methods=['POST'])
    def favorite(self, request, pk=None):
        """Adds a recipe to favourites."""

        recipe = self.add_recipe(request, pk=pk)
        return Response(RecipeLiteSerializer(recipe).data)

    @favorite.mapping.delete
    def remove_from_favourites(self, request, pk=None):
        """Removes a recipe from favourites."""

        self.remove_recipe(request, pk=pk)
        return Response(status=HTTP_204_NO_CONTENT)

    @action(detail=False)
    def download_shopping_cart(self, request):
        """Returns the shopping cart aggregated contents as a file."""

        recipes = (
            request.user.shoppingcart.recipes.prefetch_related('ingredients')
        )
        ingredients = (
            recipes.order_by('ingredients__name')
            .values('ingredients__name', 'ingredients__measurement_unit')
            .annotate(total=Sum('recipeingredient__amount'))
        )
        ingredients_list = ''
        for ingredient in ingredients:
            ingredients_list += (
                f'{ingredient.get("ingredients__name")}'
                f' — {ingredient.get("total")}'
                f' {ingredient.get("ingredients__measurement_unit")}.\r\n'
            )
        response = HttpResponse(
            ingredients_list, content_type='text/plain,charset=utf8'
        )
        response['Content-Disposition'] = (
            f'attachment; filename={"shopping_list.txt"}'
        )
        return response
