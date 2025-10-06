import streamlit as st
import pandas as pd
import joblib
import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from utils import load_data_from_api, load_css

# ================= PERMISSION CHECK =================
if not st.session_state.get("logged_in", False):
    st.error("Please log in first to access this page."); st.stop()
allowed_roles = ["Admin", "Teacher"]
if st.session_state.get("role") not in allowed_roles:
    st.error("You do not have permission to view this page."); st.stop()
# ===============================================================

# --- CONFIGURATION & INITIAL SETUP ---
load_css("assets/style.css")
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

ELITE_MODEL_PATH = os.path.join(ROOT_DIR, 'student_risk_model.pkl')
CUSTOM_MODEL_PATH = os.path.join(ROOT_DIR, 'custom_student_model.pkl')

default_features = {
    'f1': 'quiz_avg', 'f2': 'assignment_submissions',
    'f3': 'attendance_percentage', 'f4': 'lms_hours'
}
internal_feature_order = list(default_features.values())

for key in ['weights', 'weights_valid', 'custom_model_trained_eval', 'performance_models']:
    if key not in st.session_state:
        if key == 'weights_valid' or key == 'custom_model_trained_eval': st.session_state[key] = False
        elif key == 'weights': st.session_state[key] = {"f1": 0.25, "f2": 0.25, "f3": 0.25, "f4": 0.25}
        else: st.session_state[key] = {}

@st.cache_resource
def load_all_models():
    models = {}
    try:
        if os.path.exists(ELITE_MODEL_PATH):
            models['Elite'] = joblib.load(ELITE_MODEL_PATH)
        else: st.error(f"Elite model not found at {ELITE_MODEL_PATH}.")
        if os.path.exists(CUSTOM_MODEL_PATH):
            models['Custom'] = joblib.load(CUSTOM_MODEL_PATH)
            st.session_state.custom_model_trained_eval = True
    except Exception as e:
        st.error(f"An error occurred during model loading: {e}")
    return models

if not st.session_state.performance_models:
    st.session_state.performance_models = load_all_models()

base_df = load_data_from_api()

def train_and_save_custom_model(weights, data_df):
    if data_df is None or data_df.empty: return None, "No data available."
    df_copy = data_df.copy()
    df_copy['weighted_score'] = (df_copy[default_features['f1']] * weights['f1'] + df_copy[default_features['f2']] * (weights['f2'] * 10) + df_copy[default_features['f3']] * weights['f3'] + df_copy[default_features['f4']] * weights['f4'])
    at_risk_threshold = df_copy['weighted_score'].quantile(0.40)
    df_copy['custom_at_risk'] = (df_copy['weighted_score'] <= at_risk_threshold).astype(int)
    X = df_copy[internal_feature_order]; y = df_copy['custom_at_risk']
    if len(y.unique()) < 2: return None, "Not enough variation in data."
    temp_model = RandomForestClassifier(n_estimators=50, random_state=42).fit(X, y)
    joblib.dump(temp_model, CUSTOM_MODEL_PATH)
    return temp_model, None

def evaluate_model(model, X_test, y_test):
    if model is None or X_test.empty or y_test.empty: return None, None
    predictions = model.predict(X_test)
    metrics = {"Accuracy": accuracy_score(y_test, predictions), "Precision": precision_score(y_test, predictions, zero_division=0), "Recall": recall_score(y_test, predictions, zero_division=0), "F1-Score": f1_score(y_test, predictions, zero_division=0)}
    try:
        if hasattr(model, "predict_proba"):
            probabilities = model.predict_proba(X_test)[:, 1]
            metrics["AUC Score"] = roc_auc_score(y_test, probabilities)
        else: metrics["AUC Score"] = "N/A"
    except Exception: metrics["AUC Score"] = "N/A"
    cm = confusion_matrix(y_test, predictions)
    return metrics, cm

st.title("📈 AI Model Performance Dashboard")
st.markdown("Evaluate the effectiveness of your Elite and Custom models.")
st.divider()

