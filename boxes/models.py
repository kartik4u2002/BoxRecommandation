from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Box(models.Model):
    """
    Represents a shipping box with internal dimensions, weight capacity, and cost.
    """
    name = models.CharField(max_length=255)
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal length in centimeters. Must be greater than 0."
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal width in centimeters. Must be greater than 0."
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Internal height in centimeters. Must be greater than 0."
    )
    max_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Maximum weight capacity in kilograms. Must be greater than 0."
    )
    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost of the box. Must be greater than or equal to 0."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this box is available for recommendations."
    )

    class Meta:
        ordering = ['id']

    @property
    def volume(self) -> Decimal:
        """Calculate internal box volume in cubic centimeters."""
        return self.length * self.width * self.height

    def clean(self):
        super().clean()
        if self.length is not None and self.length <= Decimal('0'):
            raise ValidationError({'length': 'Length must be greater than zero.'})
        if self.width is not None and self.width <= Decimal('0'):
            raise ValidationError({'width': 'Width must be greater than zero.'})
        if self.height is not None and self.height <= Decimal('0'):
            raise ValidationError({'height': 'Height must be greater than zero.'})
        if self.max_weight is not None and self.max_weight <= Decimal('0'):
            raise ValidationError({'max_weight': 'Max weight must be greater than zero.'})
        if self.cost is not None and self.cost < Decimal('0'):
            raise ValidationError({'cost': 'Cost must not be negative.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.name} ({self.length}x{self.width}x{self.height} cm, "
            f"max {self.max_weight} kg, cost: {self.cost})"
        )
