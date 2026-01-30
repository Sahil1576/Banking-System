import psycopg2
import os
import streamlit as st

def get_connection():
    DATABASE_URL = st.secrets["DATABASE_URL"]
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable not set")
    return psycopg2.connect(
        DATABASE_URL
)

if __name__ == "__main__":
    print("Database connected successfully")