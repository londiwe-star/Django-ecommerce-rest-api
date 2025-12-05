"""
Django REST Framework serializers for ecommerce models.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Store, Product, Review


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model (nested in other serializers).
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class StoreSerializer(serializers.ModelSerializer):
    """
    Serializer for Store model.
    
    Includes nested vendor information and validates store data.
    """
    vendor = UserSerializer(read_only=True)
    vendor_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Store
        fields = ['id', 'vendor', 'vendor_id', 'name', 'description', 'logo', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        """
        Validate store name.
        
        Args:
            value: Store name to validate
        
        Returns:
            str: Validated store name
        
        Raises:
            serializers.ValidationError: If name is empty or too short
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Store name cannot be empty")
        if len(value) < 3:
            raise serializers.ValidationError("Store name must be at least 3 characters long")
        return value.strip()

    def validate_description(self, value):
        """
        Validate store description.
        
        Args:
            value: Store description to validate
        
        Returns:
            str: Validated description
        
        Raises:
            serializers.ValidationError: If description is empty
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Store description cannot be empty")
        return value.strip()

    def create(self, validated_data):
        """
        Create a new store instance.
        
        Args:
            validated_data: Validated store data
        
        Returns:
            Store: Created store instance
        """
        validated_data.pop('vendor_id', None)
        validated_data['vendor'] = self.context['request'].user
        return super().create(validated_data)


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    
    Includes nested store information and validates product data.
    """
    store = StoreSerializer(read_only=True)
    store_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Product
        fields = ['id', 'store', 'store_id', 'name', 'description', 'price', 'image', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_name(self, value):
        """
        Validate product name.
        
        Args:
            value: Product name to validate
        
        Returns:
            str: Validated product name
        
        Raises:
            serializers.ValidationError: If name is empty or too short
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Product name cannot be empty")
        if len(value) < 3:
            raise serializers.ValidationError("Product name must be at least 3 characters long")
        return value.strip()

    def validate_description(self, value):
        """
        Validate product description.
        
        Args:
            value: Product description to validate
        
        Returns:
            str: Validated description
        
        Raises:
            serializers.ValidationError: If description is empty
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Product description cannot be empty")
        return value.strip()

    def validate_price(self, value):
        """
        Validate product price.
        
        Args:
            value: Product price to validate
        
        Returns:
            decimal.Decimal: Validated price
        
        Raises:
            serializers.ValidationError: If price is negative
        """
        if value < 0:
            raise serializers.ValidationError("Product price cannot be negative")
        return value

    def validate_store_id(self, value):
        """
        Validate store ID and check ownership.
        
        Args:
            value: Store ID to validate
        
        Returns:
            int: Validated store ID
        
        Raises:
            serializers.ValidationError: If store doesn't exist or user doesn't own it
        """
        try:
            store = Store.objects.get(id=value)
            request = self.context.get('request')
            if request and request.user != store.vendor:
                raise serializers.ValidationError(
                    "You can only add products to your own stores"
                )
        except Store.DoesNotExist:
            raise serializers.ValidationError("Store does not exist")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for Review model.
    
    Includes nested user and product information.
    """
    user = UserSerializer(read_only=True)
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Review
        fields = ['id', 'product', 'product_id', 'user', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_rating(self, value):
        """
        Validate rating value.
        
        Args:
            value: Rating value to validate
        
        Returns:
            int: Validated rating
        
        Raises:
            serializers.ValidationError: If rating is not between 1 and 5
        """
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value

    def validate_comment(self, value):
        """
        Validate review comment.
        
        Args:
            value: Comment text to validate
        
        Returns:
            str: Validated comment
        
        Raises:
            serializers.ValidationError: If comment is empty
        """
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("Review comment cannot be empty")
        return value.strip()

    def create(self, validated_data):
        """
        Create a new review instance.
        
        Args:
            validated_data: Validated review data
        
        Returns:
            Review: Created review instance
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


