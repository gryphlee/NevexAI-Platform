import streamlit as st
import pandas as pd
import joblib
import shap
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
import subprocess
from sklearn.ensemble import RandomForestClassifier
from utils import load_data_from_api, load_css

# ================= PERMISSION CHECK =================
if not st.session_state.get("logged_in", False):
    st.error("Please log in first to access this page.")
    st.stop()

allowed_roles = ["Admin", "Teacher"]
if st.session_state.get("role") not in allowed_roles:
    st.error("You do not have permission to view this page.")
    st.stop()
# ===============================================================

load_css("assets/style.css")

default_features = {
    'f1': 'quiz_avg', 'f2': 'assignment_submissions',
    'f3': 'attendance_percentage', 'f4': 'lms_hours'
}
internal_feature_order = list(default_features.values())

# Initialize session state for this page
for key in ['prediction_made', 'original_input', 'custom_model', 'custom_explainer',
            'weights_valid', 'weights', 'selected_student_details', 'last_batch_explainer', 'feature_names']:
    if key not in st.session_state:
        if key == 'feature_names':
            st.session_state[key] = default_features.copy()
        elif key in ['prediction_made', 'weights_valid']:
            st.session_state[key] = False
        else:
            st.session_state[key] = None

base_df_for_training = load_data_from_api()

try:
    elite_model = joblib.load('app/elite_student_model.pkl')
    elite_explainer = joblib.load('app/elite_shap_explainer.pkl')
except FileNotFoundError:
    st.error("Model files not found. Please ensure 'app/elite_student_model.pkl' and 'app/elite_shap_explainer.pkl' exist.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred during model setup: {e}")
    st.stop()

def st_shap(plot, height=None):
    shap_html = f"<head>{shap.getjs()}</head><body>{plot.html()}</body>"
    st.components.v1.html(shap_html, height=height)

def create_gauge_chart(value, min_val, max_val, label, filename):
    fig, ax = plt.subplots(figsize=(4, 0.8)); ax.set_xlim(min_val, max_val); ax.set_ylim(0, 1)
    ax.barh([0.5], [max_val - min_val], left=min_val, height=0.5, color='#e0e0e0')
    percent = (value - min_val) / (max_val - min_val) if (max_val - min_val) != 0 else 0
    color = '#d9534f' if percent < 0.4 else ('#f0ad4e' if percent < 0.7 else '#5cb85c')
    ax.barh([0.5], [value - min_val], left=min_val, height=0.5, color=color)
    ax.text(value, 0.5, f' {value}', va='center', ha='left' if value < max_val*0.9 else 'right', color='white' if value > max_val*0.1 else 'black', fontsize=12, weight='bold')
    ax.set_title(label, loc='left', pad=10); ax.axis('off')
    plt.savefig(filename, bbox_inches='tight', dpi=150, transparent=True); plt.close(fig)

# ---- NEW: probability helper (added here next to other helpers) ----
def calculate_success_probability(hypothetical_df, model):
    """
    Returns probability (%) that the student is 'NOT AT-RISK' according to the model.
    Assumes model.predict_proba returns [prob_class_0 (NOT AT-RISK), prob_class_1 (AT-RISK)].
    If model is None or predict_proba not available, returns 0.
    """
    if model is None:
        return 0.0
    try:
        probs = model.predict_proba(hypothetical_df)
        success_proba = probs[0][0]  # class 0 = NOT AT-RISK
        return float(success_proba * 100.0)
    except Exception:
        # fallback for models without predict_proba
        try:
            pred = model.predict(hypothetical_df)[0]
            return 0.0 if pred == 1 else 100.0
        except Exception:
            return 0.0

