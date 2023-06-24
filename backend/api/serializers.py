from rest_framework import serializers

from prescripts.models import Component, ComponentUnit, Tag


class TagSerializer(serializers.ModelSerializer):
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
