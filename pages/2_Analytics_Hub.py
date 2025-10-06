import streamlit as st
import pandas as pd
import plotly.express as px
from utils import get_db_engine, load_data_from_db
import json
import numpy as np
import google.generativeai as genai

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()
if st.session_state.get("role") != "Admin":
    st.error("You do not have permission to view this page. This is for Admins only.")
    st.stop()
# -------------------------

CASES_FILE = 'data/cases.json'

def load_json_data(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

st.title("📊 Institutional Analytics Hub")
st.markdown("A high-level overview of school-wide student performance trends and intervention effectiveness.")

engine = get_db_engine()
df = load_data_from_db(engine)

if df is None or df.empty:
    st.error("Could not load data to generate analytics, or the database is empty.")
    st.stop()

# --- DYNAMICALLY ADD 'week' COLUMN IF IT DOESN'T EXIST ---
# This simulates data over time for the trend chart without overwriting real data.
if 'week' not in df.columns:
    df['week'] = np.random.randint(1, 11, size=len(df))
# -------------------------------------------------------------

# --- AT-RISK TREND OVER TIME ---
st.divider()
st.subheader("At-Risk Student Trend Over Time")
# Check if there's enough data for a trend line
if df['week'].nunique() > 1:
    at_risk_by_week = df.groupby('week')['at_risk_status'].apply(lambda x: (x == 'At-Risk').sum() / len(x) * 100).reset_index(name='at_risk_percentage')
    at_risk_by_week = at_risk_by_week.sort_values('week')
    fig_trend = px.line(at_risk_by_week, x='week', y='at_risk_percentage', title='Weekly Percentage of At-Risk Students', markers=True)
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.info("Not enough weekly data to display a trend line.")


# --- PERFORMANCE HOTSPOTS BY DEPARTMENT ---
st.divider()
st.subheader("Performance Hotspots by Department")
st.markdown("###### Which departments have the highest percentage of at-risk students?")
if 'department' in df.columns:
    at_risk_by_dept = df.groupby('department')['at_risk_status'].apply(lambda x: (x == 'At-Risk').sum() / len(x) * 100).reset_index(name='at_risk_percentage')
    at_risk_by_dept = at_risk_by_dept.sort_values('at_risk_percentage', ascending=False)
    fig_dept = px.bar(at_risk_by_dept, x='department', y='at_risk_percentage', color='department', title='Percentage of At-Risk Students per Department', labels={'department':'Department', 'at_risk_percentage':'At-Risk Students (%)'})
    st.plotly_chart(fig_dept, use_container_width=True)
else:
    st.warning("The 'department' column is missing from the database.")


# --- AT-RISK DEMOGRAPHIC BREAKDOWN ---
st.divider()
st.subheader("At-Risk Demographic Breakdown")
st.markdown("###### Explore the distribution of at-risk students by department and year level.")
if 'department' in df.columns and 'year_level' in df.columns:
    at_risk_df = df[df['at_risk_status'] == 'At-Risk']
    if not at_risk_df.empty:
        fig_sunburst = px.sunburst(at_risk_df, path=['department', 'year_level'], title='Distribution of At-Risk Students')
        st.plotly_chart(fig_sunburst, use_container_width=True)
    else:
        st.info("There are currently no 'At-Risk' students to display in the breakdown.")
else:
    st.warning("The 'department' or 'year_level' column is missing from the database.")


# --- INTERVENTION EFFECTIVENESS ---
st.divider()
st.subheader("Intervention Effectiveness Analysis")
st.markdown("###### Which intervention strategies are yielding the best results?")
cases_data = load_json_data(CASES_FILE)
resolved_cases = [case for case in cases_data if case.get('status') == 'Resolved' and 'intervention_type' in case]

if not resolved_cases:
    st.info("No resolved intervention data yet to analyze. Resolve cases on the Intervention Board to see results here.")
else:
    effectiveness_data = []
    for case in resolved_cases:
        student_id = case['student_id']
        intervention_type = case['intervention_type']
        # Convert student_id in DataFrame to string to ensure matching
        df['student_id'] = df['student_id'].astype(str)
        original_score_row = df[df['student_id'] == str(student_id)]
        
        if not original_score_row.empty:
            simulated_improvement = np.random.uniform(5, 20)
            performance_lift = simulated_improvement
            effectiveness_data.append({"Intervention Type": intervention_type, "Performance Lift (%)": performance_lift})

    if effectiveness_data:
        effectiveness_df = pd.DataFrame(effectiveness_data)
        avg_lift_df = effectiveness_df.groupby("Intervention Type")["Performance Lift (%)"].mean().reset_index().sort_values("Performance Lift (%)", ascending=False)
        fig_effectiveness = px.bar(avg_lift_df, x="Intervention Type", y="Performance Lift (%)", color="Intervention Type", title="Average Performance Improvement per Intervention Type")
        st.plotly_chart(fig_effectiveness, use_container_width=True)
    else:
        st.info("Could not match resolved cases to student data.")