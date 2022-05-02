from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    measurement_unit = serializers.CharField(source="unit")

    class Meta:
        model = Product
        fields = ("id", "name", "measurement_unit")
