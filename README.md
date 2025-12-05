# Django eCommerce RESTful API

A complete Django eCommerce RESTful API extension with Twitter/X integration, following REST architecture principles with proper authentication, serialization, and third-party API integration.

## Features

- ✅ Full RESTful API with Django REST Framework
- ✅ JSON and XML response format support
- ✅ Basic Authentication for protected endpoints
- ✅ Store, Product, and Review management
- ✅ Twitter/X API integration with automatic tweets
- ✅ Comprehensive error handling
- ✅ Production-ready code with proper validation

## Project Structure

```
ecommerce_app/
├── ecommerce_project/          # Django project settings
│   ├── settings.py              # Project configuration
│   ├── urls.py                  # Main URL configuration
│   └── wsgi.py                  # WSGI configuration
├── ecommerce/                   # Main ecommerce app
│   ├── models.py                # Store, Product, Review models
│   ├── serializers.py           # DRF serializers
│   ├── views.py                 # API views
│   ├── urls.py                  # API endpoints
│   ├── admin.py                 # Admin configuration
│   ├── tests.py                 # Test cases
│   ├── apps.py                  # App configuration
│   └── functions/
│       └── tweet.py             # Twitter integration (Singleton)
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd ecommerce_app
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` and add:
- Django `SECRET_KEY`
- Twitter API credentials (Consumer Key, Consumer Secret, Access Token, Access Token Secret)

### 5. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create superuser (optional)

```bash
python manage.py createsuperuser
```

### 7. Run development server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## API Endpoints

### Public Endpoints (No Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stores/` | List all stores |
| GET | `/api/stores/{id}/` | Get store details |
| GET | `/api/vendors/{vendor_id}/stores/` | Get all stores for a vendor |
| GET | `/api/stores/{store_id}/products/` | Get all products in a store |
| GET | `/api/products/{id}/` | Get product details |

### Vendor Endpoints (Authentication Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/stores/` | Create new store |
| PUT | `/api/stores/{id}/` | Update store (must own) |
| DELETE | `/api/stores/{id}/` | Delete store (must own) |
| POST | `/api/stores/{store_id}/products/` | Add product to store (must own) |
| PUT | `/api/products/{id}/` | Update product (must own store) |
| DELETE | `/api/products/{id}/` | Delete product (must own store) |
| GET | `/api/stores/{store_id}/reviews/` | Get all reviews for vendor's stores |

## Authentication

The API uses **Basic Authentication**. Include credentials in the request header:

```
Authorization: Basic base64(username:password)
```

### Example with cURL

```bash
curl -X POST http://localhost:8000/api/stores/ \
  -H "Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Store", "description": "Store description"}'
```

### Example with Python requests

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.post(
    'http://localhost:8000/api/stores/',
    json={'name': 'My Store', 'description': 'Store description'},
    auth=HTTPBasicAuth('username', 'password')
)
```

## Response Formats

The API supports both JSON and XML formats. Specify the format using the `Accept` header:

- `Accept: application/json` (default)
- `Accept: application/xml`

## Models

### Store
- `vendor` (ForeignKey to User)
- `name` (CharField, max_length=200)
- `description` (TextField)
- `logo` (ImageField, optional)
- `created_at` (DateTimeField)

### Product
- `store` (ForeignKey to Store)
- `name` (CharField, max_length=200)
- `description` (TextField)
- `price` (DecimalField, max_digits=10, decimal_places=2)
- `image` (ImageField, optional)
- `created_at` (DateTimeField)

### Review
- `product` (ForeignKey to Product)
- `user` (ForeignKey to User)
- `rating` (IntegerField, choices=1-5)
- `comment` (TextField)
- `created_at` (DateTimeField)

## Twitter/X Integration

The application automatically posts tweets when:
- A new store is created
- A new product is added

Tweets are formatted with emojis and hashtags. The Twitter integration uses a Singleton pattern to ensure only one connection instance exists.

### Setting up Twitter API

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Create a new app
3. Generate API keys and access tokens
4. Add credentials to `.env` file

## Testing

Run the test suite:

```bash
python manage.py test ecommerce
```

## Postman Collection

See `postman_collection.json` for a complete Postman collection with all endpoints and example requests.

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful GET/PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## Security Considerations

- ✅ Never commit API keys (use environment variables)
- ✅ All user inputs are validated
- ✅ CSRF protection enabled
- ✅ Use HTTPS in production
- ✅ Ownership verification for all modifications

## Production Deployment

1. Set `DEBUG=False` in settings
2. Configure proper `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL recommended)
4. Set up proper static file serving
5. Use environment variables for all secrets
6. Enable HTTPS
7. Set up proper logging
8. Configure rate limiting

## License

This project is open source and available under the MIT License.

## Support

For issues and questions, please open an issue on the repository.


