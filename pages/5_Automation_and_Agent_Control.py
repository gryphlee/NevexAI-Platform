import streamlit as st
import json
import requests
import subprocess
import sys
import os

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") != "Admin":
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

st.set_page_config(layout="wide")
st.title("⚙️ Automation & Agent Control")
st.markdown("Manage rule-based automations and manually trigger the system's autonomous agents.")

# --- HELPER FUNCTION TO RUN SCRIPTS (with UI improvements) ---
def run_script(script_name):
    python_executable = sys.executable
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    script_path = os.path.join(project_root, script_name)

    if not os.path.exists(script_path):
        st.error(f"Script not found: {script_path}")
        return

    with st.spinner(f"🚀 Executing `{script_name}`... Please wait."):
        process = subprocess.Popen(
            [python_executable, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=project_root
        )
        full_output = "".join(iter(process.stdout.readline, ''))
        process.stdout.close()
        return_code = process.wait()

    if return_code == 0:
        st.success(f"✅ Agent `{script_name}` finished its task successfully.")
    else:
        st.error(f"❌ Agent `{script_name}` encountered an error.")

    with st.expander("Show Detailed Log"):
        st.code(full_output, language='bash')

# --- TAB LAYOUT ---
tab1, tab2 = st.tabs(["Rule-Based Automation", "Manual Agent Triggers"])

with tab1:
    st.header("IF/THEN Rule Management")
    st.markdown("Create and manage the metrics and rules that can trigger interventions in the future.")
    
    BACKEND_URL = "http://127.0.0.1:8000"

    # --- API Functions for Rule Management ---
    def get_from_api(endpoint):
        try:
            response = requests.get(f"{BACKEND_URL}/{endpoint}")
            if response.status_code == 200: return response.json()
            st.error(f"Failed to fetch {endpoint}. Status: {response.status_code}")
        except requests.ConnectionError:
            st.error(f"Connection error. Is the backend running? Could not fetch {endpoint}.")
        return None

    def save_to_api(endpoint, data):
        try:
            response = requests.post(f"{BACKEND_URL}/{endpoint}", json=data)
            if response.status_code == 200:
                st.success(response.json().get('message')); return True
            st.error(f"Failed to save {endpoint}. Status: {response.status_code}, Detail: {response.json().get('detail')}")
        except requests.ConnectionError:
            st.error(f"Connection error. Is the backend running? Could not save {endpoint}.")
        return False

    # --- Initialize session state from API ---
    if 'automation_rules' not in st.session_state:
        st.session_state.automation_rules = get_from_api("rules")
    if 'metric_config' not in st.session_state:
        st.session_state.metric_config = get_from_api("metrics")
    if 'current_rule_conditions' not in st.session_state:
        st.session_state.current_rule_conditions = []

    if st.session_state.automation_rules is None or st.session_state.metric_config is None:
        st.error("Failed to load critical configuration from the backend. Please ensure the backend service is running and accessible.")
    else:
        with st.expander("🔧 Configure Available Metrics"):
            st.write("Add or remove metrics available for rule creation.")
            for metric in st.session_state.metric_config: st.info(f"**{metric['name']}** (Type: {metric['type']})")
            with st.form("new_metric_form", clear_on_submit=True):
                st.subheader("Add a New Metric")
                new_metric_name = st.text_input("Metric Name")
                new_metric_type = st.selectbox("Metric Type", ["Numerical", "Categorical"])
                if st.form_submit_button("Add Metric"):
                    if new_metric_name and not any(m['name'] == new_metric_name for m in st.session_state.metric_config):
                        st.session_state.metric_config.append({"name": new_metric_name, "type": new_metric_type})
                        if save_to_api("metrics", st.session_state.metric_config): st.rerun()
                    else: st.warning("Metric name cannot be empty or already exist.")

        st.divider()
        st.subheader("Create a New Automation Rule")
        with st.container(border=True):
            st.markdown("**Step 1: Add Conditions (IF...)**")
            metric_names = [m['name'] for m in st.session_state.metric_config]
            if not metric_names:
                st.warning("No metrics configured.")
            else:
                selected_metric = st.selectbox("Metric", metric_names)
                metric_type = next((m['type'] for m in st.session_state.metric_config if m['name'] == selected_metric), "Numerical")
                if metric_type == "Numerical":
                    condition = st.selectbox("Condition", ["is less than", "is greater than", "is equal to"]); value = st.number_input("Value", value=70)
                else:
                    condition = st.selectbox("Condition", ["is", "is not"]); value = st.text_input("Value", placeholder="e.g., 'IT' or '1st Year'")
                if st.button("Add Condition"):
                    if (metric_type == "Categorical" and value) or (metric_type == "Numerical"):
                        st.session_state.current_rule_conditions.append({"metric": selected_metric, "condition": condition, "value": value}); st.rerun()
                    else: st.warning("Value for Categorical metric cannot be empty.")
            
            if st.session_state.current_rule_conditions:
                st.write("Current Conditions for this Rule ('AND'):")
                for cond in st.session_state.current_rule_conditions: st.info(f"`{cond['metric']}` {cond['condition']} `{cond['value']}`")
            
            st.markdown("**Step 2: Define Action (THEN...)**")
            action = st.selectbox("Action", ["Send email notification to Advisor", "Create High-Priority Alert", "Add student to watchlist"])
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Save Full Rule", type="primary"):
                    if st.session_state.current_rule_conditions:
                        new_rule = {"conditions": st.session_state.current_rule_conditions, "action": action}
                        st.session_state.automation_rules.append(new_rule)
                        if save_to_api("rules", st.session_state.automation_rules):
                            st.session_state.current_rule_conditions = []; st.rerun()
                    else: st.warning("Please add at least one condition.")
            with col2:
                if st.button("Clear Conditions", type="secondary"):
                    st.session_state.current_rule_conditions = []; st.rerun()

        st.divider()
        st.subheader("Current Automation Rules")
        if not st.session_state.automation_rules:
            st.info("No automation rules have been created yet.")
        else:
            for i, rule in enumerate(st.session_state.automation_rules):
                with st.container(border=True):
                    st.markdown(f"**Rule #{i+1}**")
                    conditions_text = " **AND** ".join([f"`{c['metric']}` {c['condition']} `{c['value']}`" for c in rule.get('conditions', [])])
                    st.markdown(f"**IF** {conditions_text}")
                    st.markdown(f"**THEN** `{rule.get('action')}`")
                    if st.button("Delete Rule", key=f"delete_{i}"):
                        st.session_state.automation_rules.pop(i)
                        if save_to_api("rules", st.session_state.automation_rules): st.rerun()

with tab2:
    st.header("Agent Control Panel")
    st.markdown("Manually trigger the system's autonomous agents.")
    
    st.subheader("Swarm Intelligence System")
    st.markdown("Trigger the main dispatcher to process new cases using the agent swarm and debate system.")
    if st.button("Run Dispatcher Agent", use_container_width=True, type="primary", help="Continuously watches the Event Bus, runs the bidding process, assembles task forces, and initiates debates for new cases."):
        st.info("Note: The Dispatcher Agent is designed to run continuously. This button will run a single cycle.")
        run_script("dispatcher_agent.py")

    st.divider()
    st.subheader("Standalone Agents")
    st.markdown("These are the original agents that can be run independently of the swarm system.")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Run Watcher Agent", use_container_width=True, help="Scans for at-risk students and posts new 'events' to the Event Bus for the dispatcher to pick up."):
            run_script("watcher_agent.py")
    with col2:
        if st.button("Run Communication Agent", use_container_width=True, help="Checks the status of ongoing communications and sends follow-up emails based on time delays."):
            run_script("communication_agent.py")
    with col3:
        if st.button("Run Academic Integrity Agent", use_container_width=True, help="Analyzes activity logs and grade history for signs of potential academic dishonesty."):
            run_script("integrity_agent.py")