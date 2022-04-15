from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.db import models
from django.forms import ValidationError

from recipes.models import (
    FavouritesItem,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from .users_main import FoodgramUserSerializer


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    amount = serializers.IntegerField(min_value=1)
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    author = FoodgramUserSerializer(
        default=serializers.CurrentUserDefault()
    )
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipeingredient_set'
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    cooking_time = serializers.IntegerField(min_value=1)

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_user(self):
        return self.context['request'].user

    @staticmethod
    def add_ingredients(recipe, ingredients):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient['ingredient']['id'],
                amount=ingredient['amount']
            )

    def create(self, validated_data):
        """ Custom create method to handle nested tags and ingredients. """
        ingredients = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    def update(self, recipe, validated_data):
        """ Custom update method by overwriting tags and ingredients. """
        ingredients = validated_data.pop('recipeingredient_set')
        tags = validated_data.pop('tags')
        recipe.tags.set(tags)
        recipe.recipeingredient_set.all().delete()
        self.add_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def validate(self, attrs):
        if len(attrs['recipeingredient_set']) == 0:
            raise ValidationError('Добавьте ингредиенты.')
        id_ingredients = []
        for ingredient in attrs['recipeingredient_set']:
            if ingredient['amount'] <= 0:
                raise ValidationError(
                    'Укажите количество ингредиента.'
                )
            id_ingredients.append(ingredient['ingredient']['id'])
        if len(id_ingredients) > len(set(id_ingredients)):
            raise ValidationError('Ингредиенты не должны повторяться.')
        if len(attrs['tags']) > len(set(attrs['tags'])):
            raise ValidationError('Теги не должны повторяться.')
        if attrs['cooking_time'] <= 0:
            raise ValidationError('Задайте время приготовления.')
        return attrs

    def to_representation(self, data):
        """ Serializing tags manually. """
        iterable = data.all() if isinstance(data, models.Manager) else data
        tags = TagSerializer(iterable.tags.all(), many=True).data
        rep = super().to_representation(iterable)
        rep['tags'] = tags
        return rep

    def get_is_favorited(self, recipe):
        user = self.get_user()
        if user.is_authenticated:
            try:
                favourites = user.favouritesitem.recipes.all()
                return recipe in favourites
            except FavouritesItem.DoesNotExist:
                return False
        return False

    def get_is_in_shopping_cart(self, recipe):
        user = self.get_user()
        if user.is_authenticated:
            try:
                shopping_cart = user.shoppingcart.recipes.all()
                return recipe in shopping_cart
            except ShoppingCart.DoesNotExist:
                return False
        return False
