from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets

from foodgram.pagination import CustomPagination
from users.models import Subscription, User
from .serializers import (SignUpSerializer, SubscriptionSerializer,
                          SubscriptionUserSerializer, UserSerializer,)


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    pagination_class = CustomPagination
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'me'):
            return UserSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        return SignUpSerializer

    @action(('get',), permission_classes=(IsAuthenticated,), detail=False,)
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            subscribing__user=user
        ).prefetch_related('prescriptors')
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionUserSerializer(
            page, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class UserSubscribeViewSet(viewsets.ViewSet):
    pagination_class = CustomPagination
    permission_classes = (IsAuthenticated,)
    serializer_class = SubscriptionSerializer

    def create(self, request, *args, **kwargs):
        id = kwargs['pk']
        user = request.user
        author = get_object_or_404(User, pk=id)

        data = {
            'author': author.pk,
            'user': user.pk,
        }
        serializer = SubscriptionSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = SubscriptionUserSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        id = kwargs['pk']
        user = request.user
        author = get_object_or_404(User, pk=id)
        get_object_or_404(
            Subscription, author=author, user=user,
        ).delete()
        message = {
            'detail': 'Вы отписались'
        }
        return Response(message, status=status.HTTP_204_NO_CONTENT)
