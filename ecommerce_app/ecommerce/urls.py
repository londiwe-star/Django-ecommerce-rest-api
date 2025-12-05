"""
URL configuration for ecommerce API endpoints.
"""
from django.urls import path
from . import views

app_name = 'ecommerce'

urlpatterns = [
    # Store endpoints
    path('stores/', views.stores_list_create, name='stores-list-create'),
    path('stores/<int:store_id>/', views.store_detail, name='store-detail'),
    path('stores/<int:store_id>/products/', views.store_products, name='store-products'),
    path('stores/<int:store_id>/reviews/', views.get_vendor_store_reviews, name='store-reviews'),
    
    # Product endpoints
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    
    # Vendor endpoints
    path('vendors/<int:vendor_id>/stores/', views.get_vendor_stores, name='vendor-stores'),
]

