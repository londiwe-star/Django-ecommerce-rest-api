"""
Twitter/X API integration using Singleton pattern.
"""
import logging
from requests_oauthlib import OAuth1Session
from django.conf import settings

logger = logging.getLogger(__name__)


class Tweet:
    """
    Singleton class for Twitter/X API integration.
    
    This class handles OAuth1 authentication and posting tweets.
    Only one instance of this class should exist throughout the application.
    
    Attributes:
        _instance: Class variable storing the singleton instance
        consumer_key: Twitter API consumer key
        consumer_secret: Twitter API consumer secret
        access_token: Twitter API access token
        access_token_secret: Twitter API access token secret
        oauth: OAuth1Session instance for making authenticated requests
    """
    _instance = None
    CONSUMER_KEY = None
    CONSUMER_SECRET = None
    ACCESS_TOKEN = None
    ACCESS_TOKEN_SECRET = None

    def __new__(cls):
        """
        Create or return the singleton instance.
        
        Returns:
            Tweet: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super(Tweet, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """
        Initialize the singleton instance with Twitter API credentials.
        Only initializes once even if called multiple times.
        """
        if self._initialized:
            return

        # Load credentials from settings
        self.CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
        self.CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET
        self.ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
        self.ACCESS_TOKEN_SECRET = settings.TWITTER_ACCESS_TOKEN_SECRET

        self.oauth = None
        self._initialized = True

        # Authenticate if credentials are available
        if self.CONSUMER_KEY and self.CONSUMER_SECRET:
            self.authenticate()

    def authenticate(self):
        """
        Authenticate with Twitter API using OAuth1.
        
        Creates an OAuth1Session instance for making authenticated requests.
        Handles authentication errors gracefully.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            if not all([self.CONSUMER_KEY, self.CONSUMER_SECRET,
                       self.ACCESS_TOKEN, self.ACCESS_TOKEN_SECRET]):
                logger.warning("Twitter API credentials not fully configured")
                return False

            self.oauth = OAuth1Session(
                self.CONSUMER_KEY,
                client_secret=self.CONSUMER_SECRET,
                resource_owner_key=self.ACCESS_TOKEN,
                resource_owner_secret=self.ACCESS_TOKEN_SECRET
            )
            logger.info("Twitter API authentication successful")
            return True
        except Exception as e:
            logger.error(f"Twitter API authentication failed: {str(e)}")
            self.oauth = None
            return False

    def make_tweet(self, tweet_dict):
        """
        Post a tweet to Twitter/X.
        
        Args:
            tweet_dict (dict): Dictionary containing tweet data
                - text (str): Tweet text content
                - media_ids (list, optional): List of media IDs to attach
        
        Returns:
            dict: Response from Twitter API if successful, None otherwise
        
        Raises:
            Exception: If authentication is not set up or API call fails
        """
        if not self.oauth:
            logger.warning("Twitter API not authenticated. Skipping tweet.")
            return None

        try:
            url = "https://api.twitter.com/2/tweets"
            
            payload = {
                "text": tweet_dict.get('text', '')
            }

            # Add media if provided
            if 'media_ids' in tweet_dict:
                payload['media'] = {
                    "media_ids": tweet_dict['media_ids']
                }

            response = self.oauth.post(url, json=payload)
            
            if response.status_code == 201:
                logger.info(f"Tweet posted successfully: {response.json()}")
                return response.json()
            else:
                logger.error(f"Failed to post tweet. Status: {response.status_code}, "
                           f"Response: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error posting tweet: {str(e)}")
            return None


