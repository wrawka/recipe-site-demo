from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    """ Tag to specialize recipe. """
    name = models.CharField(
        max_length=200, unique=True, verbose_name='Название'
    )
    color = models.CharField(max_length=7, unique=True, verbose_name='Цвет')
    slug = models.SlugField(unique=True, verbose_name='Обозначение')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Ingredient(models.Model):
    """ Ingredient to put in the recipe. """
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes', null=True,
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(Tag, verbose_name='Теги')
    name = models.CharField(max_length=200, verbose_name='Название')
    image = models.ImageField(verbose_name='Изображение')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления',
        validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-id']

    def __str__(self) -> str:
        return self.name


class RecipeIngredient(models.Model):
    """ Representation of ingredient in the recipe (with amount). """
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.DO_NOTHING, verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество', validators=[MinValueValidator(1)]
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецептов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='ingredient_unique_in_recipe'
            ),
        ]

    def __str__(self) -> str:
        return (f'{self.ingredient.name} - {self.amount}'
                f'{self.ingredient.measurement_unit}')


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipes = models.ManyToManyField(
        Recipe, verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='shopping_cart_unique_for_user'
            ),
        ]


class FavouritesItem(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name='Пользователь'
    )
    recipes = models.ManyToManyField(Recipe, verbose_name='Рецепт')

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                name='favourites_unique_for_user'
            ),
        ]
