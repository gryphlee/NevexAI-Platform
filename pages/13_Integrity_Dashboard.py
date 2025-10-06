# pages/13_Integrity_Dashboard.py
import streamlit as st
import json
import os

# --- Configuration ---
FLAGS_FILE = 'data/integrity_flags.json'

# --- Permission Check ---
if not st.session_state.get("logged_in", False):
    st.error("Please log in first to access this page.")
    st.stop()

allowed_roles = ["Admin", "Teacher"]
if st.session_state.get("role") not in allowed_roles:
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

def load_flags():
    """Loads integrity flags from the JSON file."""
    try:
        with open(FLAGS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_flags(flags_data):
    """Saves the flags data back to the JSON file."""
    with open(FLAGS_FILE, 'w') as f:
        json.dump(flags_data, f, indent=4)

# --- Main Page UI ---
st.set_page_config(layout="wide")
st.title("🚩 Academic Integrity Dashboard")
st.markdown("This dashboard shows students flagged by the AI for potential academic dishonesty based on behavioral and performance analytics.")

flagged_students = load_flags()

if not flagged_students:
    st.success("✅ No students have been flagged by the system.")
    st.info("Run the `integrity_agent.py` script to analyze recent student activity.")
else:
    st.metric("Total Students Flagged", len(flagged_students))
    st.markdown("---")
    
    # Iterate over a copy of the items so we can modify the dictionary
    for student_id, flags in list(flagged_students.items()):
        with st.container(border=True):
            st.subheader(f"Student ID: {student_id}")
            
            for i, flag in enumerate(flags):
                st.markdown(f"**Flag {i+1}: {flag.get('type', 'N/A')}**")
                st.warning(f"Reason: {flag.get('reason', 'No details provided.')}")

            with st.expander("Actions"):
                if st.button("Review Student's Full Profile", key=f"profile_{student_id}"):
                    st.session_state['selected_student_id'] = student_id
                    st.switch_page("pages/7_Student_Dashboard.py")
                
                # --- ADDED LOGIC HERE ---
                if st.button("Clear Flags for this Student", key=f"clear_{student_id}", type="primary"):
                    # Remove the student from the dictionary
                    if student_id in flagged_students:
                        del flagged_students[student_id]
                    
                    # Save the updated dictionary back to the file
                    save_flags(flagged_students)
                    
                    st.success(f"Flags for Student ID {student_id} have been cleared.")
                    # Rerun the script to refresh the page
                    st.rerun()