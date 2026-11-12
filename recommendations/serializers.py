from decimal import Decimal
from rest_framework import serializers


def format_number(val):
    """Format Decimal or float nicely: int if whole number, else float."""
    if val is None:
        return None
    d = Decimal(str(val))
    if d == d.to_integral_value():
        return int(d)
    return float(round(d, 2))


class BoxDimensionsSerializer(serializers.Serializer):
    length = serializers.SerializerMethodField()
    width = serializers.SerializerMethodField()
    height = serializers.SerializerMethodField()

    def get_length(self, obj):
        return format_number(obj.length)

    def get_width(self, obj):
        return format_number(obj.width)

    def get_height(self, obj):
        return format_number(obj.height)


class RecommendedBoxDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    dimensions = serializers.SerializerMethodField()
    max_weight = serializers.SerializerMethodField()
    actual_weight = serializers.SerializerMethodField()
    cost = serializers.SerializerMethodField()

    def get_dimensions(self, obj):
        return {
            'length': format_number(obj.length),
            'width': format_number(obj.width),
            'height': format_number(obj.height),
        }

    def get_max_weight(self, obj):
        return format_number(obj.max_weight)

    def get_actual_weight(self, obj):
        actual_weight = self.context.get('actual_weight', Decimal('0.00'))
        return format_number(actual_weight)

    def get_cost(self, obj):
        return format_number(obj.cost)
