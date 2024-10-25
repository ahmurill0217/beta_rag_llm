import os
import sys
import time
import streamlit as st
from services.document_service import DocumentService
from services.query_service import QueryService
from ui.components import DocumentUploadComponent, DocumentSelectionComponent
import logging
from config import config 

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Log to console
        logging.StreamHandler(),
        # Also log to a file
        logging.FileHandler('app.log')
    ]
)

# Create a logger for this file
logger = logging.getLogger(__name__)
logger.info("Starting Eye Level RAG LLM Application")

class EyeLevelApp:
    def __init__(self):
        self.document_service = DocumentService()
        self.query_service = QueryService()
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        if 'buckets' not in st.session_state:
            st.session_state.buckets = {}
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'current_document' not in st.session_state:
            st.session_state.current_document = None
        if 'parsing_status' not in st.session_state:
            st.session_state.parsing_status = None
    
    def _handle_query_section(self, selected_bucket_info):
        """
        Handle the query input section and response generation.
        
        Args:
            selected_bucket_info: Information about the selected document/bucket
        """
        query = st.text_input("Enter your query:")
        
        if query:
            if not selected_bucket_info:
                st.warning("Please select a document before querying.")
            elif selected_bucket_info['status'] == 'processing':
                st.warning("Please wait for document processing to complete before querying.")
            elif selected_bucket_info['status'] == 'complete':
                if st.button("Generate Response"):
                    with st.spinner("Generating response..."):
                        response = self.query_service.process_query(
                            selected_bucket_info['id'], 
                            query
                        )
                        st.write("LLM Response:")
                        st.write(response)
    
    def _display_processing_status(self):
        """Display the overall processing status of documents."""
        if st.session_state.processing:
            st.info("A document is currently being processed. You can see its status in the document selection area.")
        else:
            st.success("All documents are processed and ready for querying.")
    
    def process_document(self, uploaded_file):
        """Process an uploaded document."""
        st.session_state.processing = True
        st.session_state.current_document = uploaded_file.name
        st.session_state.parsing_status = 'starting'
        
        bucket_id, process_id = self.document_service.process_document(uploaded_file)
        st.success(f"Created bucket {bucket_id}")
        
        self._monitor_processing(uploaded_file.name, bucket_id, process_id)
    
    def _monitor_processing(self, file_name, bucket_id, process_id):
        """Monitor the processing status of a document."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        st.session_state.buckets[file_name] = {'id': bucket_id, 'status': 'processing'}
        
        while True:
            response = self.document_service.check_processing_status(process_id)
            status = response.body['ingest']['status']
            st.session_state.parsing_status = status
            
            if status == 'complete':
                progress_bar.progress(100)
                status_text.text("Parsing complete!")
                st.session_state.buckets[file_name]['status'] = 'complete'
                st.session_state.processing = False
                break
            elif status == 'failed':
                status_text.text("Parsing failed. Please try again.")
                st.session_state.processing = False
                del st.session_state.buckets[file_name]
                break
            else:
                progress_bar.progress(50)
                status_text.text(f"Parsing status: {status}")
            
            time.sleep(5)
        
        st.rerun()
    
    def run(self):
        """Run the main application."""
        st.title("RAG LLM Beta Application")
        
        # Document upload section
        DocumentUploadComponent.render(self.process_document)
        
        # Document selection section
        selected_bucket_info = DocumentSelectionComponent.render(
            st.session_state.buckets,
            st.session_state.parsing_status
        )
        
        # Query section
        self._handle_query_section(selected_bucket_info)
        
        # Display processing status
        self._display_processing_status()

if __name__ == "__main__":
    app = EyeLevelApp()
    app.run()