# ---- NEW: Ollama helper to query local phi-3-mini/phi3-mini ----
def query_ollama(prompt, model="phi3-mini", timeout=8):
    """
    Runs: `ollama run <model>` and pipes prompt via stdin.
    Returns textual output or an ASCII-only error string. Non-fatal.
    """
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout
        )
        out = result.stdout.strip()
        if not out:
            out = result.stderr.strip()
        return out or "No response from Ollama."
    except subprocess.TimeoutExpired:
        return "Ollama request timed out."
    except FileNotFoundError:
        return "Ollama CLI not found. Please install Ollama and ensure 'ollama' is on PATH."
    except Exception as e:
        # ensure ASCII-only return for the PDF
        return f"Ollama error: {str(e)}"

# ---- Helper: sanitize text for FPDF (remove non-ascii to avoid FPDFUnicodeEncodingException) ----
def sanitize_for_pdf(text):
    if text is None:
        return None
    try:
        # Keep common whitespace and printable ASCII only
        return ''.join(ch for ch in str(text) if 32 <= ord(ch) < 127 or ch in '\n\r\t')
    except Exception:
        return str(text).encode('ascii', errors='ignore').decode('ascii', errors='ignore')

class PDF(FPDF):
    def header(self):
        if os.path.exists('assets/logo.png'): self.image('assets/logo.png', x=10, y=8, w=33)
        self.set_font('Arial', 'B', 15); self.cell(80); self.cell(30, 10, 'Student Risk Analysis Report', 0, 0, 'C'); self.ln(20)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf_report(student_data, risk_status, ai_plan, feature_names):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '1. Student Input Data & Performance Metrics', 0, 1)
    data_dict = student_data.to_dict('records')[0]
    ranges = {'attendance_percentage': 100, 'quiz_avg': 100, 'assignment_submissions': 10, 'lms_hours': 50}
    chart_files = []
    internal_to_custom_mapping = {default_features[k]: feature_names[k] for k in default_features}
    for internal_name in internal_feature_order:
        if internal_name in data_dict:
            display_name = internal_to_custom_mapping.get(internal_name, internal_name.replace('_', ' ').title())
            val = data_dict[internal_name]
            filename = f"{internal_name}_gauge.png"
            create_gauge_chart(val, 0, ranges[internal_name], display_name, filename)
            chart_files.append(filename)
            pdf.image(filename, w=90)
            pdf.ln(1)
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, '2. AI Prediction Conclusion', 0, 1)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 7, f"   - Status: {risk_status}", 0, 1)
    if ai_plan:
        # sanitize AI plan to ASCII before adding to PDF
        safe_plan = sanitize_for_pdf(ai_plan)
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, '3. AI-Generated Action Plan', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 5, safe_plan)
    for f in chart_files:
        if os.path.exists(f): os.remove(f)
    return bytes(pdf.output(dest='S'))

@st.cache_data(show_spinner="Training custom AI model...")
def train_custom_model(weights, base_df):
    if base_df is None: return None, None
    df_copy = base_df.copy()
    df_copy['weighted_score'] = (df_copy[default_features['f3']] * weights['f3'] + df_copy[default_features['f1']] * weights['f1'] + df_copy[default_features['f2']] * (weights['f2'] * 10) + df_copy[default_features['f4']] * weights['f4'])
    at_risk_threshold = df_copy['weighted_score'].quantile(0.40)
    df_copy['custom_at_risk'] = (df_copy['weighted_score'] <= at_risk_threshold).astype(int)
    X = df_copy[internal_feature_order]; y = df_copy['custom_at_risk']
    if len(y.unique()) < 2: return None, None
    custom_model = RandomForestClassifier(n_estimators=50, random_state=42).fit(X, y)
    custom_explainer = shap.TreeExplainer(custom_model)
    return custom_model, custom_explainer

# --- Main Page Layout ---
st.title("🤖 Risk Predictor with SHAP Interpretability")
st.markdown(f"Welcome, **{st.session_state.get('username')}**!")
st.divider()

