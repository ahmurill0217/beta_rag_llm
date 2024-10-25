from openai import OpenAI
from config import config  
import logging

class OpenAIClient:
    """
    A wrapper client for interacting with the OpenAI API.
    """
    
    def __init__(self) -> None:
        """Initialize the OpenAI client with API key from config."""
        self.logger = logging.getLogger(__name__)
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)  
    
    def generate_completion(self, messages: list) -> str:
        """Generate a completion using the OpenAI chat model."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error generating completion: {e}", exc_info=True)
            raise