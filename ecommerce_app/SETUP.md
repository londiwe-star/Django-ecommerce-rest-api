# Quick Setup Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Twitter Developer Account (for Twitter integration)

## Step-by-Step Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `env.example` to `.env`:

```bash
# Windows
copy env.example .env

# Linux/Mac
cp env.example .env
```

Edit `.env` and add your values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Twitter API Credentials (optional - app works without them)
TWITTER_CONSUMER_KEY=your-consumer-key
TWITTER_CONSUMER_SECRET=your-consumer-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
```

**Note:** You can generate a Django secret key using:
```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Testing the API

### Create a Test User

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
user = User.objects.create_user('vendor1', 'vendor1@test.com', 'testpass123')
user.save()
```

### Test with cURL

```bash
# List stores (public)
curl http://localhost:8000/api/stores/

# Create store (authenticated)
curl -X POST http://localhost:8000/api/stores/ \
  -u vendor1:testpass123 \
  -H "Content-Type: application/json" \
  -d '{"name": "My Store", "description": "A great store"}'
```

### Test with Postman

1. Import `postman_collection.json` into Postman
2. Update environment variables in Postman:
   - `base_url`: `http://localhost:8000/api`
   - `username`: Your username
   - `password`: Your password
3. Start making requests!

## Running Tests

```bash
python manage.py test ecommerce
```

## Troubleshooting

### Issue: ModuleNotFoundError

**Solution:** Make sure you've activated your virtual environment and installed all dependencies.

### Issue: Twitter API errors

**Solution:** The app works without Twitter credentials. If you want Twitter integration:
1. Sign up at https://developer.twitter.com
2. Create an app
3. Generate API keys and tokens
4. Add them to `.env`

### Issue: Database errors

**Solution:** Make sure you've run migrations:
```bash
python manage.py migrate
```

### Issue: Permission denied errors

**Solution:** Make sure you're authenticated and own the resource you're trying to modify.

## Next Steps

- Read the full [README.md](README.md) for detailed API documentation
- Check out the [Postman collection](postman_collection.json) for API examples
- Review [sequence diagrams](sequence_diagrams.puml) for architecture understanding


