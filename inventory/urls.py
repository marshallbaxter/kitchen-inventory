# inventory/urls.py
from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # List views
    path('', views.inventory_list, name='inventory_list'),
    path('shopping/', views.shopping_list, name='shopping_list'),

    # Item Creation
    path('add/', views.add_item, name='add_item'),

    # Actions (triggered by GET links leading to forms, or POST form submissions)
    path('add_needed/<int:item_id>/', views.add_to_shopping_list, name='add_to_shopping_list'),
    path('update_stock/<int:item_id>/', views.update_sealed_quantity, name='update_stock'),
    path('purchased/<int:item_id>/', views.mark_purchased, name='mark_purchased'),

    # Actions (POST only - triggered by forms in templates)
    path('remove_needed/<int:item_id>/', views.remove_from_shopping_list, name='remove_from_shopping_list'),
    path('toggle_open/<int:item_id>/', views.toggle_open_status, name='toggle_open'),
    path('delete/<int:item_id>/', views.delete_item, name='delete_item'),
    
    # Barcode functionality
    path('barcodes/', views.barcode_list, name='barcode_list'),
    path('barcodes/add/', views.add_barcode, name='add_barcode'),
    path('barcodes/edit/<int:barcode_id>/', views.edit_barcode, name='edit_barcode'),
    path('barcodes/delete/<int:barcode_id>/', views.delete_barcode, name='delete_barcode'),
    path('scan/', views.scan_barcode, name='scan_barcode'),
    path('item/<int:item_id>/edit/', views.edit_item, name='edit_item'),
]
