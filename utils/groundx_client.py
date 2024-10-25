from typing import Dict, Any
from groundx import Groundx
from config import config  
import logging

class GroundxClient:
    """
    A wrapper client for interacting with the GroundX API.
    """
    
    def __init__(self) -> None:
        """Initialize the GroundX client with API key from config."""
        self.logger = logging.getLogger(__name__)
        self.client = Groundx(api_key=config.GROUNDX_API_KEY)  
    
    def create_bucket(self, document_name: str) -> str:
        """Create a new bucket for document storage."""
        response = self.client.buckets.create(name=document_name)
        return response.body['bucket']['bucketId']
    
    def get_processing_status(self, process_id: str) -> Dict[str, Any]:
        """Get the current status of a document processing job."""
        return self.client.documents.get_processing_status_by_id(process_id=process_id)
    
    def search_content(self, bucket_id: str, query: str) -> str:
        """Search for content within a specific bucket."""
        response = self.client.search.content(id=bucket_id, query=query)
        return response.body['search']['text']