# --- Sidebar Configuration ---
st.sidebar.header("⚙️ Global AI Configuration")
with st.sidebar.expander("✏️ Customize Metrics"):
    st.markdown("Rename the four core metrics to match your course.")
    st.session_state.feature_names['f1'] = st.text_input("Metric 1 (e.g., Quizzes)", st.session_state.feature_names['f1'])
    st.session_state.feature_names['f2'] = st.text_input("Metric 2 (e.g., Assignments)", st.session_state.feature_names['f2'])
    st.session_state.feature_names['f3'] = st.text_input("Metric 3 (e.g., Attendance)", st.session_state.feature_names['f3'])
    st.session_state.feature_names['f4'] = st.text_input("Metric 4 (e.g., LMS/Labs)", st.session_state.feature_names['f4'])

with st.sidebar.expander("🔬 Configure Grading System", expanded=True):
    w_f1 = st.slider(f"{st.session_state.feature_names['f1']} Weight (%)", 0, 100, 40, key='w1')
    w_f2 = st.slider(f"{st.session_state.feature_names['f2']} Weight (%)", 0, 100, 30, key='w2')
    w_f3 = st.slider(f"{st.session_state.feature_names['f3']} Weight (%)", 0, 100, 10, key='w3')
    w_f4 = st.slider(f"{st.session_state.feature_names['f4']} Weight (%)", 0, 100, 20, key='w4')
    total_weight = w_f1 + w_f2 + w_f3 + w_f4
    if total_weight != 100:
        st.sidebar.error(f"Total weight must be 100%. Current: {total_weight}%"); st.session_state.weights_valid = False
    else:
        st.sidebar.success("Weights are balanced."); st.session_state.weights_valid = True
        st.session_state.weights = {"f1": w_f1/100.0, "f2": w_f2/100.0, "f3": w_f3/100.0, "f4": w_f4/100.0}

# --- Main Tabs ---
tab1, tab2 = st.tabs(["Single Student Analysis", "Batch Upload & Predict"])

