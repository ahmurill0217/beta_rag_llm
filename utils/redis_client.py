import redis
import json
import hashlib
from typing import Optional, Any, Dict
import logging
from config import config

class RedisClient:
    """
    Redis client wrapper for caching query results.
    """
    
    def __init__(self) -> None:
        """Initialize Redis connection using configuration."""
        self.logger = logging.getLogger(__name__)
        try:
            self.client = redis.Redis(
                host=config.REDIS_HOST,
                port=config.REDIS_PORT,
                password=config.REDIS_PASSWORD,
                decode_responses=True
            )
            self.client.ping()  # Test connection
            self.logger.info("Redis connection established")
        except Exception as e:
            self.logger.error(f"Redis connection failed: {e}")
            self.client = None
    
    @staticmethod
    def get_cache_key(query: str) -> str:
        """Create a unique key based on the query."""
        return hashlib.md5(query.encode()).hexdigest()
    
    def get_cached_result(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached result for a query.
        
        Args:
            query: The query string to look up
            
        Returns:
            Cached result if found, None otherwise
        """
        if not self.client:
            return None
            
        try:
            cache_key = self.get_cache_key(query)
            cached_result = self.client.get(cache_key)
            
            if cached_result:
                self.logger.info("Cache hit")
                return json.loads(cached_result)
            
            self.logger.info("Cache miss")
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set_cached_result(self, query: str, result: Dict[str, Any], 
                         expiration_time: int = 3600) -> bool:
        """
        Cache a query result.
        
        Args:
            query: The query string to cache
            result: The result to cache
            expiration_time: Time in seconds until cache expires
            
        Returns:
            True if caching successful, False otherwise
        """
        if not self.client:
            return False
            
        try:
            cache_key = self.get_cache_key(query)
            self.client.setex(
                cache_key,
                expiration_time,
                json.dumps(result)
            )
            self.logger.info(f"Cached result for query with key: {cache_key}")
            return True
        except Exception as e:
            self.logger.error(f"Error caching result: {e}")
            return False