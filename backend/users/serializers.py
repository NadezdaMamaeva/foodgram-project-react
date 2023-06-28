from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import User
from .validators import validate_username


class SignUpSerializer(UserCreateSerializer):
    username = serializers.CharField(
        label='Имя пользователя', allow_blank=False, max_length=150,
        validators=(validate_username,),
    )
    email = serializers.EmailField(
        label='Адрес электронной почты', allow_blank=False, max_length=254
    )
    password = serializers.CharField(
        label='Пароль', allow_blank=False, max_length=150,
        validators=(validate_password,), style={'input_type': 'password'},
        write_only=True,
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'first_name', 'last_name',
        )

    def validate(self, data):
        user = User.objects.filter(email=data.get('email')).first()
        if user and (user.username != data.get('username')):
            raise ValidationError({'email': 'Email уже занят.'})
        user = User.objects.filter(username=data.get('username')).first()
        if user and (user.email != data.get('email')):
            raise ValidationError({'username': 'Имя пользователя уже занято.'})
        return data


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'is_subscribed',
        )

    def update(self, instance, validated_data):
        validated_data.pop('role', None)
        return super().update(instance, validated_data)

    def get_is_subscribed(self, obj):
        return False
    #   user = self.context.get('request').user
    #    return user.is_authenticated and user.subscriber.filter(
    #        user=user, author=obj
    #    ).exists()
