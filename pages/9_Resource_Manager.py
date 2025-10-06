# pages/9_Resource_Manager.py
import streamlit as st
import json
import pandas as pd

RESOURCES_FILE = 'data/resources.json'

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") not in ["Admin", "Teacher"]:
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

def load_resources():
    """Loads resources from the JSON file."""
    try:
        with open(RESOURCES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_resources(resources):
    """Saves the updated list of resources to the JSON file."""
    with open(RESOURCES_FILE, 'w') as f:
        json.dump(resources, f, indent=4)

st.set_page_config(layout="wide")
st.title("📚 Resource Manager")
st.markdown("Add, edit, and tag educational resources for the AI agent to use.")

# Load existing resources
resources = load_resources()

# --- Display and Edit Resources in a Table ---
st.subheader("Current Resources")

if not resources:
    st.info("No resources found. Add a new resource below.")
    # Create an empty DataFrame with the correct structure if no resources exist
    df_resources = pd.DataFrame(columns=['title', 'link', 'type', 'tags_str', 'actions'])
else:
    # Convert list of dicts to DataFrame for easier manipulation
    df_resources = pd.DataFrame(resources)
    # Ensure tags column exists and is a list
    if 'tags' not in df_resources.columns:
        df_resources['tags'] = [[] for _ in range(len(df_resources))]
    # Convert list of tags to a comma-separated string for display
    df_resources['tags_str'] = df_resources['tags'].apply(lambda x: ', '.join(x) if isinstance(x, list) else '')

# --- Use st.data_editor for a spreadsheet-like interface ---
edited_df = st.data_editor(
    df_resources[['title', 'link', 'type', 'tags_str']],
    num_rows="dynamic",
    use_container_width=True,
    column_config={
        "title": st.column_config.TextColumn("Title", required=True),
        "link": st.column_config.LinkColumn("Link/URL", required=True),
        "type": st.column_config.SelectboxColumn(
            "Resource Type",
            options=["Video", "PDF", "Worksheet", "Interactive Quiz", "Article"],
            required=True
        ),
        "tags_str": st.column_config.TextColumn("Tags (comma-separated)", help="e.g., Calculus, Beginner, Video")
    },
    key="resource_editor"
)

if st.button("Save Changes", use_container_width=True):
    try:
        # Convert the edited DataFrame back to a list of dictionaries
        updated_resources = []
        for index, row in edited_df.iterrows():
            # Convert comma-separated string back to a list of tags
            tags_list = [tag.strip() for tag in row['tags_str'].split(',') if tag.strip()]
            
            updated_resources.append({
                'title': row['title'],
                'link': row['link'],
                'type': row['type'],
                'tags': tags_list
            })
        
        save_resources(updated_resources)
        st.success("Resources saved successfully!")
        st.rerun() # Rerun to reflect the changes immediately
    except Exception as e:
        st.error(f"Failed to save changes: {e}")

st.markdown("---")
st.info("To **delete** a resource, select the row(s) in the table above and press the `Delete` key on your keyboard, then click 'Save Changes'.")