"""
Test cases for ecommerce API endpoints.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from .models import Store, Product, Review


class StoreAPITestCase(TestCase):
    """Test cases for Store API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='vendor1',
            password='testpass123',
            email='vendor1@test.com'
        )
        self.other_user = User.objects.create_user(
            username='vendor2',
            password='testpass123',
            email='vendor2@test.com'
        )
        self.store = Store.objects.create(
            vendor=self.user,
            name='Test Store',
            description='A test store description'
        )
    
    def test_list_stores_public(self):
        """Test listing stores (public endpoint)."""
        url = reverse('ecommerce:stores-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_store_authenticated(self):
        """Test creating a store (authenticated)."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ecommerce:stores-list-create')
        data = {
            'name': 'New Store',
            'description': 'A new store'
        }
        with patch('ecommerce.views.Tweet') as mock_tweet:
            mock_instance = MagicMock()
            mock_tweet.return_value = mock_instance
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Store.objects.count(), 2)
    
    def test_create_store_unauthenticated(self):
        """Test creating a store without authentication."""
        url = reverse('ecommerce:stores-list-create')
        data = {
            'name': 'New Store',
            'description': 'A new store'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_store_detail(self):
        """Test getting store details (public)."""
        url = reverse('ecommerce:store-detail', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Store')
    
    def test_update_store_owner(self):
        """Test updating store by owner."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ecommerce:store-detail', kwargs={'store_id': self.store.id})
        data = {'name': 'Updated Store Name'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.store.refresh_from_db()
        self.assertEqual(self.store.name, 'Updated Store Name')
    
    def test_update_store_non_owner(self):
        """Test updating store by non-owner."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('ecommerce:store-detail', kwargs={'store_id': self.store.id})
        data = {'name': 'Hacked Store Name'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_store_owner(self):
        """Test deleting store by owner."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ecommerce:store-detail', kwargs={'store_id': self.store.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Store.objects.count(), 0)
    
    def test_delete_store_non_owner(self):
        """Test deleting store by non-owner."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('ecommerce:store-detail', kwargs={'store_id': self.store.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ProductAPITestCase(TestCase):
    """Test cases for Product API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='vendor1',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='vendor2',
            password='testpass123'
        )
        self.store = Store.objects.create(
            vendor=self.user,
            name='Test Store',
            description='A test store'
        )
        self.product = Product.objects.create(
            store=self.store,
            name='Test Product',
            description='A test product',
            price=99.99
        )
    
    def test_list_store_products_public(self):
        """Test listing products in a store (public)."""
        url = reverse('ecommerce:store-products', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_create_product_authenticated(self):
        """Test creating a product (authenticated, owner)."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ecommerce:store-products', kwargs={'store_id': self.store.id})
        data = {
            'name': 'New Product',
            'description': 'A new product',
            'price': '49.99'
        }
        with patch('ecommerce.views.Tweet') as mock_tweet:
            mock_instance = MagicMock()
            mock_tweet.return_value = mock_instance
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Product.objects.count(), 2)
    
    def test_create_product_non_owner(self):
        """Test creating a product by non-owner."""
        self.client.force_authenticate(user=self.other_user)
        url = reverse('ecommerce:store-products', kwargs={'store_id': self.store.id})
        data = {
            'name': 'New Product',
            'description': 'A new product',
            'price': '49.99'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_get_product_detail(self):
        """Test getting product details (public)."""
        url = reverse('ecommerce:product-detail', kwargs={'product_id': self.product.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
    
    def test_update_product_owner(self):
        """Test updating product by store owner."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ecommerce:product-detail', kwargs={'product_id': self.product.id})
        data = {'name': 'Updated Product Name', 'price': '79.99'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Updated Product Name')
    
    def test_delete_product_owner(self):
        """Test deleting product by store owner."""
        self.client.force_authenticate(user=self.user)
        url = reverse('ecommerce:product-detail', kwargs={'product_id': self.product.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)


class VendorAPITestCase(TestCase):
    """Test cases for Vendor API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='vendor1',
            password='testpass123'
        )
        self.store1 = Store.objects.create(
            vendor=self.user,
            name='Store 1',
            description='First store'
        )
        self.store2 = Store.objects.create(
            vendor=self.user,
            name='Store 2',
            description='Second store'
        )
    
    def test_get_vendor_stores(self):
        """Test getting all stores for a vendor (public)."""
        url = reverse('ecommerce:vendor-stores', kwargs={'vendor_id': self.user.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)


class ReviewAPITestCase(TestCase):
    """Test cases for Review API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.vendor = User.objects.create_user(
            username='vendor1',
            password='testpass123'
        )
        self.customer = User.objects.create_user(
            username='customer1',
            password='testpass123'
        )
        self.store = Store.objects.create(
            vendor=self.vendor,
            name='Test Store',
            description='A test store'
        )
        self.product = Product.objects.create(
            store=self.store,
            name='Test Product',
            description='A test product',
            price=99.99
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.customer,
            rating=5,
            comment='Great product!'
        )
    
    def test_get_vendor_store_reviews(self):
        """Test getting reviews for vendor's store (authenticated, owner)."""
        self.client.force_authenticate(user=self.vendor)
        url = reverse('ecommerce:store-reviews', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_get_vendor_store_reviews_non_owner(self):
        """Test getting reviews for store by non-owner."""
        self.client.force_authenticate(user=self.customer)
        url = reverse('ecommerce:store-reviews', kwargs={'store_id': self.store.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


