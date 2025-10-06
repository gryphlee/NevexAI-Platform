import streamlit as st
import pandas as pd
from utils import load_data_from_api # UPDATED IMPORT
import joblib
from sklearn.ensemble import RandomForestClassifier
import shap

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") != "Student":
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

# --- Re-usable function to train a model on the fly ---
@st.cache_data(show_spinner="Training custom AI model...")
def train_custom_model(weights, base_df):
    if base_df is None: return None
    df_copy = base_df.copy()
    default_features = {
        'f1': 'quiz_avg', 'f2': 'assignment_submissions', 
        'f3': 'attendance_percentage', 'f4': 'lms_hours'
    }
    df_copy['weighted_score'] = (df_copy[default_features['f3']] * weights['f3'] + 
                                 df_copy[default_features['f1']] * weights['f1'] + 
                                 df_copy[default_features['f2']] * (weights['f2'] * 10) + 
                                 df_copy[default_features['f4']] * weights['f4'])
    
    at_risk_threshold = df_copy['weighted_score'].quantile(0.40)
    df_copy['custom_at_risk'] = (df_copy['weighted_score'] <= at_risk_threshold).astype(int)
    
    X = df_copy[list(default_features.values())]
    y = df_copy['custom_at_risk']

    if len(y.unique()) < 2: return None
    
    custom_model = RandomForestClassifier(n_estimators=50, random_state=42).fit(X, y)
    return custom_model

# --- Initialize Session State for this page ---
if 'student_feature_names' not in st.session_state:
    st.session_state.student_feature_names = {
        'f1': 'Quiz Avg', 'f2': 'Assignments', 'f3': 'Attendance', 'f4': 'LMS Hours'
    }
if 'student_weights_valid' not in st.session_state:
    st.session_state.student_weights_valid = False
if 'student_weights' not in st.session_state:
    st.session_state.student_weights = None


st.title("🔬 My Risk Simulator")
st.markdown("Use this tool to understand your current risk status and simulate how improving your scores can change the outcome.")

# --- SIDEBAR FOR CONFIGURATION ---
st.sidebar.header("Simulator Configuration")
with st.sidebar.expander("✏️ Customize Metric Names"):
    st.session_state.student_feature_names['f1'] = st.text_input("Metric 1", st.session_state.student_feature_names['f1'])
    st.session_state.student_feature_names['f2'] = st.text_input("Metric 2", st.session_state.student_feature_names['f2'])
    st.session_state.student_feature_names['f3'] = st.text_input("Metric 3", st.session_state.student_feature_names['f3'])
    st.session_state.student_feature_names['f4'] = st.text_input("Metric 4", st.session_state.student_feature_names['f4'])

with st.sidebar.expander("🔬 Configure Custom Grading"):
    st.info("Experiment with different grading weights to see how it affects your risk status.")
    w_f1 = st.slider(f"{st.session_state.student_feature_names['f1']} Weight (%)", 0, 100, 40, key='sw1')
    w_f2 = st.slider(f"{st.session_state.student_feature_names['f2']} Weight (%)", 0, 100, 30, key='sw2')
    w_f3 = st.slider(f"{st.session_state.student_feature_names['f3']} Weight (%)", 0, 100, 10, key='sw3')
    w_f4 = st.slider(f"{st.session_state.student_feature_names['f4']} Weight (%)", 0, 100, 20, key='sw4')
    
    total_weight = w_f1 + w_f2 + w_f3 + w_f4
    if total_weight != 100:
        st.sidebar.error(f"Total weight must be 100%. Current: {total_weight}%")
        st.session_state.student_weights_valid = False
    else:
        st.sidebar.success("Weights are balanced.")
        st.session_state.student_weights_valid = True
        st.session_state.student_weights = {"f1": w_f1/100.0, "f2": w_f2/100.0, "f3": w_f3/100.0, "f4": w_f4/100.0}

# --- Load Student Data from API ---
try:
    all_students_df = load_data_from_api()
    if all_students_df is None:
        st.error("Could not load data. Please ensure the backend service is running.")
        st.stop()

    student_id = st.session_state.get('student_id')
    my_data = all_students_df[all_students_df['student_id'] == student_id]
    student_record = my_data.iloc[0]
except Exception as e:
    st.error(f"Failed to load your data. Please contact an administrator. Error: {e}")
    st.stop()

# --- Display Current Status ---
st.divider()
st.subheader("Your Current Standing")
# (Current status display remains the same)

# --- "WHAT-IF" SCENARIO SIMULATOR ---
st.divider()
st.subheader("What-If Scenario Simulator")
st.write("Use the sliders below to see how improving certain metrics could change your risk status.")

try:
    # --- MODEL SELECTION LOGIC ---
    if st.session_state.student_weights_valid:
        st.info("Using your custom grading system for prediction.")
        model_to_use = train_custom_model(st.session_state.student_weights, all_students_df)
        if model_to_use is None:
            st.warning("Could not train custom model, using default.")
            model_to_use = joblib.load('app/elite_student_model.pkl')
    else:
        st.info("Using the default grading system. Configure weights in the sidebar to run a custom model.")
        model_to_use = joblib.load('app/elite_student_model.pkl')
    
    # --- Sliders now use custom names ---
    what_if_quiz = st.slider(f"Hypothetical {st.session_state.student_feature_names['f1']}", 0, 100, int(student_record['quiz_avg']))
    what_if_assign = st.slider(f"Hypothetical {st.session_state.student_feature_names['f2']}", 0, 10, int(student_record['assignment_submissions']))
    what_if_attend = st.slider(f"Hypothetical {st.session_state.student_feature_names['f3']}", 0, 100, int(student_record['attendance_percentage']))
    what_if_lms = st.slider(f"Hypothetical {st.session_state.student_feature_names['f4']}", 0, 50, int(student_record['lms_hours']))
    
    hypothetical_data = {
        'quiz_avg': [what_if_quiz],
        'assignment_submissions': [what_if_assign],
        'attendance_percentage': [what_if_attend],
        'lms_hours': [what_if_lms]
    }
    hypothetical_df = pd.DataFrame(hypothetical_data)
    
    feature_order = ['quiz_avg', 'assignment_submissions', 'attendance_percentage', 'lms_hours']
    hypothetical_df_ordered = hypothetical_df[feature_order]
    
    hypo_prediction = model_to_use.predict(hypothetical_df_ordered)
    hypo_risk_status = 'AT-RISK' if hypo_prediction[0] == 1 else 'NOT AT-RISK'
    
    st.subheader("💡 Hypothetical Outcome")
    if hypo_risk_status == 'AT-RISK':
        st.warning(f'**With these scores, the prediction is still:** {hypo_risk_status}')
    else:
        st.success(f'**With these scores, the prediction improves to:** {hypo_risk_status}')

except FileNotFoundError:
    st.error("Prediction model not found. The simulator is currently unavailable.")
except Exception as e:
    st.error(f"An error occurred while running the simulation. Please check your data. Error: {e}")

