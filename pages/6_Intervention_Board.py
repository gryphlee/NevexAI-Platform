import streamlit as st
import pandas as pd
from utils import load_data_from_api # UPDATED IMPORT
import json
from datetime import datetime

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
allowed_roles = ["Admin", "Teacher"]
if st.session_state.get("role") not in allowed_roles:
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

st.title("📋 Intervention Tracking Board")
st.markdown("Monitor and manage intervention cases for at-risk students.")

RULES_FILE = 'data/rules.json'
CASES_FILE = 'data/cases.json'

# --- Functions to load and save data ---
def load_data(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_data(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# --- Initialize Session State ---
st.session_state.automation_rules = load_data(RULES_FILE)
st.session_state.intervention_cases = load_data(CASES_FILE)
if 'resolving_case' not in st.session_state:
    st.session_state.resolving_case = None

# --- RULE ENGINE ---
def run_rule_engine():
    rules = st.session_state.automation_rules
    if not rules:
        st.toast("No automation rules to run.")
        return
    
    # --- DATA IS NOW LOADED FROM THE API ---
    df = load_data_from_api()
    if df is None:
        st.error("Could not load student data to run rules. Please ensure the backend service is running.")
        return
        
    new_cases_generated = 0
    current_cases = st.session_state.intervention_cases
    for index, student in df.iterrows():
        for rule in rules:
            all_conditions_met = True
            if 'conditions' not in rule or not rule['conditions']: continue
            for condition_details in rule['conditions']:
                metric, condition_op, value = condition_details['metric'], condition_details['condition'], condition_details['value']
                student_value = student.get(metric)
                if student_value is None:
                    all_conditions_met = False
                    break
                try:
                    if condition_op in ['is less than', 'is greater than', 'is equal to']:
                        if not (pd.to_numeric(student_value, errors='coerce') < float(value) if condition_op == 'is less than' else \
                                pd.to_numeric(student_value, errors='coerce') > float(value) if condition_op == 'is greater than' else \
                                pd.to_numeric(student_value, errors='coerce') == float(value)):
                            all_conditions_met = False
                            break
                    elif condition_op in ['is', 'is not']:
                        if not (str(student_value).lower() == str(value).lower() if condition_op == 'is' else \
                                str(student_value).lower() != str(value).lower()):
                            all_conditions_met = False
                            break
                except (ValueError, TypeError):
                    all_conditions_met = False
                    break
            if all_conditions_met:
                rule_text = " AND ".join([f"{c['metric']} {c['condition']} {c['value']}" for c in rule['conditions']])
                case_id = f"{student['student_id']}_{rule_text}"
                case_exists = any(c.get('id') == case_id for c in current_cases)
                if not case_exists:
                    new_case = {"id": case_id, "student_id": student['student_id'], "status": "To Do", "reason": f"Rule: {rule_text}", "action_needed": rule['action']}
                    current_cases.append(new_case)
                    new_cases_generated += 1
    if new_cases_generated > 0:
        save_data(CASES_FILE, current_cases)
        st.success(f"{new_cases_generated} new intervention case(s) have been generated!")
        st.rerun()
    else:
        st.info("No new cases were generated based on the current rules.")

if st.button("Run Rules & Check for New Cases", type="primary"):
    run_rule_engine()

st.divider()

# --- Functions to change case status ---
def change_status(case_id, new_status, intervention_type=None):
    for case in st.session_state.intervention_cases:
        if case.get('id') == case_id:
            case['status'] = new_status
            if intervention_type:
                case['intervention_type'] = intervention_type
                case['resolved_date'] = datetime.now().strftime("%Y-%m-%d")
            break
    save_data(CASES_FILE, st.session_state.intervention_cases)
    st.session_state.resolving_case = None # Clear the resolving state
    st.rerun()

# --- POP-UP LOGIC WITHOUT st.dialog ---
if st.session_state.resolving_case:
    case = st.session_state.resolving_case
    with st.container(border=True):
        st.subheader(f"Log Intervention Action for Student ID: {case['student_id']}")
        intervention_type = st.selectbox(
            "What type of intervention was performed?",
            ("1-on-1 Tutoring", "Parent-Teacher Conference", "Referred to Guidance Counselor", "Provided Extra Materials", "Behavioral Counseling", "Other"),
            index=None,
            placeholder="Select an action...",
            key=f"intervention_select_{case['id']}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Resolution", type="primary", key=f"confirm_{case['id']}"):
                if intervention_type:
                    change_status(case['id'], "Resolved", intervention_type)
                else:
                    st.warning("Please select an intervention type.")
        with col2:
            if st.button("Cancel", key=f"cancel_{case['id']}"):
                st.session_state.resolving_case = None
                st.rerun()
# --- KANBAN BOARD (Only shows if not resolving a case) ---
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("⚪ To Do")
        for case in [c for c in st.session_state.intervention_cases if c['status'] == 'To Do']:
            with st.container(border=True):
                st.markdown(f"**Student ID:** {case['student_id']}")
                st.caption(f"Reason: {case['reason']}")
                if st.button("Start Intervention", key=f"start_{case['id']}"):
                    change_status(case['id'], "In Progress")

    with col2:
        st.header("🔵 In Progress")
        for case in [c for c in st.session_state.intervention_cases if c['status'] == 'In Progress']:
            with st.container(border=True):
                st.markdown(f"**Student ID:** {case['student_id']}")
                st.caption(f"Reason: {case['reason']}")
                if st.button("Mark as Resolved", key=f"resolve_{case['id']}"):
                    st.session_state.resolving_case = case
                    st.rerun()

    with col3:
        st.header("🟢 Resolved")
        for case in [c for c in st.session_state.intervention_cases if c['status'] == 'Resolved']:
            with st.container(border=True):
                st.markdown(f"**Student ID:** {case['student_id']}")
                st.caption(f"Reason: {case['reason']}")
                if 'intervention_type' in case:
                    st.success(f"Action Taken: {case['intervention_type']}")
                if st.button("Re-open Case", key=f"reopen_{case['id']}", type="secondary"):
                    change_status(case['id'], "To Do")

