import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from prescripts.models import (Component, ComponentUnit, Favorite, Prescriptor,
                               PrescriptorComponent, ShoppingCart, Tag)
from users.serializers import UserSerializer


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = Tag


class ComponentUnitSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ComponentUnit


class ComponentSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.StringRelatedField(
        read_only=True, source='unit',
    )

    class Meta:
        fields = '__all__'
        model = Component


class ComponentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = '__all__'


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class PrescriptorComponentSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Component.objects.all(),
        source='component.id',
        error_messages={'does_not_exist': 'Такого ингредиента не существует'},
    )
    name = serializers.CharField(source='component.name', read_only=True,)
    unit = serializers.CharField(source='component.unit.id', read_only=True,)
    measurement_unit = serializers.StringRelatedField(source='component.unit')
    amount = serializers.IntegerField(
        validators=(MinValueValidator(
            1, message='Количество не меньше 1'),
        )
    )

    class Meta:
        model = PrescriptorComponent
        fields = ('id', 'name', 'unit', 'measurement_unit', 'amount',)


class PrescriptorSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True,)
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = PrescriptorComponentSerializer(
        many=True, source='prescriptor_component'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart'
    )

    class Meta:
        model = Prescriptor
        fields = ('id', 'author', 'name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart',)

    def get_is_favorited(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.favorites.filter(user=user).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return obj.cart.filter(user=user).exists()


class PrescriptorPostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True,)
    image = Base64ImageField(required=True, allow_null=False, max_length=None)
    ingredients = PrescriptorComponentSerializer(
        many=True, required=True,
        source='prescriptor_component',
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True,
        error_messages={'does_not_exist': 'Такого тега не существует'}
    )
    cooking_time = serializers.IntegerField(
        required=True,
        validators=(MinValueValidator(
            1, message='Время приготовления (в минутах) не меньше 1'),)
    )

    class Meta:
        model = Prescriptor
        fields = ('id', 'author', 'name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time',)

    @staticmethod
    def _set_components(prescriptor, components):
        prescriptor_component = []
        for tmp in components:
            component = tmp['component']['id']
            amount = tmp.get('amount')
            prescriptor_component.append(
                PrescriptorComponent(
                    prescriptor=prescriptor,
                    component=component,
                    amount=amount
                )
            )
        PrescriptorComponent.objects.bulk_create(prescriptor_component)

    def create(self, validated_data):
        author = self.context.get('request').user
        components = validated_data.pop('prescriptor_component')
        tags = validated_data.pop('tags')

        with transaction.atomic():
            prescriptor = Prescriptor.objects.create(
                author=author, **validated_data
            )
            prescriptor.tags.set(tags)
            self._set_components(prescriptor, components)

        return prescriptor

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        tags = validated_data.pop('tags')
        components = validated_data.pop('prescriptor_component')

        with transaction.atomic():
            instance.tags.clear()
            instance.tags.set(tags)
            instance.ingredients.clear()
            self._set_components(instance, components)
            instance.save()

        return instance


class PrescriptorInfoSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Prescriptor
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого пользователя не существует'},
    )
    prescriptor = serializers.PrimaryKeyRelatedField(
        queryset=Prescriptor.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого рецепта не существует'},
    )

    class Meta:
        model = Favorite
        fields = ('user', 'prescriptor',)

    def validate(self, data):
        user = data.get('user')
        prescriptor = data.get('prescriptor')
        if user.favorites.filter(prescriptor=prescriptor).exists():
            raise ValidationError({'error': 'Рецепт уже в избранном'})
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого пользователя не существует'},
    )
    prescriptor = serializers.PrimaryKeyRelatedField(
        queryset=Prescriptor.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого рецепта не существует'},
    )

    class Meta:
        model = ShoppingCart
        fields = ('user', 'prescriptor',)

    def validate(self, data):
        user = data.get('user')
        prescriptor = data.get('prescriptor')
        if user.cart.filter(prescriptor=prescriptor).exists():
            raise ValidationError({'error': 'Рецепт уже в корзине'})
        return data
