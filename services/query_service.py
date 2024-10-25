from typing import Dict, Any, Optional, List
from utils.groundx_client import GroundxClient
from utils.openai_client import OpenAIClient
from utils.redis_client import RedisClient
from config import config
import logging

class QueryService:
    """Service for handling document queries with caching."""
    
    def __init__(self) -> None:
        """Initialize the service with required clients."""
        self.groundx_client = GroundxClient()
        self.openai_client = OpenAIClient()
        self.redis_client = RedisClient()
        self.logger = logging.getLogger(__name__)
    
    def process_query(self, bucket_id: str, query: str) -> str:
        """
        Process a user query with caching support.
        
        Args:
            bucket_id: ID of the bucket to search in
            query: User's query string
            
        Returns:
            Generated response or cached response
        """
        # Create a cache key that includes the bucket_id
        cache_query = f"{bucket_id}:{query}"
        
        # Check cache first
        cached_result = self.redis_client.get_cached_result(cache_query)
        if cached_result:
            self.logger.info("Returning cached response")
            return cached_result.get('response', '')
        
        try:
            # Perform the search
            context = self.groundx_client.search_content(bucket_id, query)
            
            if not context:
                return "No relevant content found for your query."
            
            # Truncate if needed
            if len(context) > 4000 * 3:
                context = context[:4000*3]
            
            # Generate response
            messages = self._create_prompt(context, query)
            response = self.openai_client.generate_completion(messages)
            
            # Cache the result
            result_to_cache = {
                'response': response,
                'context': context,
                'bucket_id': bucket_id
            }
            
            self.redis_client.set_cached_result(
                cache_query,
                result_to_cache,
                expiration_time=config.CACHE_EXPIRATION
            )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return f"An error occurred: {str(e)}"
    
    def _create_prompt(self, context: str, query: str) -> List[Dict[str, str]]:
        """Create the prompt for the LLM."""
        system_prompt = 'You are a helpful AI agent tasked with helping users extract information from the context below'
        return [
            {"role": "system", "content": f"{system_prompt}\n\n===\n{context}\n==="},
            {"role": "user", "content": query}
        ]
