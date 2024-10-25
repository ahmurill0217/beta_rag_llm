from typing import Tuple, Any, Dict
import tempfile
import os
from utils.groundx_client import GroundxClient
import logging

class DocumentService:
    """
    Service for handling document processing operations.
    """
    
    def __init__(self) -> None:
        """Initialize the document service with a GroundX client."""
        self.logger = logging.getLogger(__name__)
        self.groundx_client = GroundxClient()
    
    def process_document(self, uploaded_file: Any) -> Tuple[str, str]:
        """Process an uploaded document."""
        try:
            bucket_id = self.groundx_client.create_bucket(uploaded_file.name)
            process_id = self._upload_and_parse_document(bucket_id, uploaded_file)
            return bucket_id, process_id
        except Exception as e:
            self.logger.error(f"Error processing document: {e}", exc_info=True)
            raise
    
    def _upload_and_parse_document(self, bucket_id: str, uploaded_file: Any) -> str:
        """Internal method to handle document upload and parsing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_file_path = tmp_file.name

        try:
            response = self.groundx_client.client.documents.ingest_local([{
                "blob": open(tmp_file_path, "rb"),
                "metadata": {
                    "bucketId": bucket_id,
                    "fileName": uploaded_file.name,
                    "fileType": "pdf",
                }
            }])
            return response.body['ingest']['processId']
        finally:
            os.unlink(tmp_file_path)
    
    def check_processing_status(self, process_id: str) -> Dict[str, Any]:
        """Check the current status of a document processing job."""
        return self.groundx_client.get_processing_status(process_id)