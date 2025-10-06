# pages/12_Agent_Action_Center.py

import streamlit as st
import json
import pandas as pd

RECOMMENDATIONS_FILE = 'data/recommendations.json'

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") not in ["Admin", "Teacher"]:
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

def load_recommendations():
    """Loads recommendations from the JSON file."""
    try:
        with open(RECOMMENDATIONS_FILE, 'r') as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return []
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_recommendations(data):
    """Saves the updated list of recommendations to the JSON file."""
    with open(RECOMMENDATIONS_FILE, 'w') as f:
        json.dump(data, f, indent=4)

st.set_page_config(layout="wide")
st.title("🤖 Agent Action Center")
st.markdown("This is the inbox for the AI Agent's proactive recommendations. Review and act on these alerts.")

recommendations = load_recommendations()

if not recommendations:
    st.info("The AI Agent has not generated any recommendations yet. Run an agent script to scan for cases.")
else:
    # Convert to DataFrame for easier filtering and display
    df = pd.DataFrame(recommendations)
    df = df.sort_values(by='timestamp', ascending=False) # Show newest first
    
    # --- METRICS ---
    pending_count = len(df[df['status'] == 'Pending'])
    actioned_count = len(df[df['status'] == 'Action Taken'])
    dismissed_count = len(df[df['status'] == 'Dismissed'])
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Pending Recommendations", pending_count)
    col2.metric("Actioned Cases", actioned_count)
    col3.metric("Dismissed Alerts", dismissed_count)

    st.markdown("---")
    
    # --- FILTERS in Sidebar ---
    st.sidebar.header("Filter Recommendations")
    status_filter = st.sidebar.multiselect(
        "Filter by Status:",
        options=df['status'].unique(),
        default=['Pending'] # Default to only showing pending items
    )
    
    priority_filter = st.sidebar.multiselect(
        "Filter by Priority:",
        options=df['priority'].unique(),
        default=df['priority'].unique()
    )

    # Filter dataframe based on selections
    filtered_df = df[df['status'].isin(status_filter) & df['priority'].isin(priority_filter)]

    st.subheader(f"Displaying {len(filtered_df)} Recommendations")

    if filtered_df.empty:
        st.warning("No recommendations match the current filters.")
    else:
        # Convert df to a list of dicts to iterate through
        recs_to_display = filtered_df.to_dict('records')
        
        for i, rec in enumerate(recs_to_display):
            rec_id = f"{rec['student_id']}_{rec['timestamp']}"
            
            with st.container(border=True):
                col1, col2, col3 = st.columns([2,1,1])
                with col1:
                    st.markdown(f"**Student ID:** `{rec['student_id']}`")
                with col2:
                    st.markdown(f"**Priority:** {rec['priority']}")
                with col3:
                    st.markdown(f"**Status:** {rec['status']}")
                
                st.caption(f"Generated on: {rec['timestamp']}")
                st.write(rec['summary'])
                
                with st.expander("View Full AI Recommendation & Actions"):
                    st.text_area("AI Generated Text:", rec['recommendation'], height=150, disabled=True, key=f"text_{rec_id}")
                    
                    st.markdown("**Actions:**")
                    action_col1, action_col2, action_col3 = st.columns(3)
                    
                    # Action Taken Button
                    if action_col1.button("✅ Mark as Action Taken", key=f"act_{rec_id}", use_container_width=True, disabled=(rec['status'] != 'Pending')):
                        # Find the original index and update
                        original_index = df[df['timestamp'] == rec['timestamp']].index[0]
                        recommendations[original_index]['status'] = 'Action Taken'
                        save_recommendations(recommendations)
                        st.success(f"Case for {rec['student_id']} marked as 'Action Taken'.")
                        st.rerun() # Use the new command

                    # Dismiss Button
                    if action_col2.button("🗑️ Dismiss", key=f"dismiss_{rec_id}", use_container_width=True, disabled=(rec['status'] != 'Pending')):
                        original_index = df[df['timestamp'] == rec['timestamp']].index[0]
                        recommendations[original_index]['status'] = 'Dismissed'
                        save_recommendations(recommendations)
                        st.info(f"Case for {rec['student_id']} dismissed.")
                        st.rerun() # Use the new command
                        
                    # Re-open Button
                    if action_col3.button("🔄 Re-open Case", key=f"reopen_{rec_id}", use_container_width=True, disabled=(rec['status'] == 'Pending')):
                        original_index = df[df['timestamp'] == rec['timestamp']].index[0]
                        recommendations[original_index]['status'] = 'Pending'
                        save_recommendations(recommendations)
                        st.warning(f"Case for {rec['student_id']} re-opened.")
                        st.rerun() # Use the new command