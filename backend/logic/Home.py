import streamlit as st
from utils import load_css

st.set_page_config(
    page_title="Student Intervention System",
    page_icon="🎓",
    layout="wide"
)

load_css("assets/style.css")

st.title("🎓 Welcome to the AI-Powered Student Intervention System")
st.sidebar.success("Select a page above to begin.")

st.markdown(
    """
    This application is a proof-of-concept tool designed to help educators identify,
    understand, and support at-risk students proactively.

    **👈 Select a page from the sidebar to get started.**

    ### What can you do?
    - **Risk Predictor:** Analyze students individually or in batches using a dynamic AI model that adapts to your grading style.
    - **Analytics Hub:** Explore the entire student dataset with interactive charts and AI-powered summaries to discover trends.
    """
)

st.divider()

# --- NEW: Data Privacy & Ethics Section ---
with st.expander("ℹ️ Data Privacy & Ethical Use Statement"):
    st.markdown(
        """
        This application is designed with the highest regard for data privacy and ethical principles, in line with standards like FERPA and GDPR.

        - **Purpose:** The sole purpose of this tool is to provide **supportive** interventions for student success. Data and predictions are never to be used for punitive measures.
        - **Confidentiality:** All individual student data is treated as confidential. Access to this system is restricted to authorized personnel only.
        - **Transparency:** We believe in "glass box" AI. The integrated SHAP analysis feature is designed to make the AI's reasoning as transparent as possible, ensuring that educators can understand and validate the factors behind any prediction.
        - **Data Integrity:** The application's core dataset is managed through a secure admin panel, ensuring that the data used for analysis is accurate and controlled.
        - **Security:** API keys and sensitive credentials are managed using Streamlit's built-in secrets management and are never exposed in the source code.
        """
    )