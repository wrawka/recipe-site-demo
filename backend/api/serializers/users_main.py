from djoser.serializers import UserCreateSerializer
from rest_framework.serializers import (
    EmailField,
    ModelSerializer,
    SerializerMethodField,
)
from rest_framework.validators import UniqueValidator

from .recipes_misc import Recipe, RecipeLiteSerializer
from users.models import Follow, User


class FoodgramUserCreateSerializer(UserCreateSerializer):
    email = EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message='Пользователь с таким email уже зарегистрирован.'
            )
        ],
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'password', 'first_name', 'last_name'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }


class FoodgramUserSerializer(ModelSerializer):
    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        result = False
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
            result = user.is_authenticated
        if result:
            result = Follow.objects.filter(user=user, author=author).exists()
        return result # noqa


class SubscriptionUserSerializer(FoodgramUserSerializer):
    recipes = SerializerMethodField()
    recipes_count = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_recipes(self, user):
        queryset = Recipe.objects.filter(author=user)
        limit = queryset.count()
        request = self.context.get('request')
        if request:
            limit = int(request.query_params.get('recipes_limit', limit))
        return RecipeLiteSerializer(queryset[:limit], many=True).data
