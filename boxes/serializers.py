from decimal import Decimal
from rest_framework import serializers
from .models import Box


class BoxSerializer(serializers.ModelSerializer):
    """
    Serializer for the Box model with explicit validation for dimensions, weight, and cost.
    """
    class Meta:
        model = Box
        fields = ['id', 'name', 'length', 'width', 'height', 'max_weight', 'cost', 'is_active']
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

    def validate_max_weight(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Max weight must be greater than zero.")
        return value

    def validate_cost(self, value):
        if value < Decimal('0'):
            raise serializers.ValidationError("Cost must not be negative.")
        return value
