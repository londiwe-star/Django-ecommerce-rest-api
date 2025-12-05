"""
API views for ecommerce application with RESTful endpoints.
"""
import logging
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import Store, Product, Review
from .serializers import StoreSerializer, ProductSerializer, ReviewSerializer
from .functions.tweet import Tweet

logger = logging.getLogger(__name__)


# ==================== ROOT VIEW ====================

def api_root(request):
    """
    Root API endpoint that provides API information and available endpoints.
    
    GET /
    No authentication required
    """
    api_info = {
        'name': 'Django eCommerce RESTful API',
        'version': '1.0.0',
        'description': 'A complete Django eCommerce RESTful API with Twitter/X integration',
        'base_url': '/api/',
        'endpoints': {
            'public': {
                'stores': {
                    'list': 'GET /api/stores/',
                    'detail': 'GET /api/stores/{id}/',
                    'products': 'GET /api/stores/{store_id}/products/',
                },
                'products': {
                    'detail': 'GET /api/products/{id}/',
                },
                'vendors': {
                    'stores': 'GET /api/vendors/{vendor_id}/stores/',
                },
            },
            'authenticated': {
                'stores': {
                    'create': 'POST /api/stores/',
                    'update': 'PUT /api/stores/{id}/',
                    'delete': 'DELETE /api/stores/{id}/',
                    'reviews': 'GET /api/stores/{store_id}/reviews/',
                },
                'products': {
                    'create': 'POST /api/stores/{store_id}/products/',
                    'update': 'PUT /api/products/{id}/',
                    'delete': 'DELETE /api/products/{id}/',
                },
            },
        },
        'authentication': {
            'type': 'Basic Authentication',
            'header': 'Authorization: Basic <base64(username:password)>',
        },
        'formats': ['JSON', 'XML'],
        'documentation': {
            'readme': 'See README.md for full documentation',
            'postman': 'Import postman_collection.json for API examples',
        },
    }
    return JsonResponse(api_info, json_dumps_params={'indent': 2})


# ==================== VENDOR ENDPOINTS (Authenticated) ====================