with st.sidebar:
    st.header("⚙️ Custom Model Training")
    st.markdown("Define weights to train a 'Custom' model.")
    w_f1 = st.slider("Quiz Avg Weight", 0, 100, 25, key='eval_w1')
    w_f2 = st.slider("Assignment Submissions Weight", 0, 100, 25, key='eval_w2')
    w_f3 = st.slider("Attendance Percentage Weight", 0, 100, 25, key='eval_w3')
    w_f4 = st.slider("Lms Hours Weight", 0, 100, 25, key='eval_w4')
    total_weight = w_f1 + w_f2 + w_f3 + w_f4
    if total_weight != 100: st.error(f"Total weight must be 100%."); st.session_state.weights_valid = False
    else: st.success("Weights are balanced."); st.session_state.weights_valid = True
    st.session_state.weights = {"f1": w_f1/100.0, "f2": w_f2/100.0, "f3": w_f3/100.0, "f4": w_f4/100.0}
    if st.button("Train Custom Model", use_container_width=True, disabled=not st.session_state.weights_valid):
        if base_df is not None and not base_df.empty:
            with st.spinner("Training and saving..."):
                custom_model_temp, error_msg = train_and_save_custom_model(st.session_state.weights, base_df)
                if custom_model_temp is not None:
                    st.session_state.performance_models['Custom'] = custom_model_temp
                    st.session_state.custom_model_trained_eval = True; st.success("Custom model trained!")
                else: st.error(f"Training failed: {error_msg}"); st.session_state.custom_model_trained_eval = False
        else: st.error("No student data available for training.")

if base_df is None or base_df.empty:
    st.warning("No student data available. Please upload data to evaluate models.")
else:
    available_models = list(st.session_state.performance_models.keys())
    selected_model_name = st.radio("Select Model to Evaluate", available_models, index=0, horizontal=True)
    st.divider()
    model_to_evaluate = st.session_state.performance_models.get(selected_model_name)
    if model_to_evaluate:
        st.subheader(f"📊 {selected_model_name} Model Performance")
        X = base_df[internal_feature_order]; y_true = None
        if selected_model_name == 'Elite':
            base_df['temp_score'] = (base_df[default_features['f1']] * 0.25 + base_df[default_features['f2']] * 2.5 + base_df[default_features['f3']] * 0.25 + base_df[default_features['f4']] * 0.25)
            threshold = base_df['temp_score'].quantile(0.40); y_true = (base_df['temp_score'] <= threshold).astype(int)
        elif selected_model_name == 'Custom':
            custom_df_for_y = base_df.copy()
            custom_df_for_y['weighted_score'] = (custom_df_for_y[default_features['f1']] * st.session_state.weights['f1'] + custom_df_for_y[default_features['f2']] * (st.session_state.weights['f2'] * 10) + custom_df_for_y[default_features['f3']] * st.session_state.weights['f3'] + custom_df_for_y[default_features['f4']] * st.session_state.weights['f4'])
            threshold = custom_df_for_y['weighted_score'].quantile(0.40); y_true = (custom_df_for_y['weighted_score'] <= threshold).astype(int)
        if y_true is not None:
            if y_true.nunique() > 1 and y_true.value_counts().min() > 1:
                X_train, X_test, y_train, y_test = train_test_split(X, y_true, test_size=0.3, random_state=42, stratify=y_true)
            else: X_train, X_test, y_train, y_test = train_test_split(X, y_true, test_size=0.3, random_state=42)
            metrics, cm = evaluate_model(model_to_evaluate, X_test, y_test)
            if metrics and cm is not None:
                st.write("### Key Performance Metrics"); metrics_cols = st.columns(len(metrics))
                for i, (metric_name, value) in enumerate(metrics.items()):
                    metrics_cols[i].metric(metric_name, f"{value:.2f}" if isinstance(value, float) else value)
                st.write("### Confusion Matrix"); fig, ax = plt.subplots(figsize=(6, 5))
                sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False, xticklabels=['Not At-Risk (Predicted)', 'At-Risk (Predicted)'], yticklabels=['Not At-Risk (Actual)', 'At-Risk (Actual)'])
                plt.title('Confusion Matrix'); plt.ylabel('Actual Label'); plt.xlabel('Predicted Label'); st.pyplot(fig)
            else: st.error("Failed to evaluate the model.")
        else: st.error("Could not generate target variable for evaluation.")
    else: st.warning(f"'{selected_model_name}' model not available.")