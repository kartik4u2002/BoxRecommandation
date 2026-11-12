from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from products.models import Product


class Order(models.Model):
    """
    Represents a customer order containing one or more products.
    """
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PACKED', 'Packed'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    customer_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        ordering = ['-created_at']

    @property
    def total_weight(self) -> Decimal:
        """Calculate total weight of all items in the order."""
        total = Decimal('0.00')
        for item in self.items.select_related('product'):
            total += item.product.weight * item.quantity
        return total

    @property
    def total_volume(self) -> Decimal:
        """Calculate total volume of all items in the order."""
        total = Decimal('0.00')
        for item in self.items.select_related('product'):
            total += item.product.volume * item.quantity
        return total

    def __str__(self):
        return f"Order #{self.id} - {self.customer_name} ({self.status})"


class OrderItem(models.Model):
    """
    Represents an item within an order, linking a product with a specific quantity.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity of product in the order. Must be at least 1."
    )

    class Meta:
        unique_together = ['order', 'product']
        ordering = ['id']

    def clean(self):
        super().clean()
        if self.quantity is not None and self.quantity <= 0:
            raise ValidationError({'quantity': 'Quantity must be greater than zero.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantity}x {self.product.name} (Order #{self.order_id})"
