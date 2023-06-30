from rest_framework import permissions
from rest_framework import viewsets

from prescripts.models import Component, ComponentUnit, Prescriptor, Tag
from users.pagination import CustomPagination

from .serializers import (ComponentSerializer, ComponentPostSerializer,
                          ComponentUnitSerializer, PrescriptorPostSerializer,
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
        return PrescriptorPostSerializer

    def get_queryset(self):
        if self.action in ('list', 'retrieve'):
            queryset = (Prescriptor.objects
                          .prefetch_related('tags')
                          .prefetch_related('ingredients')
                          .order_by('-pub_date'))
            return queryset
        return Prescriptor.objects.all()
