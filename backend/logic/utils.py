import streamlit as st
from sqlalchemy import create_engine
import pandas as pd
import requests
import os
import bcrypt

# --- PATHS ---
# This robust pathing ensures files are found from any script in the 'pages' folder
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT_DIR, 'university.db')
DB_URI = f'sqlite:///{DB_PATH}'

# --- DATABASE & API ---
@st.cache_resource
def get_db_engine():
    """Returns a cached SQLAlchemy engine instance."""
    return create_engine(DB_URI)

@st.cache_data(ttl=300)
def load_data_from_api():
    """
    Fetches all student data from the FastAPI backend's /students endpoint.
    """
    backend_url = "http://127.0.0.1:8000/students"
    try:
        response = requests.get(backend_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data)
        else:
            st.error(f"Failed to fetch student data from API. Status: {response.status_code}")
            return pd.DataFrame() # Return empty DF on error
    except requests.exceptions.ConnectionError:
        st.error("Connection Error: Could not connect to the backend to fetch student data.")
        return pd.DataFrame() # Return empty DF on error

def load_data_from_db(engine):
    """Loads data directly from the database (used by backend scripts)."""
    try:
        df = pd.read_sql('students', engine)
        return df
    except Exception:
        return None

# --- AUTHENTICATION ---
def hash_password(password):
    """Hashes a password for storing."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Verifies a plain password against a hashed one."""
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password)

# --- STYLING ---
def load_css(file_path):
    """Loads a CSS file into the Streamlit app using a robust path."""
    abs_path = os.path.join(ROOT_DIR, file_path)
    try:
        with open(abs_path) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"CSS file not found at: {abs_path}. Using default styling.")
