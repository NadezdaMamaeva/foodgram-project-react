from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.pagination import (LimitOffsetPagination, 
                                       PageNumberPagination,)

from .serializers import (ComponentSerializer, ComponentPostSerializer, 
                          ComponentUnitSerializer, TagSerializer,)

from prescripts.models import Component, ComponentUnit, Tag


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberPagination


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.select_related('unit').all()
    serializer_class = ComponentSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = LimitOffsetPagination
 
    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ComponentSerializer
        return ComponentPostSerializer


class ComponentUnitViewSet(viewsets.ModelViewSet):
    queryset = ComponentUnit.objects.all()
    serializer_class = ComponentUnitSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = LimitOffsetPagination
