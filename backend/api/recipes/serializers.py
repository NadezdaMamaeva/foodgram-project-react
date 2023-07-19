import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.validators import MinValueValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Component, ComponentUnit, Favorite, Recipe,
                            RecipeComponent, ShoppingCart, Tag)
from api.users.serializers import UserSerializer


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


class IngredientSerializer(serializers.ModelSerializer):
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
        model = RecipeComponent
        fields = ('id', 'name', 'unit', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=False, read_only=True,)
    image = Base64ImageField(required=False, allow_null=True)
    ingredients = IngredientSerializer(
        many=True, source='recipe_component'
    )
    tags = TagSerializer(many=True)
    is_favorited = serializers.BooleanField()
    is_in_shopping_cart = serializers.BooleanField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time', 'is_favorited',
                  'is_in_shopping_cart',)


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True,)
    image = Base64ImageField(required=True, allow_null=False, max_length=None)
    ingredients = IngredientSerializer(
        many=True, required=True,
        source='recipe_component',
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
        model = Recipe
        fields = ('id', 'author', 'name', 'image', 'text', 'ingredients',
                  'tags', 'cooking_time',)

    @staticmethod
    def _set_components(recipe, components):
        recipe_component = []
        for tmp in components:
            component = tmp['component']['id']
            amount = tmp.get('amount')
            recipe_component.append(
                RecipeComponent(
                    recipe=recipe,
                    component=component,
                    amount=amount
                )
            )
        RecipeComponent.objects.bulk_create(recipe_component)

    def validate(self, data):
        value = data.get('recipe_component')
        if not value:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        ingredients_set = set()
        for component in value:
            ingredient = component['component']['id']
            if ingredient in ingredients_set:
                raise ValidationError({
                    'error': f'Ингредиент "{ingredient}" повторяется!'
                })
            if int(component['amount']) <= 0:
                raise ValidationError({
                    'error': f'Количество "{ingredient}" должно быть > 0!'
                })
            ingredients_set.add(ingredient)
        return data

    def create(self, validated_data):
        author = self.context.get('request').user
        components = validated_data.pop('recipe_component')
        tags = validated_data.pop('tags')

        with transaction.atomic():
            recipe = Recipe.objects.create(
                author=author, **validated_data
            )
            recipe.tags.set(tags)
            self._set_components(recipe, components)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )

        tags = validated_data.pop('tags')
        components = validated_data.pop('recipe_component')

        with transaction.atomic():
            instance.tags.clear()
            instance.tags.set(tags)
            instance.ingredients.clear()
            self._set_components(instance, components)
            instance.save()

        return instance


class RecipeInfoSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого пользователя не существует'},
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого рецепта не существует'},
    )

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if user.favorites.filter(recipe=recipe).exists():
            raise ValidationError({'error': 'Рецепт уже в избранном'})
        return data


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого пользователя не существует'},
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True,
        error_messages={'does_not_exist': 'Такого рецепта не существует'},
    )

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)

    def validate(self, data):
        user = data.get('user')
        recipe = data.get('recipe')
        if user.cart.filter(recipe=recipe).exists():
            raise ValidationError({'error': 'Рецепт уже в корзине'})
        return data
