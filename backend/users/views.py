from djoser.views import UserViewSet
from rest_framework import exceptions, filters, pagination, viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView
from rest_framework.pagination import PageNumberPagination

from users.models import User

from .permissions import IsAdminOrReadOnly, IsAdmin, IsAuthorOrAdminOrReadOnly
from .serializers import SignUpSerializer, UserSerializer


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return UserSerializer
        return SignUpSerializer
