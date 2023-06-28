from djoser.views import UserViewSet
from djoser.serializers import SetPasswordSerializer
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from users.models import User

from .pagination import CustomPagination
from .serializers import SignUpSerializer, UserSerializer


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

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(
            {
                'detail': 'Password changed successfully'
            },
            status=status.HTTP_204_NO_CONTENT
        )
