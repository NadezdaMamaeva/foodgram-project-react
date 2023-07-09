from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.pagination import CustomPagination

from .models import Subscription, User
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
        if self.action in ('subscribe', 'subscriptions',):
            return SubscriptionUserSerializer
        return SignUpSerializer

    @action(('post',), detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data['new_password'])
        self.request.user.save()
        return Response(
            {
                'detail': 'Пароль изменён успешно'
            },
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        ('post', 'delete'), permission_classes=(IsAuthenticated,),
        detail=True,
    )
    def subscribe(self, request, id):
        user = request.user
        author = get_object_or_404(User, pk=id)

        if request.method == 'POST':
            data = {
                'author': author.pk,
                'user': user.pk,
            }
            serializer = SubscriptionSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = self.get_serializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            get_object_or_404(
                Subscription, author=author, user=user,
            ).delete()
            message = {
                'detail': 'Вы отписались'
            }
            return Response(message, status=status.HTTP_204_NO_CONTENT)

    @action(('get',), permission_classes=(IsAuthenticated,), detail=False,)
    def subscriptions(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            subscribing__user=user
        ).prefetch_related('prescriptors')
        page = self.paginate_queryset(subscriptions)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
