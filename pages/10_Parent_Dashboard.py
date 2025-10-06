import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data_from_api # UPDATED IMPORT
import json
import numpy as np

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") != "Parent":
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

RESOURCES_FILE = 'data/resources.json'

def load_resources():
    try:
        with open(RESOURCES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

st.title(f"👨‍👩‍👧 Parent Dashboard")
st.markdown(f"Welcome, {st.session_state.get('username')}! This is your portal to monitor your child's academic progress and find helpful resources.")

# --- DATA IS NOW LOADED FROM THE API ---
all_students_df = load_data_from_api()
parent_username = st.session_state.get('username')

if all_students_df is None:
    st.error("Could not load student data. Please ensure the backend service is running.")
    st.stop()

# Check first if the 'parent_username' column even exists
if 'parent_username' not in all_students_df.columns:
    st.error("The parent linking system has not been initialized by an administrator yet.")
    st.info("Please contact your school administrator and ask them to visit the 'Database Admin' page to set up the necessary columns.")
    st.stop()
# ---------------------------

child_data = all_students_df[all_students_df['parent_username'] == parent_username]

if child_data.empty:
    st.warning("Could not find data for your child. Please ensure your account has been correctly linked by the school administrator via the 'Database Admin' page.")
    st.stop()

child_record = child_data.iloc[0]
child_id = child_record['student_id']
risk_status = child_record['at_risk_status']

st.divider()

# --- Child's Current Status ---
st.header(f"Performance Snapshot for Student ID: {child_id}")
col1, col2 = st.columns(2)
with col1:
    st.subheader("Current Risk Status")
    if risk_status == "At-Risk":
        st.error("Status: AT-RISK")
        st.caption("This status is based on our AI's analysis of recent academic data.")
    else:
        st.success("Status: NOT AT-RISK")
        st.caption("Your child is currently performing well.")

with col2:
    st.subheader("Key Metrics")
    st.metric("Quiz Average", f"{child_record['quiz_avg']}%")
    st.metric("Attendance", f"{child_record['attendance_percentage']}%")

# --- Performance Trend ---
st.divider()
st.subheader("Quiz Performance Trend")
st.markdown("This chart shows your child's quiz performance over recent weeks.")

# Simulate weekly data for the trend chart
week_data = pd.DataFrame({
    'Week': list(range(1, 11)),
    'Quiz Score': np.random.normal(loc=child_record['quiz_avg'], scale=5, size=10).clip(0, 100)
})
fig_trend = px.line(week_data, x='Week', y='Quiz Score', title="Weekly Quiz Score Progress", markers=True)
fig_trend.update_layout(yaxis_range=[0,100])
st.plotly_chart(fig_trend, use_container_width=True)


# --- Communication Hub ---
st.divider()
st.subheader("Connect with the Advisor")
st.markdown("Have a question or concern? Send a message directly to your child's advisor.")
with st.form("contact_advisor_form"):
    message = st.text_area("Your Message")
    submitted = st.form_submit_button("Send Message")
    if submitted:
        if message:
            st.success("Your message has been sent to the advisor!")
        else:
            st.warning("Please enter a message.")
            
# --- RESOURCES FOR PARENTS ---
st.divider()
st.subheader("📚 Resources for You")
st.markdown("Here are some articles and guides selected by the school to help you support your child's learning journey.")

all_resources = load_resources()
parent_resources = [res for res in all_resources if 'parent' in res.get('tags', [])]

if not parent_resources:
    st.info("No specific resources for parents have been added by the administrator yet.")
else:
    for resource in parent_resources:
        with st.container(border=True):
            st.markdown(f"**{resource['title']}** (`{resource['type']}`)")
            st.markdown(f"[Click here to view this resource]({resource['link']})")

