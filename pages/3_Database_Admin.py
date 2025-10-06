import streamlit as st
import pandas as pd
import requests
import io
import json

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") != "Admin":
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

st.title("🔑 Data Engineering Control Panel")
st.markdown("Monitor data health, validate new uploads, and manage database records.")

# Import the API loading function from utils
from utils import load_data_from_api

df = load_data_from_api()
BACKEND_URL = "http://127.0.0.1:8000"

# --- DATABASE HEALTH CHECK ---
st.divider()
st.subheader("Database Health Check")
if df is not None:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Student Records", f"{df.shape[0]:,}")
    with col2:
        missing_values = df.isnull().sum().sum()
        st.metric("Missing Data Points", f"{missing_values}", help="Total number of empty cells.")
    with col3:
        num_departments = df['department'].nunique() if 'department' in df.columns else 'N/A'
        st.metric("Unique Departments", num_departments)
else:
    st.warning("Could not load database to perform health check. Is the backend running?")

# --- INTELLIGENT DATA MAPPER ---
st.divider()
st.subheader("Upload & Map New Student Data")

REQUIRED_COLUMNS = {
    'student_id': 'Unique Student ID',
    'quiz_avg': 'Quiz Average (%)',
    'assignment_submissions': 'Assignments Submitted (Count)',
    'attendance_percentage': 'Attendance (%)',
    'lms_hours': 'LMS Engagement (Hours)',
    'department': 'Student Department',
    'year_level': 'Year Level',
}

uploaded_file = st.file_uploader("Upload any student CSV file", type="csv", key="data_mapper_uploader")

if uploaded_file is not None:
    try:
        df_uploaded = pd.read_csv(uploaded_file)
        uploaded_columns = df_uploaded.columns.tolist()

        st.info("Step 1: Preview of your uploaded data (first 5 rows)")
        st.dataframe(df_uploaded.head())

        st.info("Step 2: Map your columns to our system's required fields")
        column_mapping = {}
        used_columns = set()
        
        for req_col, req_desc in REQUIRED_COLUMNS.items():
            best_guess = next((col for col in uploaded_columns if req_col.lower() in col.lower() or col.lower() in req_col.lower()), None)
            best_guess_index = uploaded_columns.index(best_guess) if best_guess else 0
            selected_col = st.selectbox(
                f"System needs: **{req_desc}**",
                options=uploaded_columns,
                index=best_guess_index,
                key=f"map_{req_col}"
            )
            column_mapping[req_col] = selected_col
            used_columns.add(selected_col)

        # --- NEW: Step 3 for Optional Columns ---
        st.info("Step 3: (Optional) Select any extra columns you want to import")
        optional_columns = [col for col in uploaded_columns if col not in used_columns]
        selected_optional_cols = st.multiselect(
            "Select custom columns to include:",
            options=optional_columns
        )

        if st.button("Process and Import Data", type="primary", use_container_width=True):
            with st.spinner("Mapping and validating data..."):
                df_to_import = pd.DataFrame()
                df_to_import['at_risk_status'] = 'Not Evaluated'

                for req_col, user_col in column_mapping.items():
                    df_to_import[req_col] = df_uploaded[user_col]
                
                # --- Logic to handle custom columns ---
                if selected_optional_cols:
                    custom_df = df_uploaded[selected_optional_cols]
                    df_to_import['custom_data'] = custom_df.apply(lambda row: row.to_json(), axis=1)
                else:
                    df_to_import['custom_data'] = '{}' # Add empty json object if no custom cols

                errors = []
                for col in ['quiz_avg', 'attendance_percentage']:
                    if not pd.api.types.is_numeric_dtype(df_to_import[col]):
                        errors.append(f"Mapped column for '{col}' must be numeric.")
                
                if errors:
                    for error in errors: st.error(error)
                else:
                    st.success("✅ Data mapped successfully!")
                    st.write("The following data will be sent to the database:")
                    st.dataframe(df_to_import.head())
                    
                    csv_bytes = df_to_import.to_csv(index=False).encode('utf-8')
                    files = {'file': ('mapped_data.csv', csv_bytes, 'text/csv')}
                    
                    try:
                        response = requests.post(f"{BACKEND_URL}/students/upload", files=files)
                        if response.status_code == 200:
                            st.success("Successfully appended new data via backend!")
                            st.cache_data.clear(); st.rerun()
                        else:
                            st.error(f"Backend Error: {response.json().get('detail')}")
                    except Exception as e:
                        st.error(f"Failed to send data to backend: {e}")

    except Exception as e:
        st.error(f"An error occurred: {e}")

# --- LINK PARENT TO STUDENT SECTION ---
st.divider()
st.subheader("🔗 Link Parent to Student Account")
if df is not None:
    with st.form("link_parent_form"):
        col1, col2 = st.columns(2)
        with col1:
            student_id_to_link = st.number_input("Enter Student ID", format="%d", step=1, value=None)
        with col2:
            parent_username_to_link = st.text_input("Enter Parent Username")
        
        submitted = st.form_submit_button("Link Accounts")
        if submitted:
            if student_id_to_link is not None and parent_username_to_link:
                try:
                    payload = {"student_id": student_id_to_link, "parent_username": parent_username_to_link}
                    response = requests.post(f"{BACKEND_URL}/students/link-parent", json=payload)
                    if response.status_code == 200:
                        st.success(response.json().get('message'))
                        st.cache_data.clear(); st.rerun()
                    else:
                        st.error(f"Backend Error: {response.json().get('detail')}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please provide both a Student ID and a Parent Username.")
else:
    st.warning("Could not load student data to perform linking.")

# --- View Current Database Section ---
st.divider()
st.subheader("View Current Database")
if df is not None:
    st.dataframe(df)
else:
    st.warning("Could not load data to display.")