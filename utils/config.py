import os
from dotenv import load_dotenv

# Load environment variables from .env file if available
load_dotenv()

def get_api_key(key_name: str) -> str:
    """
    Retrieve API key from system env, .env file, or Streamlit secrets.
    Ensures safe key management meeting assignment requirements.
    """
    val = os.getenv(key_name)
    if val:
        return val

    # Try Streamlit secrets if running inside Streamlit
    try:
        import streamlit as st
        if key_name in st.secrets:
            return st.secrets[key_name]
    except Exception:
        pass

    return ""
