from rest_framework.routers import DefaultRouter
from django.urls import include, path

from api.views import (
    FollowViewSet,
    IngredientsViewSet,
    RecipesViewSet,
    TagsViewSet,
)


router = DefaultRouter()
router.register(r'users', FollowViewSet, basename='following')
router.register(r'tags', TagsViewSet)
router.register(r'ingredients', IngredientsViewSet)
router.register(r'recipes', RecipesViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
