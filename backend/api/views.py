from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .serializers import TagSerializer

from prescripts.models import Tag


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny,)
    pagination_class = PageNumberPagination