with tab1:
    col1, col2 = st.columns([1, 1.2])
    with col1:
        st.header('📊 Enter Student Data')
        with st.form("prediction_form"):
            val_f1 = st.slider(f"Student {st.session_state.feature_names['f1']}", 0, 100, 78)
            val_f2 = st.slider(f"Student {st.session_state.feature_names['f2']}", 0, 10, 9)
            val_f3 = st.slider(f"Student {st.session_state.feature_names['f3']}", 0, 100, 85)
            val_f4 = st.slider(f"Student {st.session_state.feature_names['f4']}", 0, 50, 20)
            submit_button = st.form_submit_button(label='Analyze Student Risk')
        if submit_button:
            if st.session_state.weights_valid and base_df_for_training is not None:
                st.session_state.custom_model, st.session_state.custom_explainer = train_custom_model(st.session_state.weights, base_df_for_training)
                input_data_custom_names = {st.session_state.feature_names['f1']: [val_f1], st.session_state.feature_names['f2']: [val_f2], st.session_state.feature_names['f3']: [val_f3], st.session_state.feature_names['f4']: [val_f4]}
                reverse_mapping = {v: default_features[k] for k, v in st.session_state.feature_names.items()}
                standardized_input_df = pd.DataFrame(input_data_custom_names).rename(columns=reverse_mapping)
                st.session_state.original_input = standardized_input_df[internal_feature_order]
                st.session_state.prediction_made = True
            elif not st.session_state.weights_valid: st.warning("Please ensure weights sum to 100% in the sidebar.")
            else: st.error("Base data for training not loaded.")
            
    with col2:
        if st.session_state.prediction_made and st.session_state.original_input is not None:
            model_to_use = st.session_state.custom_model or elite_model
            explainer_to_use = st.session_state.custom_explainer or elite_explainer
            original_df = st.session_state.original_input
            
            if model_to_use and explainer_to_use:
                prediction = model_to_use.predict(original_df)
                risk_status = 'AT-RISK' if prediction[0] == 1 else 'NOT AT-RISK'
                
                st.header("✨ Initial Prediction Analysis")
                # we'll produce AI plan if needed
                ai_plan = None

                if risk_status == 'AT-RISK':
                    st.error(f'Conclusion: {risk_status}')
                else:
                    st.success(f'Conclusion: {risk_status}')
                
                st.subheader("Reasoning")
                
                shap_values = explainer_to_use.shap_values(original_df)
                expected_value = explainer_to_use.expected_value
                
                # Handle multi-output (binary classification) models
                if hasattr(shap_values, 'shape') and len(shap_values.shape) == 3 and shap_values.shape[2] == 2:
                    shap_values_for_plot = shap_values[:, :, 1]
                    expected_value_for_plot = expected_value[1] if hasattr(expected_value, '__len__') else expected_value
                elif isinstance(shap_values, list) and len(shap_values) > 1:
                    shap_values_for_plot = shap_values[1]
                    expected_value_for_plot = expected_value[1]
                else:
                    shap_values_for_plot = shap_values
                    expected_value_for_plot = expected_value if not hasattr(expected_value, '__len__') else expected_value[0]

                # Create beautiful SHAP visualization and ask Ollama to explain
                ai_explanation = None
                try:
                    import numpy as np
                    
                    # Prepare data
                    feature_names = original_df.columns.tolist()
                    feature_values = original_df.iloc[0].values
                    shap_vals = shap_values_for_plot[0]
                    
                    # Create custom bar plot
                    fig, ax = plt.subplots(figsize=(10, 5))
                    fig.patch.set_facecolor('#1e1e2e')
                    ax.set_facecolor('#1e1e2e')
                    
                    # Sort by absolute SHAP value
                    indices = np.argsort(np.abs(shap_vals))[::-1]
                    
                    # Create bars
                    colors = ['#ff4b4b' if val > 0 else '#4b8bff' for val in shap_vals[indices]]
                    bars = ax.barh(range(len(indices)), shap_vals[indices], color=colors, alpha=0.8, height=0.6)
                    
                    # Customize labels
                    labels = [f"{feature_names[i]} = {feature_values[i]:.1f}" for i in indices]
                    ax.set_yticks(range(len(indices)))
                    ax.set_yticklabels(labels, fontsize=11, color='white')
                    ax.set_xlabel('SHAP Value (Impact on Prediction)', fontsize=12, color='white', weight='bold')
                    ax.set_title('Feature Impact Analysis', fontsize=14, color='white', weight='bold', pad=20)
                    
                    # Add value labels on bars
                    for i, (bar, val) in enumerate(zip(bars, shap_vals[indices])):
                        width = bar.get_width()
                        label_x = width + (0.01 if width > 0 else -0.01)
                        ha = 'left' if width > 0 else 'right'
                        ax.text(label_x, bar.get_y() + bar.get_height()/2, 
                               f'{val:+.3f}', ha=ha, va='center', 
                               fontsize=10, color='white', weight='bold')
                    
                    # Style grid and spines
                    ax.grid(True, axis='x', alpha=0.2, color='white', linestyle='--')
                    ax.spines['top'].set_visible(False)
                    ax.spines['right'].set_visible(False)
                    ax.spines['bottom'].set_color('white')
                    ax.spines['left'].set_color('white')
                    ax.tick_params(colors='white', which='both')
                    ax.axvline(x=0, color='white', linestyle='-', linewidth=1.5, alpha=0.5)
                    
                    # Add legend
                    from matplotlib.patches import Patch
                    legend_elements = [
                        Patch(facecolor='#ff4b4b', alpha=0.8, label='Increases Risk'),
                        Patch(facecolor='#4b8bff', alpha=0.8, label='Decreases Risk')
                    ]
                    ax.legend(handles=legend_elements, loc='lower right', 
                             framealpha=0.9, facecolor='#2e2e3e', edgecolor='white',
                             fontsize=10)
                    
                    plt.tight_layout()
                    st.pyplot(fig)
                    
                    # Ask Ollama to explain the chart in simple terms (teacher/student/parent friendly)
                    explanation_prompt = f"""
You are an educational assistant. Explain this SHAP graph in short, simple terms (for teachers, students, and parents).
Student feature values: {dict(zip(feature_names, feature_values))}
SHAP contributions (impact on risk): {dict(zip(feature_names, shap_vals.tolist()))}

Give:
- 2-3 short bullets summarizing the most important drivers of the prediction,
- one simple recommendation (one sentence) the teacher/parent can try immediately.
Keep language non-technical, friendly, and concise.
"""
                    ai_explanation = query_ollama(explanation_prompt)
                    plt.close()
                except Exception as e:
                    st.error(f"Could not generate SHAP visualization: {str(e)}")
                    import traceback
                    st.code(traceback.format_exc())

                # Show AI explanation (if available)
                if ai_explanation:
                    st.subheader("📖 AI Explanation of Graph")
                    st.info(ai_explanation)

                st.divider()

                # --- Intervention Planner (What-If) ---
                st.header("🔬 Intervention Planner (What-If)")
                what_if_f1 = st.slider(f"Hypothetical {st.session_state.feature_names['f1']}", 0, 100, int(original_df[default_features['f1']].iloc[0]))
                what_if_f2 = st.slider(f"Hypothetical {st.session_state.feature_names['f2']}", 0, 10, int(original_df[default_features['f2']].iloc[0]))
                what_if_f3 = st.slider(f"Hypothetical {st.session_state.feature_names['f3']}", 0, 100, int(original_df[default_features['f3']].iloc[0]))
                what_if_f4 = st.slider(f"Hypothetical {st.session_state.feature_names['f4']}", 0, 50, int(original_df[default_features['f4']].iloc[0]))
                
                hypothetical_df = pd.DataFrame({default_features['f1']: [what_if_f1], default_features['f2']: [what_if_f2], default_features['f3']: [what_if_f3], default_features['f4']: [what_if_f4]})
                hypothetical_df_ordered = hypothetical_df[internal_feature_order]
                hypo_prediction = model_to_use.predict(hypothetical_df_ordered)
                hypo_risk_status = 'AT-RISK' if hypo_prediction[0] == 1 else 'NOT AT-RISK'
                
                # ---- Two-column comparison: Original vs Hypothetical ----
                st.subheader("💡 Hypothetical Outcome")

                projected_success_prob = calculate_success_probability(hypothetical_df_ordered, model_to_use)
                try:
                    original_ordered_df = original_df[internal_feature_order]
                except Exception:
                    original_ordered_df = original_df
                original_success_prob = calculate_success_probability(original_ordered_df, model_to_use)
                delta_prob = projected_success_prob - original_success_prob

                colA, colB = st.columns(2)
                with colA:
                    st.markdown("**📍 Original Scenario**")
                    st.metric(label="Success Probability", value=f"{original_success_prob:.1f}%")
                    if original_success_prob < 50:
                        st.error("Conclusion: AT-RISK")
                    else:
                        st.success("Conclusion: NOT AT-RISK")
                with colB:
                    st.markdown("**🔮 Hypothetical Scenario**")
                    st.metric(label="Success Probability", value=f"{projected_success_prob:.1f}%", delta=f"{delta_prob:+.1f}% vs Original")
                    if projected_success_prob < 50:
                        st.warning("Conclusion: Still AT-RISK")
                    else:
                        st.info("Conclusion: Now NOT AT-RISK")
                # ---- end comparison ----

                # --- AI Action Plan generation if AT-RISK ---
                if risk_status == 'AT-RISK':
                    st.subheader("📝 AI-Generated Action Plan")
                    action_prompt = f"""
You are an educational assistant. The student is AT-RISK.
Student input: {original_df.to_dict('records')[0]}
Top SHAP contributions: {dict(zip(feature_names, shap_vals.tolist()))}

Provide a practical 3-step action plan that teachers or parents can implement in the next 2 weeks.
Keep it simple, actionable, and empathetic.
"""
                    ai_plan = query_ollama(action_prompt)
                    # display the plan
                    st.warning(ai_plan)
                else:
                    ai_plan = None
                
                st.divider(); st.header("📄 Download Report")
                # sanitize ai_plan before writing to PDF inside create_pdf_report
                pdf_data = create_pdf_report(original_df, risk_status, ai_plan, st.session_state.feature_names)
                st.download_button(label="📥 Generate PDF Report", data=pdf_data, file_name=f"student_risk_report.pdf", mime="application/pdf")
            else:
                st.error("Model could not be loaded or trained.")
        else:
            st.info("Configure metrics & weights, enter data, and click 'Analyze'.")

