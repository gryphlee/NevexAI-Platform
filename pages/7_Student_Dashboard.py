# pages/7_Student_Dashboard.py
import streamlit as st
import pandas as pd
from utils import get_db_engine, load_data_from_db
import json
import os

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
allowed_roles = ["Student", "Admin", "Teacher"]
if st.session_state.get("role") not in allowed_roles:
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

# --- CONFIGURATION ---
DATA_DIR = 'data'
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'assignments.json')

def load_json_data(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# --- MAIN APP LOGIC ---
st.set_page_config(layout="wide")

engine = get_db_engine()
all_students_df = load_data_from_db(engine)

student_to_display_id = None
current_user_role = st.session_state.get("role")

# Case 1: An Admin or Teacher has selected a student from another page
if current_user_role in ["Admin", "Teacher"] and 'selected_student_id' in st.session_state:
    student_to_display_id = st.session_state.get('selected_student_id')
    
    # --- IMPROVED BACK BUTTON LOGIC ---
    if st.button("← Back to Integrity Dashboard"):
        del st.session_state['selected_student_id']
        # Instead of rerun, we switch back to the previous page
        st.switch_page("pages/13_Integrity_Dashboard.py")

# Case 2: A Student is logged in
elif current_user_role == "Student":
    student_to_display_id = st.session_state.get("student_id")

# --- Render the dashboard for the selected student ---
if student_to_display_id and all_students_df is not None:
    all_students_df['student_id'] = all_students_df['student_id'].astype(str)
    my_data = all_students_df[all_students_df['student_id'] == str(student_to_display_id)]
    
    if my_data.empty:
        st.warning(f"Could not find data for Student ID: {student_to_display_id}")
        st.stop()

    student_record = my_data.iloc[0]
    risk_status = student_record['at_risk_status']
    
    # Determine the title based on the user's role
    if current_user_role == "Student":
        title_username = st.session_state.get('username')
    else: # Admin/Teacher is viewing another student
        title_username = f"ID: {student_to_display_id}"
        
    st.title(f"🎓 Student Dashboard: {title_username}")
    st.markdown("This is the personal dashboard to track progress and achievements.")
    
    # (The rest of your code for displaying resources, goals, badges, metrics, etc. remains the same)
    st.divider()
    st.subheader("🤖 AI Recommended Resources")
    assigned_resources_log = load_json_data(ASSIGNMENTS_FILE)
    my_assigned_resources = [item for item in assigned_resources_log if item.get('student_id') == str(student_to_display_id)]
    if my_assigned_resources:
        st.info("Our AI agents have assigned the following resources to help you improve.")
        latest_assignment = my_assigned_resources[-1]
        for resource in latest_assignment.get('assigned_resources', []):
            st.markdown(f"- **{resource['title']} ({resource['type']}):** [Click to open]({resource['link']})")
    else:
        st.success("No specific resources have been assigned by the AI agents. Keep up the great work!")

    # --- PERFORMANCE METRICS ---
    st.divider()
    st.subheader("📊 My Performance Metrics")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Quiz Average", f"{student_record['quiz_avg']}%")
    col2.metric("Assignments Submitted", f"{student_record['assignment_submissions']}/10")
    col3.metric("Attendance", f"{student_record['attendance_percentage']}%")
    col4.metric("LMS Hours (Weekly)", f"{student_record['lms_hours']} hrs")

    if risk_status == "At-Risk":
        st.error(f"Current Status: {risk_status}")
    else:
        st.success(f"Current Status: {risk_status}")

else:
    st.title("🎓 Student Dashboard")
    st.info("Select a student from another page (like the Integrity Dashboard) to view their details, or log in as a student to see your own dashboard.")
