import webcolors
from rest_framework import serializers

from prescripts.models import Component, ComponentUnit, Tag


class Hex2NameColor(serializers.Field):
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class TagSerializer(serializers.ModelSerializer):
    color = Hex2NameColor(label='Цвет')
    class Meta:
        fields = '__all__'
        model = Tag


class ComponentUnitSerializer(serializers.ModelSerializer):
    class Meta:
        fields = '__all__'
        model = ComponentUnit


class ComponentSerializer(serializers.ModelSerializer):
    unit = serializers.StringRelatedField(read_only=True)
 
    class Meta:
        fields = '__all__'
        model = Component


class ComponentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = '__all__'