with tab2:
    st.header("📤 Batch Upload & Predict")
    
    if st.session_state.get('weights_valid'):
        st.info("Using the custom grading system defined in the sidebar.", icon="🔬")
        model_to_use, explainer_to_use = train_custom_model(st.session_state.weights, base_df_for_training)
    else:
        st.info("Using the default 'Elite' model.", icon="ℹ️")
        model_to_use, explainer_to_use = elite_model, elite_explainer
    
    if not model_to_use or not explainer_to_use:
        st.error("Could not train or load a model for batch processing.")
    else:
        st.session_state.last_batch_explainer = explainer_to_use
        
        required_columns_list = ['student_id'] + list(st.session_state.feature_names.values())
        st.markdown(f"**Required columns for CSV:** `{', '.join(required_columns_list)}`")

        uploaded_file = st.file_uploader("Choose a CSV file for batch analysis", type="csv", key="batch_uploader")
        
        if uploaded_file is not None:
            roster_df = pd.read_csv(uploaded_file)
            
            if all(col in roster_df.columns for col in required_columns_list):
                reverse_mapping = {v: default_features[k] for k, v in st.session_state.feature_names.items()}
                standardized_roster_df = roster_df.rename(columns=reverse_mapping)
                
                with st.spinner("Analyzing student roster..."):
                    roster_features = standardized_roster_df[internal_feature_order]
                    predictions = model_to_use.predict(roster_features)
                    roster_df['risk_prediction'] = ['AT-RISK' if p == 1 else 'NOT AT-RISK' for p in predictions]

                st.subheader("Batch Prediction Results")
                for index, row in roster_df.iterrows():
                    st.divider()
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        st.metric("Student ID", str(row.get('student_id', 'N/A')))
                    with col2:
                        if row['risk_prediction'] == 'AT-RISK': st.error(f"**Prediction:** {row['risk_prediction']}")
                        else: st.success(f"**Prediction:** {row['risk_prediction']}")
                    with col3:
                        if st.button("🔍 View Details", key=f"details_{row.get('student_id', index)}"):
                            st.session_state.selected_student_details = row.to_dict()
                            st.rerun()
            else:
                missing = set(required_columns_list) - set(roster_df.columns)
                st.error(f"The uploaded CSV is missing: {', '.join(missing)}")

