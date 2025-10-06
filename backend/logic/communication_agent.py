# communication_agent.py (Production Version)
from datetime import datetime, timedelta
import pandas as pd
import os
from dotenv import load_dotenv

# --- Local Imports ---
from utils import get_db_engine, load_data_from_db
from communication_manager import get_student_status, update_student_status
from email_sender import send_outreach_email

# --- Configuration ---
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)
SENDER_EMAIL = os.getenv("SENDER_EMAIL")

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Agent Logic ---
def run_communication_agent():
    print("🤖 Communication Agent: Starting run...")
    
    engine = get_db_engine()
    students_df = load_data_from_db(engine)
    if students_df is None or students_df.empty:
        print("No student data found. Exiting.")
        return

    at_risk_students = students_df[students_df['at_risk_status'] == 'At-Risk']
    print(f"Found {len(at_risk_students)} at-risk students to check.")

    for index, student in at_risk_students.iterrows():
        student_id = student['student_id']
        student_name = f"Student {student_id}"
        
        print(f"\n--- Checking Student ID: {student_id} ---")
        
        status, last_update_str = get_student_status(student_id)
        
        # --- Decision Making Logic ---
        
        if status is None:
            print("  -> Status: New case. Sending Day 1 check-in.")
            if send_outreach_email(SENDER_EMAIL, student_name, "Day 1 Check-In"):
                update_student_status(student_id, "Day 1 Email Sent")
            continue

        if status == "Day 1 Email Sent":
            last_update_time = datetime.strptime(last_update_str, TIME_FORMAT)
            # Restored to 48 hours for real-world use
            if datetime.now() >= last_update_time + timedelta(hours=48):
                print("  -> Status: Day 1 email sent over 48 hours ago. Sending Day 3 follow-up.")
                if send_outreach_email(SENDER_EMAIL, student_name, "Day 3 Follow-Up"):
                    update_student_status(student_id, "Day 3 Follow-Up Sent")
            else:
                print("  -> Status: Day 1 email sent recently. No action needed yet.")
            continue
            
        if status == "Day 3 Follow-Up Sent":
            last_update_time = datetime.strptime(last_update_str, TIME_FORMAT)
            # Restored to 48 hours for real-world use
            if datetime.now() >= last_update_time + timedelta(hours=48):
                print("  -> Status: Day 3 follow-up sent over 48 hours ago. Escalating.")
                update_student_status(student_id, "Escalated to Human")
            else:
                print("  -> Status: Day 3 follow-up sent recently. No action needed yet.")
            continue
            
        if status in ["Responded", "Escalated to Human"]:
            print(f"  -> Status: '{status}'. No further automated action will be taken.")
            continue

    print("\n🤖 Communication Agent: Run complete.")

if __name__ == "__main__":
    run_communication_agent()