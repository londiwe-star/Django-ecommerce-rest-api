"""
Django admin configuration for ecommerce models.
"""
from django.contrib import admin
from .models import Store, Product, Review


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    """Admin interface for Store model."""
    list_display = ['name', 'vendor', 'created_at']
    list_filter = ['created_at', 'vendor']
    search_fields = ['name', 'description', 'vendor__username']
    readonly_fields = ['created_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin interface for Product model."""
    list_display = ['name', 'store', 'price', 'created_at']
    list_filter = ['created_at', 'store']
    search_fields = ['name', 'description', 'store__name']
    readonly_fields = ['created_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin interface for Review model."""
    list_display = ['product', 'user', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['product__name', 'user__username', 'comment']
    readonly_fields = ['created_at']


