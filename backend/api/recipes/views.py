from django.db.models import Exists
from django.http.response import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from foodgram.pagination import CustomPagination
from foodgram.permissions import IsAdminOrReadOnly
from recipes.models import (Component, ComponentUnit, Favorite, Recipe,
                            ShoppingCart, Tag,)

from api.filters import ComponentFilter, RecipeFilter
from .serializers import (ComponentSerializer, ComponentPostSerializer,
                          ComponentUnitSerializer, FavoriteSerializer,
                          RecipeInfoSerializer, RecipePostSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer,)
from .utils import get_shopping_cart


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.select_related('unit').all()
    serializer_class = ComponentSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (ComponentFilter,)
    search_fields = ('^name',)

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ComponentSerializer
        return ComponentPostSerializer


class ComponentUnitViewSet(viewsets.ModelViewSet):
    queryset = ComponentUnit.objects.all()
    serializer_class = ComponentUnitSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        return RecipePostSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            user = self.request.user
        else:
            user = None
        favorites = Favorite.objects.filter(user=user)
        cart = ShoppingCart.objects.filter(user=user)
        queryset = (
            Recipe.objects
            .prefetch_related('tags', 'ingredients',)
            .select_related('author')
            .annotate(is_favorited=Exists(favorites))
            .annotate(is_in_shopping_cart=Exists(cart))
            .order_by('-pub_date')
        )
        return queryset

    @action(
        ('post',), permission_classes=(permissions.IsAuthenticated,),
        detail=True,
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = RecipeInfoSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        get_object_or_404(
            Favorite, user=user, recipe=recipe,
        ).delete()
        message = {
            'detail': 'Рецепт удалён из избранного'
        }
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(
        ('post',), permission_classes=(permissions.IsAuthenticated,),
        detail=True,
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = ShoppingCartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = RecipeInfoSerializer(
            recipe, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        get_object_or_404(
            ShoppingCart, user=user, recipe=recipe,
        ).delete()
        message = {
            'detail': 'Рецепт удалён из корзины'
        }
        return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(
        ('get',), permission_classes=(permissions.IsAuthenticated,),
        detail=False,
    )
    def download_shopping_cart(self, request):
        user = request.user
        content = get_shopping_cart(user)
        file = 'shopping_cart.txt'
        response = FileResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response
