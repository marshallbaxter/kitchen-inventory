# inventory/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponseNotAllowed
from django.db.models import F, Q # Import F and Q for database operations
from django.utils.safestring import mark_safe
from .models import Item, Barcode
# Import the forms you just defined
from .forms import ItemForm, AddToShoppingListForm, PurchaseForm, QuantityUpdateForm, BarcodeForm, BarcodeScanForm
from django.contrib import messages

def inventory_list(request):
    # Show items physically present (sealed quantity > 0 OR an open unit exists)
    items_in_stock = Item.objects.filter(Q(quantity__gt=0) | Q(is_open=True)).order_by('name') # Explicit ordering
    context = {
        'items': items_in_stock,
        'page_title': 'Items in Inventory',
        'list_type': 'inventory'
    }
    return render(request, 'inventory/item_list.html', context)

def shopping_list(request):
    # Show items with quantity_needed > 0
    items_needed = Item.objects.filter(quantity_needed__gt=0).order_by('name') # Explicit ordering
    context = {
        'items': items_needed,
        'page_title': 'Shopping List',
        'list_type': 'shopping'
    }
    return render(request, 'inventory/item_list.html', context)

def add_item(request):
    # Handles initial creation of an item
    if request.method == 'POST':
        form = ItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            # Redirect intelligently based on initial state
            if item.is_on_shopping_list:
                return redirect('inventory:shopping_list')
            elif item.quantity > 0 or item.is_open:
                return redirect('inventory:inventory_list')
            else: # Added with 0 qty, not open, not needed (rare)
                 return redirect('inventory:add_item') # Or inventory list
    else: # GET request
        form = ItemForm()

    context = {'form': form, 'page_title': 'Add New Item'}
    return render(request, 'inventory/item_form.html', context)


# --- Actions ---

def add_to_shopping_list(request, item_id):
    """View to set the quantity_needed for an item."""
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = AddToShoppingListForm(request.POST)
        if form.is_valid():
            item.quantity_needed = form.cleaned_data['quantity_needed']
            item.save()
            return redirect('inventory:shopping_list') # Go to shopping list after adding
    else: # GET request
        # Pre-fill with 1 if currently 0, else keep existing needed amount
        initial_needed = item.quantity_needed if item.quantity_needed > 0 else 1
        form = AddToShoppingListForm(initial={'quantity_needed': initial_needed})

    context = {
        'form': form,
        'item': item,
        'page_title': f'How many {item.name} to buy?'
    }
    return render(request, 'inventory/add_to_shopping_form.html', context)


def remove_from_shopping_list(request, item_id):
    """Sets quantity_needed to 0."""
    if request.method == 'POST': # Enforce POST for actions that change data
        item = get_object_or_404(Item, pk=item_id)
        item.quantity_needed = 0
        item.save()
        # Try to redirect back to the page the user came from, default to inventory
        referer = request.META.get('HTTP_REFERER')
        if referer:
            # Basic check if user was on shopping list page
            if reverse('inventory:shopping_list') in referer:
                 return redirect('inventory:shopping_list')
        return redirect('inventory:inventory_list') # Default back to inventory
    else:
        return HttpResponseNotAllowed(['POST'])


def mark_purchased(request, item_id):
    """Handles purchasing items from the shopping list."""
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = PurchaseForm(request.POST)
        if form.is_valid():
            purchased_qty = form.cleaned_data['quantity_purchased']
            # Add purchased amount to the sealed quantity using F expression for safety
            item.quantity = F('quantity') + purchased_qty
            # Remove from shopping list
            item.quantity_needed = 0
            item.save()
            return redirect('inventory:shopping_list') # Back to shopping list
    else: # GET request
        # Pre-fill form with the amount that was needed
        form = PurchaseForm(initial={'quantity_purchased': item.quantity_needed})

    context = {
        'form': form,
        'item': item,
        'page_title': f'Purchased {item.name}'
    }
    return render(request, 'inventory/purchase_form.html', context)


def update_sealed_quantity(request, item_id):
    """Updates the sealed quantity and potentially the open status."""
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        # Pass instance=item to update the existing item
        form = QuantityUpdateForm(request.POST, instance=item)
        if form.is_valid():
            form.save() # Saves quantity and is_open status
            # Redirect intelligently
            # Try redirecting back to where user came from
            referer = request.META.get('HTTP_REFERER')
            if referer:
                if reverse('inventory:shopping_list') in referer and item.is_on_shopping_list:
                     return redirect('inventory:shopping_list')
            # Default redirects
            if item.quantity > 0 or item.is_open:
                return redirect('inventory:inventory_list')
            else: # If quantity is 0 and not open, maybe shopping list if still needed?
                return redirect('inventory:inventory_list') # Default to inventory

    else: # GET request
        # Pre-fill form with current data
        form = QuantityUpdateForm(instance=item)

    context = {
        'form': form,
        'item': item,
        'page_title': f'Update Stock for {item.name}'
    }
    # Use a generic form template or create quantity_form.html
    return render(request, 'inventory/generic_form.html', context)


def toggle_open_status(request, item_id):
    """Flips the is_open boolean flag."""
    if request.method == 'POST': # Enforce POST
        item = get_object_or_404(Item, pk=item_id)
        item.is_open = not item.is_open
        item.save()
        # Redirect back to inventory list ideally, or wherever user was
        referer = request.META.get('HTTP_REFERER')
        if referer and reverse('inventory:inventory_list') in referer:
            return redirect('inventory:inventory_list')
        # Fallback if referer is not helpful or missing
        return redirect('inventory:inventory_list')
    else:
        return HttpResponseNotAllowed(['POST'])

