"""
Ecommerce models for Store, Product, and Review.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Store(models.Model):
    """
    Store model representing a vendor's store.
    
    Attributes:
        vendor: Foreign key to User (vendor)
        name: Store name (max 200 characters)
        description: Store description
        logo: Optional store logo image
        created_at: Timestamp when store was created
    """
    vendor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stores',
        help_text="The vendor who owns this store"
    )
    name = models.CharField(
        max_length=200,
        help_text="Store name"
    )
    description = models.TextField(
        help_text="Store description"
    )
    logo = models.ImageField(
        upload_to='store_logos/',
        null=True,
        blank=True,
        help_text="Store logo image"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when store was created"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Store'
        verbose_name_plural = 'Stores'

    def __str__(self):
        return self.name


class Product(models.Model):
    """
    Product model representing a product in a store.
    
    Attributes:
        store: Foreign key to Store
        name: Product name (max 200 characters)
        description: Product description
        price: Product price (decimal, max 10 digits, 2 decimal places)
        image: Optional product image
        created_at: Timestamp when product was created
    """
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='products',
        help_text="The store this product belongs to"
    )
    name = models.CharField(
        max_length=200,
        help_text="Product name"
    )
    description = models.TextField(
        help_text="Product description"
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text="Product price"
    )
    image = models.ImageField(
        upload_to='product_images/',
        null=True,
        blank=True,
        help_text="Product image"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when product was created"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Product'
        verbose_name_plural = 'Products'

    def __str__(self):
        return f"{self.name} - {self.store.name}"


class Review(models.Model):
    """
    Review model representing a user's review of a product.
    
    Attributes:
        product: Foreign key to Product
        user: Foreign key to User (reviewer)
        rating: Rating from 1 to 5
        comment: Review comment text
        created_at: Timestamp when review was created
    """
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The product being reviewed"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text="The user who wrote the review"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    comment = models.TextField(
        help_text="Review comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when review was created"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        unique_together = ['product', 'user']  # One review per user per product

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}/5"


