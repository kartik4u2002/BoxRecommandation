from decimal import Decimal
from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model with explicit boundary validation.
    """
    class Meta:
        model = Product
        fields = ['id', 'name', 'length', 'width', 'height', 'weight']
        read_only_fields = ['id']

    def validate_length(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Length must be greater than zero.")
        return value

    def validate_width(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Width must be greater than zero.")
        return value

    def validate_height(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Height must be greater than zero.")
        return value

    def validate_weight(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError("Weight must not be negative.")
        return value
