from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator

class Item(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # Represents the quantity of UNOPENED/SEALED units
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    unit = models.CharField(max_length=20, null=True, blank=True)
    # How many units are needed for the shopping list. 0 means not on list.
    quantity_needed = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    # Flag to indicate if there's an open unit/package of this item
    is_open = models.BooleanField(default=False)
    # Location where the item should be stored
    location = models.CharField(max_length=100, null=True, blank=True, 
                               help_text="Where this item should be stored (e.g., 'Pantry', 'Fridge', 'Freezer')")
    added_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def is_on_shopping_list(self):
        """Helper property to check if item should be listed"""
        return self.quantity_needed > 0

    class Meta:
        ordering = ['name']

class Barcode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='barcodes')
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1.0,
        validators=[MinValueValidator(0.01)],
        help_text="Quantity this barcode represents (e.g., 1.0 for a 1lb box)"
    )
    description = models.CharField(max_length=255, blank=True, 
        help_text="Optional description (e.g., '1lb box', '12oz can')")
    
    def __str__(self):
        return f"{self.code} - {self.item.name} ({self.quantity} {self.item.unit})"
