# integrity_agent.py
import pandas as pd
from datetime import timedelta
import json
import os

# --- Configuration ---
DATA_DIR = 'data'
ACTIVITY_LOG_FILE = os.path.join(DATA_DIR, 'activity_log.csv')
GRADE_HISTORY_FILE = os.path.join(DATA_DIR, 'grade_history.csv')
INTEGRITY_FLAGS_FILE = os.path.join(DATA_DIR, 'integrity_flags.json')

def analyze_quiz_behavior(log_df):
    """Analyzes activity logs for behavioral anomalies."""
    flagged_students = {}
    for (student_id, quiz_id), group in log_df.groupby(['student_id', 'quiz_id']):
        # Ensure start and submit actions exist before proceeding
        if group[group['action'] == 'start_quiz'].empty or group[group['action'] == 'submit_quiz'].empty:
            continue
        start_time = group[group['action'] == 'start_quiz']['timestamp'].iloc[0]
        submit_time = group[group['action'] == 'submit_quiz']['timestamp'].iloc[0]
        duration = submit_time - start_time
        num_questions = group[group['action'] == 'answer_question']['question_id'].nunique()
        min_duration_threshold = timedelta(seconds=10 * num_questions)

        if duration < min_duration_threshold:
            reason = f"Completed a {num_questions}-question quiz in {duration.seconds}s. (Threshold: {min_duration_threshold.seconds}s)"
            if student_id not in flagged_students: flagged_students[student_id] = []
            flagged_students[student_id].append({"quiz_id": quiz_id, "reason": reason, "type": "Behavioral Anomaly"})
    return flagged_students

def analyze_performance_outliers(history_df):
    """Analyzes grade history for performance anomalies."""
    flagged_students = {}
    for student_id, group in history_df.groupby('student_id'):
        quizzes = group[group['assessment_id'].str.contains('Quiz', na=False)]
        if len(quizzes) < 2: continue
            
        mean_grade = quizzes['grade'].mean()
        std_dev = quizzes['grade'].std()
        if pd.isna(std_dev) or std_dev == 0: continue
            
        outlier_threshold = mean_grade + (2 * std_dev)
        outliers = group[group['grade'] > outlier_threshold]
        
        for index, row in outliers.iterrows():
            reason = f"Scored {row['grade']} on {row['assessment_id']}, a major outlier compared to their quiz average of {mean_grade:.1f}."
            if student_id not in flagged_students: flagged_students[student_id] = []
            flagged_students[student_id].append({"assessment_id": row['assessment_id'], "reason": reason, "type": "Performance Anomaly"})
    return flagged_students


if __name__ == "__main__":
    all_flags = {}

    # --- Run Behavioral Analysis ---
    try:
        activity_df = pd.read_csv(ACTIVITY_LOG_FILE)
        activity_df['timestamp'] = pd.to_datetime(activity_df['timestamp'])
        behavioral_flags = analyze_quiz_behavior(activity_df)
        for student, flags in behavioral_flags.items():
            student_key = str(student) # Ensure key is a string
            if student_key not in all_flags: all_flags[student_key] = []
            all_flags[student_key].extend(flags)
    except FileNotFoundError:
        print(f"Info: '{ACTIVITY_LOG_FILE}' not found, skipping behavioral analysis.")
    
    # --- Run Performance Analysis ---
    try:
        history_df = pd.read_csv(GRADE_HISTORY_FILE)
        performance_flags = analyze_performance_outliers(history_df)
        for student, flags in performance_flags.items():
            student_key = str(student) # Ensure key is a string
            if student_key not in all_flags: all_flags[student_key] = []
            all_flags[student_key].extend(flags)
    except FileNotFoundError:
        print(f"Info: '{GRADE_HISTORY_FILE}' not found, skipping performance analysis.")

    # --- Save All Flags to JSON file ---
    if all_flags:
        print(f"\n--- 🚩 {len(all_flags)} student(s) flagged. Saving results to {INTEGRITY_FLAGS_FILE} ---")
        with open(INTEGRITY_FLAGS_FILE, 'w') as f:
            json.dump(all_flags, f, indent=4)
    else:
        print("\n--- ✅ No suspicious activity detected. ---")
        # Save an empty object to the file if no flags
        with open(INTEGRITY_FLAGS_FILE, 'w') as f:
            json.dump({}, f, indent=4)