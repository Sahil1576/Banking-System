import psycopg2
import os

def get_connection():
    DATABASE_URL = None

    # Streamlit Cloud
    try:
        import streamlit as st
        if "DATABASE_URL" in st.secrets:
            DATABASE_URL = st.secrets["DATABASE_URL"]
    except:
        pass

    # Local fallback
    if not DATABASE_URL:
        DATABASE_URL = os.getenv("DATABASE_URL")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found")

    return psycopg2.connect(DATABASE_URL)