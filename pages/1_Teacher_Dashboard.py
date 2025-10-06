import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_data_from_api # UPDATED IMPORT
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# --- PERMISSION CHECK ---
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Please log in to continue.")
    st.stop()

user_role = st.session_state.get("role")
if user_role not in ["Admin", "Teacher"]:
    st.error("You do not have permission to view this page.")
    st.stop()
# -------------------------

st.title(f"👨‍🏫 Teacher Dashboard")
st.markdown(f"Advanced analytics overview of your assigned students.")

# --- DATA IS NOW LOADED FROM THE API ---
my_students_df = load_data_from_api()

if my_students_df is None or my_students_df.empty:
    st.info("There is no student data available or the backend service is not running.")
else:
    st.divider()
    col1, col2, col3 = st.columns(3)
    at_risk_count = my_students_df[my_students_df['at_risk_status'] == 'At-Risk'].shape[0]
    total_students = my_students_df.shape[0]
    with col1: st.metric("Total Students", total_students)
    with col2: st.metric("Students At-Risk", at_risk_count)
    at_risk_percentage = (at_risk_count / total_students * 100) if total_students > 0 else 0
    with col3: st.metric("At-Risk Percentage", f"{at_risk_percentage:.1f}%")
    
    st.divider()
    
    with st.expander("💡 How to Use & Analyze These Graphs (Tutorial)"):
        st.markdown("""
        **Why were these specific graphs chosen?** These are standard Data Science tools designed to reveal not just *what* is happening, but *why*.
        ---
        #### 1. Performance Distribution Analysis (Violin Plot)
        * **What is it?** It shows the full *distribution* (or spread) of scores for each group.
        * **How to read it?** The **wider** parts of the violin show where student scores are most concentrated.
        ---
        #### 2. Metric Correlation Heatmap
        * **What is it?** This chart shows the strength of the relationship between every pair of metrics.
        * **How to read it:** Bright Red (close to 1.0) means strong positive correlation. Bright Blue (close to -1.0) means strong negative correlation.
        ---
        #### 3. Student Segmentation via Clustering (Scatter Plot)
        * **What is it?** This graph uses an AI algorithm to automatically discover distinct groups of students.
        * **How to read it?** Each dot is a student. The color indicates which performance group they belong to.
        """)
    
    st.divider()
    
    st.subheader("Performance Distribution Analysis")
    st.plotly_chart(px.violin(my_students_df, x='at_risk_status', y='quiz_avg', color='at_risk_status', box=True, points="all", color_discrete_map={'At-Risk':'#d9534f', 'Not At-Risk':'#5cb85c'}, labels={'at_risk_status': 'Risk Status', 'quiz_avg': 'Quiz Score Distribution (%)'}).update_layout(showlegend=False), use_container_width=True)
    
    st.subheader("Metric Correlation Heatmap")
    numeric_cols = my_students_df.select_dtypes(include=['number']).columns
    corr = my_students_df[numeric_cols].corr()
    st.plotly_chart(px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r', labels=dict(color="Correlation")).update_xaxes(side="top"), use_container_width=True)
    
    st.subheader("Student Segmentation via Clustering")
    cluster_features = ['quiz_avg', 'attendance_percentage', 'assignment_submissions', 'lms_hours']
    student_features = my_students_df[cluster_features]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(student_features)
    kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
    my_students_df['cluster'] = kmeans.fit_predict(scaled_features).astype('str')
    st.plotly_chart(px.scatter(my_students_df, x='quiz_avg', y='attendance_percentage', color='cluster', hover_data=['student_id', 'at_risk_status'], title='Student Groups based on Quiz and Attendance', labels={'quiz_avg': 'Quiz Average (%)', 'attendance_percentage': 'Attendance (%)', 'cluster': 'Student Group'}), use_container_width=True)
    
    st.divider()
    st.subheader("Detailed Student Roster")
    st.dataframe(my_students_df)