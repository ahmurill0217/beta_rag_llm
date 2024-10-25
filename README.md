# RAG LLM Beta Application

A Streamlit application that implements RAG (Retrieval-Augmented Generation) using Eye Level and OpenAI APIs.

## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file for local development
   - Configure secrets in Streamlit Cloud for deployment

## Environment Variables

Required environment variables:
- `EYE_LEVEL_API_KEY`: Your Eye Level API key
- `OPENAI_API_KEY`: Your OpenAI API key

## Running Locally

```bash
streamlit run app.py
```
