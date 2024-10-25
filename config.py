import os
from dotenv import load_dotenv
from typing import Optional

class Config:
    """Configuration management for both local and Streamlit deployment"""
    
    # Load .env file for local development
    load_dotenv()

    def __init__(self):
        """Initialize configuration values"""
        # API Keys
        self.GROUNDX_API_KEY = self._get_env_var("EYE_LEVEL_API_KEY")
        self.OPENAI_API_KEY = self._get_env_var("OPENAI_API_KEY")
        
        # Redis Configuration
        self.REDIS_HOST = self._get_env_var("REDIS_HOST")
        self.REDIS_PORT = int(self._get_env_var("REDIS_PORT", "13600"))
        self.REDIS_PASSWORD = self._get_env_var("REDIS_PASSWORD")
        self.CACHE_EXPIRATION = int(self._get_env_var("CACHE_EXPIRATION", "3600"))

    def _get_env_var(self, key: str, default: Optional[str] = None) -> str:
        """Get an environment variable with optional Streamlit secrets fallback."""
        try:
            # Try getting from Streamlit secrets first
            import streamlit as st
            value = st.secrets.get(key)
            if value is not None:
                return value
        except:
            pass
        
        # Try getting from environment
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Required configuration '{key}' not found in environment or secrets")
        return value

# Create and export the singleton instance
config = Config()

# Export the instance for other modules to import
__all__ = ['config']