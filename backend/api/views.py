from django.db.models import Sum
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from prescripts.models import (Component, ComponentUnit, Favorite, Prescriptor,
                               PrescriptorComponent, ShoppingCart, Tag,)
from users.pagination import CustomPagination
from users.permissions import IsAdminOrReadOnly

from .filters import ComponentFilter, PrescriptorFilter
from .serializers import (ComponentSerializer, ComponentPostSerializer,
                          ComponentUnitSerializer, FavoriteSerializer,
                          PrescriptorInfoSerializer, PrescriptorPostSerializer,
                          PrescriptorSerializer, ShoppingCartSerializer,
                          TagSerializer,)


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


class PrescriptorViewSet(viewsets.ModelViewSet):
    queryset = Prescriptor.objects.all()
    serializer_class = PrescriptorSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = PrescriptorFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return PrescriptorSerializer
        elif self.action in ('favorite', 'shopping_cart'):
            return PrescriptorInfoSerializer
        return PrescriptorPostSerializer

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            queryset = (Prescriptor.objects
                        .prefetch_related('tags')
                        .prefetch_related('ingredients')
                        .order_by('-pub_date')
                        )
            return queryset
        return Prescriptor.objects.all()

    @action(
        ('post', 'delete'), permission_classes=(permissions.IsAuthenticated,),
        detail=True,
    )
    def favorite(self, request, pk):
        user = request.user
        prescriptor = get_object_or_404(Prescriptor, pk=pk)

        if request.method == 'POST':
            data = {
                'user': user.id,
                'prescriptor': prescriptor.id,
            }
            serializer = FavoriteSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.get_serializer(prescriptor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            get_object_or_404(
                Favorite, user=user, prescriptor=prescriptor,
            ).delete()
            message = {
                'detail': 'Рецепт удалён из избранного'
            }
            return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(
        ('post', 'delete'), permission_classes=(permissions.IsAuthenticated,),
        detail=True,
    )
    def shopping_cart(self, request, pk):
        user = request.user
        prescriptor = get_object_or_404(Prescriptor, pk=pk)

        if request.method == 'POST':
            data = {
                'user': user.id,
                'prescriptor': prescriptor.id,
            }
            serializer = ShoppingCartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.get_serializer(prescriptor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            get_object_or_404(
                ShoppingCart, user=user, prescriptor=prescriptor,
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
        components = PrescriptorComponent.objects.filter(
            prescriptor__cart__user=user
        ).order_by(
            'component__name',
        ).values(
            'component__name',
            'component__unit__name',
        ).annotate(amount=Sum('amount'))
        data = []
        for component in components:
            data.append(
                f'{component["component__name"]} '
                f'({component["component__unit__name"]}) - '
                f'{component["amount"]}'
            )
        content = '\n'.join(data)
        file = 'shopping_cart.txt'
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={file}'
        return response
