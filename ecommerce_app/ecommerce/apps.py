"""
Ecommerce app configuration.
"""
from django.apps import AppConfig


class EcommerceConfig(AppConfig):
    """Configuration for the ecommerce app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ecommerce'

    def ready(self):
        """
        Initialize Tweet singleton when app is ready.
        This ensures the Twitter API connection is established at startup.
        """
        from .functions.tweet import Tweet
        # Initialize singleton instance
        Tweet()


