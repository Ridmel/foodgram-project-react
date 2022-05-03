from rest_framework import serializers

from .models import Product, Tag


class ProductSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source="unit")

    class Meta:
        model = Product
        fields = ("id", "name", "measurement_unit")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
