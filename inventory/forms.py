# inventory/forms.py
from django import forms
from .models import Item, Barcode
from django.core.validators import MinValueValidator

class ItemForm(forms.ModelForm):
    """Form for creating a new item."""
    class Meta:
        model = Item
        # Include fields relevant for *creation*, now with location
        fields = ['name', 'quantity', 'unit', 'quantity_needed', 'is_open', 'location']
        labels = {
            'quantity': 'Initial Sealed Quantity',
            'quantity_needed': 'Quantity Needed (if adding to shopping list now)',
            'is_open': 'Is a unit already open?',
            'location': 'Storage Location'
        }
        help_texts = {
            'quantity': 'Number of unopened/sealed units.',
            'quantity_needed': 'Set > 0 to add to shopping list immediately.',
            'is_open': 'Check if you already have an open package/unit.',
            'location': 'Where this item should be stored (e.g., Pantry, Fridge, Freezer)'
        }
        widgets = {
             'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
             'quantity_needed': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
        }

class AddToShoppingListForm(forms.Form):
    """Form to specify how many units are needed."""
    quantity_needed = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)], # Must need at least 1
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '1'}),
        label="Quantity Needed"
    )

class PurchaseForm(forms.Form):
    """Form to record how many units were purchased."""
    quantity_purchased = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)], # Must buy > 0
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        label="Quantity Purchased"
    )

class QuantityUpdateForm(forms.ModelForm):
    """Form to update sealed quantity, open status, and location."""
    class Meta:
        model = Item
        fields = ['quantity', 'is_open', 'location'] # Added location field
        labels = {
            'quantity': 'New Sealed Quantity',
            'is_open': 'Is a unit currently open?',
            'location': 'Storage Location'
        }
        widgets = {
             'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0'})
        }

class BarcodeForm(forms.ModelForm):
    """Form for adding or editing a barcode."""
    class Meta:
        model = Barcode
        fields = ['code', 'item', 'quantity', 'description']
        widgets = {
            'quantity': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'})
        }

class BarcodeScanForm(forms.Form):
    """Form for scanning a barcode."""
    barcode = forms.CharField(
        max_length=100,
        label="Scan Barcode",
        widget=forms.TextInput(attrs={'autofocus': 'autofocus'})
    )
    action = forms.ChoiceField(
        choices=[
            ('add', 'Add to Inventory'),
            ('remove', 'Remove from Inventory'),
            ('open', 'Open Package')
        ],
        initial='add',
        widget=forms.RadioSelect
    )