def delete_item(request, item_id):
    # Deletes the item entirely
     if request.method == 'POST': # Enforce POST
        item = get_object_or_404(Item, pk=item_id)
        item.delete()
        # Redirect back to list user was likely viewing
        referer = request.META.get('HTTP_REFERER')
        if referer and reverse('inventory:shopping_list') in referer:
             return redirect('inventory:shopping_list')
        return redirect('inventory:inventory_list') # Default
     else:
         return HttpResponseNotAllowed(['POST'])

def edit_item(request, item_id):
    """View to edit an item's details including location."""
    item = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f"{item.name} updated successfully")
            
            # Redirect intelligently based on where the item should appear
            if item.is_on_shopping_list:
                return redirect('inventory:shopping_list')
            elif item.quantity > 0 or item.is_open:
                return redirect('inventory:inventory_list')
            else:
                return redirect('inventory:inventory_list')
    else:
        form = ItemForm(instance=item)
    
    context = {
        'form': form,
        'item': item,
        'page_title': f'Edit {item.name}'
    }
    return render(request, 'inventory/item_form.html', context)

def barcode_list(request):
    """View to display all barcodes."""
    barcodes = Barcode.objects.all().order_by('code')
    context = {
        'barcodes': barcodes,
        'page_title': 'Manage Barcodes'
    }
    return render(request, 'inventory/barcode_list.html', context)

def add_barcode(request):
    """View to add a new barcode."""
    if request.method == 'POST':
        form = BarcodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:barcode_list')
    else:
        form = BarcodeForm()
    
    context = {
        'form': form,
        'page_title': 'Add New Barcode'
    }
    return render(request, 'inventory/barcode_form.html', context)

def edit_barcode(request, barcode_id):
    """View to edit an existing barcode."""
    barcode = get_object_or_404(Barcode, pk=barcode_id)
    if request.method == 'POST':
        form = BarcodeForm(request.POST, instance=barcode)
        if form.is_valid():
            form.save()
            return redirect('inventory:barcode_list')
    else:
        form = BarcodeForm(instance=barcode)
    
    context = {
        'form': form,
        'page_title': f'Edit Barcode: {barcode.code}'
    }
    return render(request, 'inventory/barcode_form.html', context)

def delete_barcode(request, barcode_id):
    """View to delete a barcode."""
    if request.method == 'POST':
        barcode = get_object_or_404(Barcode, pk=barcode_id)
        barcode.delete()
        return redirect('inventory:barcode_list')
    else:
        return HttpResponseNotAllowed(['POST'])

def scan_barcode(request):
    """View to scan and process barcodes."""
    recent_scans = Barcode.objects.all().order_by('-id')[:5]  # Show 5 most recent barcodes
    
    if request.method == 'POST':
        form = BarcodeScanForm(request.POST)
        if form.is_valid():
            barcode_value = form.cleaned_data['barcode']
            action = form.cleaned_data['action']
            
            try:
                barcode = Barcode.objects.get(code=barcode_value)
                item = barcode.item
                
                # Create base message without location info
                if action == 'add':
                    # Add to inventory and decrease shopping list (never below zero)
                    item.quantity = F('quantity') + barcode.quantity
                    
                    # If item is on shopping list, decrease needed quantity (but never below zero)
                    if item.quantity_needed > 0:
                        # We need to refresh from DB to get current values before comparing
                        item.save()
                        item.refresh_from_db()
                        
                        # Calculate new needed quantity (never below zero)
                        new_needed = max(0, item.quantity_needed - barcode.quantity)
                        item.quantity_needed = new_needed
                        item.save()
                        
                        base_msg = f"Added {barcode.quantity} {item.unit or ''} of {item.name} to inventory and updated shopping list"
                    else:
                        item.save()
                        base_msg = f"Added {barcode.quantity} {item.unit or ''} of {item.name} to inventory"
                
                elif action == 'remove':
                    # Remove from inventory and add to shopping list if not already there
                    if item.quantity >= barcode.quantity:
                        item.quantity = F('quantity') - barcode.quantity
                        
                        # If not on shopping list, add it with quantity 1
                        if item.quantity_needed == 0:
                            item.quantity_needed = 1
                            
                        item.save()
                        base_msg = f"Removed {barcode.quantity} {item.unit or ''} of {item.name} from inventory and updated shopping list"
                    else:
                        messages.error(request, f"Not enough {item.name} in inventory to remove")
                
                elif action == 'open':
                    # Mark a package as open and increase shopping list quantity
                    item.is_open = True
                    item.quantity_needed = F('quantity_needed') + 1
                    item.save()
                    base_msg = f"Marked {item.name} as open and added to shopping list"
                
                # Add location info if available and send message with appropriate class
                if item.location:
                    full_msg = f"{base_msg}<span class='location-section'>Store in: {item.location}</span>"
                    messages.success(request, mark_safe(full_msg))
                else:
                    messages.success(request, base_msg)
                
            except Barcode.DoesNotExist:
                messages.error(request, f"Barcode {barcode_value} not found. Please add it first.")
            
            # Return a new form with the same action selected
            form = BarcodeScanForm(initial={'action': action})
    else:
        form = BarcodeScanForm()
    
    context = {
        'form': form,
        'recent_scans': recent_scans,
        'page_title': 'Scan Barcode'
    }
    return render(request, 'inventory/scan_barcode.html', context)
