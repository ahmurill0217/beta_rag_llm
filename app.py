import streamlit as st
from groundx import Groundx
import json
import os
import tempfile
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Input API Keys
GROUNDX_API_KEY = os.getenv("EYE_LEVEL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize groundx client
groundx = Groundx(api_key=GROUNDX_API_KEY)

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize session state for storing bucket information and processing status
if 'buckets' not in st.session_state:
    st.session_state.buckets = {}
if 'processing' not in st.session_state:
    st.session_state.processing = False
if 'current_document' not in st.session_state:
    st.session_state.current_document = None
if 'parsing_status' not in st.session_state:
    st.session_state.parsing_status = None

def create_bucket(document_name):
    response = groundx.buckets.create(
        name=document_name
    )
    bucket_id = response.body['bucket']['bucketId']
    return bucket_id

def upload_and_parse_document(bucket_id, uploaded_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        response = groundx.documents.ingest_local([{
            "blob": open(tmp_file_path, "rb"),
            "metadata": {
                "bucketId": bucket_id,
                "fileName": uploaded_file.name,
                "fileType": "pdf",
            }
        }])
        process_id = response.body['ingest']['processId']
        return process_id
    finally:
        os.unlink(tmp_file_path)

def check_parsing_status(process_id):
    while True:
        response = groundx.documents.get_processing_status_by_id(
            process_id=process_id
        )
        status = response.body['ingest']['status']
        st.session_state.parsing_status = status  # Store the current status
        if status == 'complete':
            doc_id = response.body['ingest']['progress']['complete']['documents'][0]['documentId']
            return 'complete', doc_id
        elif status == 'failed':
            return 'failed', None
        time.sleep(5)
        yield status
 

def gx_search(bucket_id, query):
    response = groundx.search.content(
        id=bucket_id,
        query=query
    )
    return response.body['search']['text']

def gx_retrieve_and_augment(bucket_id, query):
    context = gx_search(bucket_id, query)
    if len(context) > 4000 * 3:
        context = context[:4000*3]
    system_prompt = 'You are a helpful AI agent tasked with helping users extract information from the context below'
    augmented_prompt = [
        {"role": "system", "content": system_prompt + '\n\n===\n' + context + '\n==='},
        {"role": "user", "content": query}
    ]
    return augmented_prompt

def gxrag(bucket_id, query):
    augmented_prompt = gx_retrieve_and_augment(bucket_id, query)
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=augmented_prompt
    )
    return response.choices[0].message.content

def process_document(uploaded_file):
    st.session_state.processing = True
    st.session_state.current_document = uploaded_file.name
    st.session_state.parsing_status = 'starting'
    
    bucket_id = create_bucket(uploaded_file.name)
    st.success(f"Created bucket {bucket_id}")
    
    process_id = upload_and_parse_document(bucket_id, uploaded_file)
    st.success(f"Document uploaded. Process ID: {process_id}")
    
    st.session_state.buckets[uploaded_file.name] = {'id': bucket_id, 'status': 'processing'}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    while True:
        response = groundx.documents.get_processing_status_by_id(process_id=process_id)
        status = response.body['ingest']['status']
        st.session_state.parsing_status = status
        
        if status == 'complete':
            progress_bar.progress(100)
            status_text.text("Parsing complete!")
            st.session_state.buckets[uploaded_file.name]['status'] = 'complete'
            st.session_state.processing = False
            break
        elif status == 'failed':
            status_text.text("Parsing failed. Please try again.")
            st.session_state.processing = False
            del st.session_state.buckets[uploaded_file.name]
            break
        else:
            progress_bar.progress(50)
            status_text.text(f"Parsing status: {status}")
        
        time.sleep(5)
    
    st.rerun()
       
        
st.title("Eye Level RAG LLM Application")

# Document upload section
uploaded_file = st.file_uploader("Choose a document", type=["pdf"])
if uploaded_file is not None:
    st.write("Document uploaded successfully!")
    if st.button("Process Document"):
        process_document(uploaded_file)

# Document selection section
st.subheader("Select a document to query")
document_options = list(st.session_state.buckets.keys())
if document_options:
    selected_document = st.selectbox("Choose a document", document_options, index=0)
    selected_bucket_info = st.session_state.buckets.get(selected_document)
    if selected_bucket_info['status'] == 'processing':
        st.info(f"Currently processing: {selected_document}")
        st.info(f"Parsing status: {st.session_state.parsing_status}")
    elif selected_bucket_info['status'] == 'complete':
        st.success(f"Document ready: {selected_document}")
else:
    st.info("No documents available. Please upload and process a document first.")

# Query section
query = st.text_input("Enter your query:")
if query and selected_bucket_info and selected_bucket_info['status'] == 'complete':
    if st.button("Generate Response"):
        with st.spinner("Generating response..."):
            response = gxrag(selected_bucket_info['id'], query)
            st.write("LLM Response:")
            st.write(response)
elif query and selected_bucket_info and selected_bucket_info['status'] == 'processing':
    st.warning("Please wait for document processing to complete before querying.")
elif query:
    st.warning("Please select a document before querying.")

# Display overall processing status
if st.session_state.processing:
    st.info("A document is currently being processed. You can see its status in the document selection area.")
else:
    st.success("All documents are processed and ready for querying.")