@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
def store_detail(request, store_id):
    """
    Get, update, or delete a store.
    
    GET /api/stores/{id}/ - Get store details (Public)
    PUT /api/stores/{id}/ - Update store (Authenticated, must own)
    DELETE /api/stores/{id}/ - Delete store (Authenticated, must own)
    """
    try:
        store = get_object_or_404(Store, id=store_id)
        
        if request.method == 'GET':
            # Public endpoint - no auth required
            serializer = StoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # Check authentication
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check ownership
            if store.vendor != request.user:
                return Response(
                    {'error': 'You do not have permission to update this store'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = StoreSerializer(store, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:  # DELETE
            # Check authentication
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check ownership
            if store.vendor != request.user:
                return Response(
                    {'error': 'You do not have permission to delete this store'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            store.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
    except Store.DoesNotExist:
        return Response(
            {'error': 'Store not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error with store operation: {str(e)}")
        return Response(
            {'error': 'Operation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
def store_products(request, store_id):
    """
    Get all products in a store (GET) or add a product to a store (POST).
    
    GET /api/stores/{store_id}/products/ - List all products (Public)
    POST /api/stores/{store_id}/products/ - Add product (Authenticated, must own store)
    """
    try:
        store = get_object_or_404(Store, id=store_id)
        
        if request.method == 'GET':
            # Public endpoint
            products = store.products.all()
            serializer = ProductSerializer(products, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        else:  # POST
            # Check authentication
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check ownership
            if store.vendor != request.user:
                return Response(
                    {'error': 'You do not have permission to add products to this store'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Add store_id to request data
            data = request.data.copy()
            data['store_id'] = store_id
            
            serializer = ProductSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                product = serializer.save()
                
                # Trigger tweet for new product
                try:
                    tweet = Tweet()
                    tweet_text = (
                        f"🛍️ New Product Alert!\n\n"
                        f"🏪 Store: {store.name}\n"
                        f"📦 Product: {product.name}\n"
                        f"💰 Price: ${product.price}\n\n"
                        f"📝 {product.description[:150]}{'...' if len(product.description) > 150 else ''}\n\n"
                        f"#eCommerce #NewProduct #Shopping"
                    )
                    tweet.make_tweet({'text': tweet_text})
                except Exception as e:
                    logger.error(f"Failed to post tweet for new product: {str(e)}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Store.DoesNotExist:
        return Response(
            {'error': 'Store not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error with store products: {str(e)}")
        return Response(
            {'error': 'Operation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
def product_detail(request, product_id):
    """
    Get, update, or delete a product.
    
    GET /api/products/{id}/ - Get product details (Public)
    PUT /api/products/{id}/ - Update product (Authenticated, must own store)
    DELETE /api/products/{id}/ - Delete product (Authenticated, must own store)
    """
    try:
        product = get_object_or_404(Product, id=product_id)
        
        if request.method == 'GET':
            # Public endpoint
            serializer = ProductSerializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'PUT':
            # Check authentication
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check ownership
            if product.store.vendor != request.user:
                return Response(
                    {'error': 'You do not have permission to update this product'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:  # DELETE
            # Check authentication
            if not request.user.is_authenticated:
                return Response(
                    {'error': 'Authentication required'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Check ownership
            if product.store.vendor != request.user:
                return Response(
                    {'error': 'You do not have permission to delete this product'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            product.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
    except Product.DoesNotExist:
        return Response(
            {'error': 'Product not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error with product operation: {str(e)}")
        return Response(
            {'error': 'Operation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )




@api_view(['GET'])
@authentication_classes([BasicAuthentication])
@permission_classes([IsAuthenticated])
def get_vendor_store_reviews(request, store_id):
    """
    Get all reviews for a vendor's store (Vendor only, must own the store).
    
    GET /api/stores/{store_id}/reviews/
    Requires: Basic Authentication, Store ownership
    """
    try:
        store = get_object_or_404(Store, id=store_id)
        
        # Check ownership
        if store.vendor != request.user:
            return Response(
                {'error': 'You do not have permission to view reviews for this store'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all products in the store
        products = store.products.all()
        reviews = Review.objects.filter(product__in=products)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"Error fetching store reviews: {str(e)}")
        return Response(
            {'error': 'Failed to fetch reviews'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ==================== PUBLIC ENDPOINTS (No auth required) ====================

@api_view(['GET', 'POST'])
@authentication_classes([BasicAuthentication])
@permission_classes([AllowAny])
def stores_list_create(request):
    """
    List all stores (GET) or create a new store (POST).
    
    GET /api/stores/ - List all stores (Public)
    POST /api/stores/ - Create new store (Authenticated)
    """
    if request.method == 'GET':
        try:
            stores = Store.objects.all()
            serializer = StoreSerializer(stores, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error listing stores: {str(e)}")
            return Response(
                {'error': 'Failed to list stores'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    else:  # POST
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        try:
            serializer = StoreSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                store = serializer.save()
                
                # Trigger tweet for new store
                try:
                    tweet = Tweet()
                    tweet_text = (
                        f"🏪 New Store Alert!\n\n"
                        f"📛 {store.name}\n\n"
                        f"📝 {store.description[:200]}{'...' if len(store.description) > 200 else ''}\n\n"
                        f"#eCommerce #NewStore"
                    )
                    tweet.make_tweet({'text': tweet_text})
                except Exception as e:
                    logger.error(f"Failed to post tweet for new store: {str(e)}")
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating store: {str(e)}")
            return Response(
                {'error': 'Failed to create store'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )




@api_view(['GET'])
@permission_classes([AllowAny])
def get_vendor_stores(request, vendor_id):
    """
    Get all stores for a vendor (Public endpoint).
    
    GET /api/vendors/{vendor_id}/stores/
    No authentication required
    """
    try:
        vendor = get_object_or_404(User, id=vendor_id)
        stores = Store.objects.filter(vendor=vendor)
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response(
            {'error': 'Vendor not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error fetching vendor stores: {str(e)}")
        return Response(
            {'error': 'Failed to fetch vendor stores'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )





