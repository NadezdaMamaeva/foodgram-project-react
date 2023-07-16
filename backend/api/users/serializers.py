from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import Recipe

from users.models import Subscription, User
from users.validators import validate_username


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


class UserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(
        method_name='get_is_subscribed'
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.subscribing.filter(user=user).exists()


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionUserSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField(read_only=True,)
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',
        )
        read_only_fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        if limit:
            recipes = obj.recipes.all()[:(int(limit))]
        else:
            recipes = obj.recipes.all()
        serializer = SubscriptionRecipeSerializer(
            recipes, many=True, read_only=True,
        )
        return serializer.data


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ('author', 'user',)

    def validate(self, data):
        user = data.get('user')
        author = data.get('author')
        if author == user:
            raise ValidationError({'error': 'Нельзя подписаться на себя'})
        if author.subscribing.filter(user=user).exists():
            raise ValidationError({'error': 'Подписка уже существует'})
        return data
