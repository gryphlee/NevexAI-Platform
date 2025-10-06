import streamlit as st
import requests

def check_login_api(username, password):
    """Calls the backend API to verify credentials and set session state."""
    backend_url = "http://127.0.0.1:8000/token"
    login_data = {'username': username, 'password': password}
    
    try:
        response = requests.post(backend_url, data=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            parts = access_token.split(':')
            if len(parts) == 3:
                user, role, student_id_str = parts
                st.session_state['logged_in'] = True
                st.session_state['role'] = role
                st.session_state['username'] = username
                st.session_state['student_id'] = student_id_str if student_id_str and student_id_str != 'None' else None
                return True
        elif response.status_code == 401:
            st.error("Invalid username or password.")
            return False
    except requests.exceptions.RequestException:
        st.error("Connection Error: Could not connect to the backend server.")
        return False
    return False

@st.dialog("User Login")
def login_dialog():
    """A dialog box for the login form."""
    with st.form("login_form_dialog"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Login", type="primary"):
            if check_login_api(username, password):
                st.rerun()