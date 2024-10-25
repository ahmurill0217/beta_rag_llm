from typing import Callable, Dict, Optional, Any
import streamlit as st

class DocumentUploadComponent:
    """Component for handling document uploads in the Streamlit UI."""
    
    @staticmethod
    def render(on_process_callback: Callable[[Any], None]) -> None:
        """
        Render the document upload interface.
        
        Args:
            on_process_callback: Callback function to handle document processing
        """
        uploaded_file = st.file_uploader("Choose a document", type=["pdf"])
        if uploaded_file is not None:
            st.write("Document uploaded successfully!")
            if st.button("Process Document"):
                on_process_callback(uploaded_file)

class DocumentSelectionComponent:
    """Component for document selection in the Streamlit UI."""
    
    @staticmethod
    def render(documents: Dict[str, Dict[str, Any]], 
               parsing_status: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Render the document selection interface.
        
        Args:
            documents: Dictionary of available documents and their info
            parsing_status: Current parsing status if any
            
        Returns:
            Selected document's information or None if no selection
        """
        st.subheader("Select a document to query")
        if not documents:
            st.info("No documents available. Please upload and process a document first.")
            return None
            
        selected_document = st.selectbox("Choose a document", list(documents.keys()), index=0)
        selected_bucket_info = documents.get(selected_document)
        
        if selected_bucket_info['status'] == 'processing':
            st.info(f"Currently processing: {selected_document}")
            st.info(f"Parsing status: {parsing_status}")
        elif selected_bucket_info['status'] == 'complete':
            st.success(f"Document ready: {selected_document}")
            
        return selected_bucket_info