if st.session_state.get('selected_student_details'):
    student_details = st.session_state.selected_student_details
    explainer_for_dialog = st.session_state.get('last_batch_explainer', elite_explainer)

    with st.container(border=True): 
        st.header(f"Detailed Analysis for Student ID: {student_details.get('student_id', 'N/A')}")
        
        reverse_mapping = {v: default_features[k] for k, v in st.session_state.feature_names.items()}
        student_df_for_model_data = {reverse_mapping.get(k, k): v for k, v in student_details.items()}
        student_df_for_model = pd.DataFrame([student_df_for_model_data])[internal_feature_order]
        
        st.subheader("Reasoning Behind Prediction")
        
        shap_values = explainer_for_dialog.shap_values(student_df_for_model)
        expected_value = explainer_for_dialog.expected_value
        
        # Handle multi-output (binary classification) models
        if hasattr(shap_values, 'shape') and len(shap_values.shape) == 3 and shap_values.shape[2] == 2:
            shap_values_for_plot = shap_values[:, :, 1]
            expected_value_for_plot = expected_value[1] if hasattr(expected_value, '__len__') else expected_value
        elif isinstance(shap_values, list) and len(shap_values) > 1:
            shap_values_for_plot = shap_values[1]
            expected_value_for_plot = expected_value[1]
        else:
            shap_values_for_plot = shap_values
            expected_value_for_plot = expected_value if not hasattr(expected_value, '__len__') else expected_value[0]
        
        # Generate beautiful SHAP visualization (batch/detail) and ask Ollama to explain
        try:
            import numpy as np

            # Prepare data
            feature_names = student_df_for_model.columns.tolist()
            feature_values = student_df_for_model.iloc[0].values
            shap_vals = shap_values_for_plot[0]

            # Create custom bar plot
            fig, ax = plt.subplots(figsize=(10, 5))
            fig.patch.set_facecolor('#1e1e2e')
            ax.set_facecolor('#1e1e2e')

            # Sort by absolute SHAP value
            indices = np.argsort(np.abs(shap_vals))[::-1]

            # Create bars
            colors = ['#ff4b4b' if val > 0 else '#4b8bff' for val in shap_vals[indices]]
            bars = ax.barh(range(len(indices)), shap_vals[indices], color=colors, alpha=0.8, height=0.6)

            # Customize labels
            labels = [f"{feature_names[i]} = {feature_values[i]:.1f}" for i in indices]
            ax.set_yticks(range(len(indices)))
            ax.set_yticklabels(labels, fontsize=11, color='white')
            ax.set_xlabel('SHAP Value (Impact on Prediction)', fontsize=12, color='white', weight='bold')
            ax.set_title('Feature Impact Analysis', fontsize=14, color='white', weight='bold', pad=20)

            # Add value labels on bars
            for i, (bar, val) in enumerate(zip(bars, shap_vals[indices])):
                width = bar.get_width()
                label_x = width + (0.01 if width > 0 else -0.01)
                ha = 'left' if width > 0 else 'right'
                ax.text(label_x, bar.get_y() + bar.get_height()/2,
                        f'{val:+.3f}', ha=ha, va='center',
                        fontsize=10, color='white', weight='bold')

            # Style grid and spines
            ax.grid(True, axis='x', alpha=0.2, color='white', linestyle='--')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color('white')
            ax.spines['left'].set_color('white')
            ax.tick_params(colors='white', which='both')
            ax.axvline(x=0, color='white', linestyle='-', linewidth=1.5, alpha=0.5)

            # Add legend
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='#ff4b4b', alpha=0.8, label='Increases Risk'),
                Patch(facecolor='#4b8bff', alpha=0.8, label='Decreases Risk')
            ]
            ax.legend(handles=legend_elements, loc='lower right',
                      framealpha=0.9, facecolor='#2e2e3e', edgecolor='white',
                      fontsize=10)

            plt.tight_layout()
            st.pyplot(fig)

            # Ask Ollama to explain
            explanation_prompt = f"""
You are an educational assistant. Explain this SHAP graph in short, simple terms (for teachers, students, and parents).
Student feature values: {dict(zip(feature_names, feature_values))}
SHAP contributions (impact on risk): {dict(zip(feature_names, shap_vals.tolist()))}

Give 2-3 short bullets summarizing the most important drivers of the prediction,
and one immediate recommendation the teacher/parent can try.
Keep language non-technical and concise.
"""
            ai_explanation = query_ollama(explanation_prompt)
            if ai_explanation:
                st.subheader("📖 AI Explanation of Graph")
                st.info(ai_explanation)

            plt.close()

        except Exception as e:
            st.error(f"Could not generate SHAP visualization: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
        
        if st.button("Close"):
            st.session_state.selected_student_details = None
            st.rerun()


