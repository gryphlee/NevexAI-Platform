import streamlit as st
import pandas as pd
import requests

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") != "Admin":
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

st.title("👥 User Account Management")
st.markdown("Create, view, and manage user accounts for the system.")

BACKEND_URL = "http://127.0.0.1:8000"

# --- API Functions ---
@st.cache_data(ttl=10) # Cache user list for 10 seconds
def get_users_from_api():
    try:
        response = requests.get(f"{BACKEND_URL}/users")
        if response.status_code == 200:
            return pd.DataFrame(response.json())
    except requests.ConnectionError:
        st.error("Connection error. Could not connect to the backend.")
    return pd.DataFrame()

users_df = get_users_from_api()

# --- Form to Add New User ---
with st.expander("Create a New User Account", expanded=True):
    with st.form("new_user_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Student", "Teacher", "Parent", "Admin"])
        
        student_id_input = ""
        if role == "Student":
            student_id_input = st.text_input("Student ID (Required for Students)")

        submitted = st.form_submit_button("Create User")
        if submitted:
            if username and password:
                payload = {
                    "username": username,
                    "password": password,
                    "role": role,
                    "student_id": student_id_input if student_id_input else None
                }
                try:
                    response = requests.post(f"{BACKEND_URL}/users", json=payload)
                    if response.status_code == 200:
                        st.success(response.json().get('message'))
                        st.cache_data.clear() # Clear cache to refresh user list
                        st.rerun()
                    else:
                        st.error(f"Backend Error: {response.json().get('detail')}")
                except requests.ConnectionError:
                    st.error("Connection error. Could not create user.")
            else:
                st.warning("Username and Password are required.")

# --- Display and Manage Existing Users ---
st.divider()
st.subheader("Current User Accounts")

if users_df.empty:
    st.info("No users have been created yet, or the backend service is not running.")
else:
    cols = st.columns([2, 1, 1, 1])
    headers = ["Username", "Role", "Student ID", "Action"]
    for col, header in zip(cols, headers): col.markdown(f"**{header}**")

    for index, user in users_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        with col1: st.write(user['username'])
        with col2: st.write(user['role'])
        with col3: st.write(user['student_id'] if pd.notna(user.get('student_id')) else "N/A")
        with col4:
            if user['username'] != st.session_state.get('username'):
                if st.button("Delete", key=f"delete_{user['username']}", type="secondary"):
                    try:
                        response = requests.delete(f"{BACKEND_URL}/users/{user['username']}")
                        if response.status_code == 200:
                            st.success(response.json().get('message'))
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error(f"Backend Error: {response.json().get('detail')}")
                    except requests.ConnectionError:
                        st.error("Connection error. Could not delete user.")
