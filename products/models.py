from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator


class Product(models.Model):
    """
    Represents a sellable product with physical dimensions and weight.
    """
    name = models.CharField(max_length=255)
    length = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Length in centimeters. Must be greater than 0."
    )
    width = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Width in centimeters. Must be greater than 0."
    )
    height = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Height in centimeters. Must be greater than 0."
    )
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Weight in kilograms. Must be greater than or equal to 0."
    )

    class Meta:
        ordering = ['id']

    @property
    def volume(self) -> Decimal:
        """Calculate product volume in cubic centimeters."""
        return self.length * self.width * self.height

    def clean(self):
        super().clean()
        if self.length is not None and self.length <= Decimal('0'):
            raise ValidationError({'length': 'Length must be greater than zero.'})
        if self.width is not None and self.width <= Decimal('0'):
            raise ValidationError({'width': 'Width must be greater than zero.'})
        if self.height is not None and self.height <= Decimal('0'):
            raise ValidationError({'height': 'Height must be greater than zero.'})
        if self.weight is not None and self.weight < Decimal('0'):
            raise ValidationError({'weight': 'Weight must not be negative.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.length}x{self.width}x{self.height} cm, {self.weight} kg)"
