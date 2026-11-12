from decimal import Decimal
from rest_framework import serializers
from products.models import Product
from products.serializers import ProductSerializer
from .models import Order, OrderItem


class OrderItemReadSerializer(serializers.ModelSerializer):
    """
    Serializer for reading order items with nested product details.
    """
    product = ProductSerializer(read_only=True)
    subtotal_weight = serializers.SerializerMethodField()
    subtotal_volume = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'subtotal_weight', 'subtotal_volume']

    def get_subtotal_weight(self, obj) -> Decimal:
        return obj.product.weight * obj.quantity

    def get_subtotal_volume(self, obj) -> Decimal:
        return obj.product.volume * obj.quantity


class OrderItemInputSerializer(serializers.Serializer):
    """
    Serializer for validating order item payload during order creation.
    Supports either 'product_id' or 'product'.
    """
    product_id = serializers.IntegerField(required=False)
    product = serializers.IntegerField(required=False)
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, attrs):
        product_id = attrs.get('product_id') or attrs.get('product')
        if not product_id:
            raise serializers.ValidationError("Either 'product_id' or 'product' must be provided.")
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError(f"Product with id {product_id} does not exist.")
        attrs['product_instance'] = product
        return attrs


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing detailed order information.
    """
    items = OrderItemReadSerializer(many=True, read_only=True)
    total_weight = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_volume = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'status', 'created_at', 'total_weight', 'total_volume', 'items']
        read_only_fields = ['id', 'created_at', 'total_weight', 'total_volume', 'items']


class OrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an order with one or more order items in an atomic transaction.
    """
    items = OrderItemInputSerializer(many=True, required=True)

    class Meta:
        model = Order
        fields = ['id', 'customer_name', 'status', 'created_at', 'items']
        read_only_fields = ['id', 'created_at']

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("An order must contain at least one item.")
        return items

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        # Aggregate quantities if same product appears multiple times
        product_quantities = {}
        for item_data in items_data:
            product = item_data['product_instance']
            product_quantities[product] = product_quantities.get(product, 0) + item_data['quantity']

        for product, quantity in product_quantities.items():
            OrderItem.objects.create(order=order, product=product, quantity=quantity)

        return order

    def to_representation(self, instance):
        return OrderSerializer(instance).data
