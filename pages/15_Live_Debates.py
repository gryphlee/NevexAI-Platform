import streamlit as st
import pandas as pd
import json
import os
from sqlalchemy import create_engine
import time
from case_actions import approve_plan, modify_plan, reject_plan

# ================= PERMISSION CHECK =================
if not st.session_state.get("logged_in", False):
    st.error("Please log in first to access this page."); st.stop()
allowed_roles = ["Admin", "Teacher"]
if st.session_state.get("role") not in allowed_roles:
    st.error("You do not have permission to view this page."); st.stop()
# ===============================================================

# --- Initialize Session State for this page's forms ---
if 'show_modify_form' not in st.session_state:
    st.session_state.show_modify_form = False
if 'show_reject_form' not in st.session_state:
    st.session_state.show_reject_form = False

# --- CONFIGURATION & DATA LOADING ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT_DIR, 'university.db')
DB_URI = f'sqlite:///{DB_PATH}'
AGENT_REGISTRY_FILE = os.path.join(ROOT_DIR, 'data', 'agent_registry.json')

@st.cache_data(ttl=10)
def load_live_data():
    engine = create_engine(DB_URI)
    try:
        query = "SELECT * FROM events WHERE status = 'in_progress' OR status = 'resolved' ORDER BY timestamp DESC LIMIT 1"
        live_case_df = pd.read_sql(query, engine)
        if not live_case_df.empty:
            return live_case_df.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Could not connect to the event bus (database). Error: {e}")
    return None

@st.cache_data(ttl=60)
def load_agent_registry():
    try:
        with open(AGENT_REGISTRY_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"agents": []}

# --- MAIN PAGE LAYOUT ---
st.set_page_config(layout="wide")
st.title("💬 Live Agent Debates")
st.markdown("This page shows the real-time status and results of the AI Agent Swarm.")
st.divider()

live_case = load_live_data()
agent_registry = load_agent_registry()

if live_case:
    st.header(f"🚨 Case: Student {live_case['student_id']}")
    st.subheader(f"Problem: {live_case['event_type']}")
    st.caption(f"Status: {live_case['status']} | Last Update: {live_case['timestamp']}")

    with st.container(border=True):
        st.subheader("📢 Agent Bidding Simulation")
        agents = agent_registry.get('agents', [])
        if agents:
            st.success(f"✅ Task Force Selected: {agents[0]['id']}, {agents[1]['id']}, {agents[2]['id']}")
        else:
            st.warning("No agent data found in registry.")

    with st.expander("View Mock Debate Transcript", expanded=True):
        st.subheader(f"💬 Case #{live_case['event_id']} Debate")
        st.markdown("---")
        st.markdown("📍 **ROUND 1: Opening Statements (Simulated)**")
        st.markdown(f"**🤖 {agents[0]['id']} ({agents[0]['type']}):** \"Based on the data, the primary issue is academic. I propose immediate resource assignment.\"")
        st.markdown(f"**🤖 {agents[1]['id']} ({agents[1]['type']}):** \"I disagree, the pattern suggests an engagement problem. An outreach is necessary first.\"")
        st.markdown(f"**🤖 {agents[2]['id']} ({agents[2]['type']}):** \"Both are valid, but a check-in call should precede any new assignments to avoid overwhelming the student.\"")
        st.markdown("---")
        st.markdown("📍 **FINAL ROUND: Synthesized Recommendation (Simulated)**")
        st.info("""
        **CONSENSUS:** Prioritize student well-being before academic intervention.
        **FINAL PLAN:**
        1. **Immediate:** Initiate 'Day 1' outreach.
        2. **Monitor:** Track engagement for 48 hours.
        3. **Contingency:** If no engagement, assign targeted resources.
        """)

    st.divider()
    st.subheader("Teacher Approval")
    is_action_taken = live_case['status'] in ['approved', 'modified', 'rejected']
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Approve & Execute Plan", type="primary", use_container_width=True, disabled=is_action_taken):
            success, message = approve_plan(live_case['event_id'], live_case['student_id'], st.session_state.get('username', 'Unknown'))
            if success:
                st.success(message); st.toast("Refreshing page..."); time.sleep(2); st.rerun()
            else:
                st.error(message)
    with col2:
        if st.button("✏️ Modify Plan", use_container_width=True, disabled=is_action_taken):
            st.session_state.show_modify_form = True
            st.session_state.show_reject_form = False
            st.rerun()
    with col3:
        if st.button("❌ Reject & Provide Reason", use_container_width=True, disabled=is_action_taken):
            st.session_state.show_reject_form = True
            st.session_state.show_modify_form = False
            st.rerun()
    
    if is_action_taken:
        st.info(f"Action has been taken on this plan (Status: {live_case['status']}).")

    if st.session_state.show_modify_form:
        with st.form("modify_form"):
            st.subheader("✏️ Modify the AI's Plan")
            modifications = st.text_area("Describe your changes or provide a new plan:", height=150)
            submitted = st.form_submit_button("Save Modifications")
            if submitted:
                success, message = modify_plan(live_case['event_id'], live_case['student_id'], st.session_state.get('username'), modifications)
                if success:
                    st.success(message); st.session_state.show_modify_form = False; time.sleep(2); st.rerun()
                else:
                    st.error(message)

    if st.session_state.show_reject_form:
        with st.form("reject_form"):
            st.subheader("❌ Reject the AI's Plan")
            reason = st.selectbox("Reason for rejection:", ["I have additional context", "The recommendation is off-base", "I want to try a different approach", "Other"])
            comments = st.text_area("Provide additional comments (required):")
            submitted = st.form_submit_button("Submit Rejection")
            if submitted:
                if comments:
                    success, message = reject_plan(live_case['event_id'], live_case['student_id'], st.session_state.get('username'), reason, comments)
                    if success:
                        st.success(message); st.session_state.show_reject_form = False; time.sleep(2); st.rerun()
                    else:
                        st.error(message)
                else:
                    st.warning("Comments are required when rejecting a plan.")

else:
    st.info("No active or recently resolved cases found on the Event Bus.")
    st.markdown("---")
    st.header("How to generate a new debate:")
    st.write("1. Run `watcher_agent.py` to post a new 'at-risk' event.")
    st.write("2. Run `dispatcher_agent.py` to process the event.")
    st.write("3. Refresh this page to see the results.")