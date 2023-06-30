from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from prescripts.models import (Component, ComponentUnit, Favorite, Prescriptor,
                               Tag,)
from users.pagination import CustomPagination

from .serializers import (ComponentSerializer, ComponentPostSerializer,
                          ComponentUnitSerializer, FavoriteSerializer,
                          PrescriptorInfoSerializer, PrescriptorPostSerializer,
                          PrescriptorSerializer, TagSerializer,)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.select_related('unit').all()
    serializer_class = ComponentSerializer
    permission_classes = (permissions.AllowAny,)
 
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ComponentSerializer
        return ComponentPostSerializer


class ComponentUnitViewSet(viewsets.ModelViewSet):
    queryset = ComponentUnit.objects.all()
    serializer_class = ComponentUnitSerializer
    permission_classes = (permissions.AllowAny,)


class PrescriptorViewSet(viewsets.ModelViewSet):
    queryset = Prescriptor.objects.all()
    serializer_class = PrescriptorSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return PrescriptorSerializer
        elif self.action in ('favorite'):
            return PrescriptorInfoSerializer
        return PrescriptorPostSerializer

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            queryset = (Prescriptor.objects
                          .prefetch_related('tags')
                          .prefetch_related('ingredients')
                          .order_by('-pub_date'))
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
