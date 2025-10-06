# watcher_agent.py (Updated to use the Event Bus)
import pandas as pd
import json
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
import os

# --- Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'university.db')
DB_URI = f'sqlite:///{DB_PATH}'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

def post_event_to_bus(student_id, event_type, details):
    """Posts a new event to the 'events' table in the database."""
    engine = create_engine(DB_URI)
    event_id = f"evt_{uuid.uuid4().hex[:8]}"
    timestamp = datetime.now().strftime(DATETIME_FORMAT)
    
    event = {
        "event_id": event_id,
        "student_id": str(student_id),
        "event_type": event_type,
        "payload": json.dumps(details),
        "status": "new",
        "timestamp": timestamp
    }
    
    try:
        with engine.connect() as connection:
            insert_query = text("""
                INSERT INTO events (event_id, student_id, event_type, payload, status, timestamp)
                VALUES (:event_id, :student_id, :event_type, :payload, :status, :timestamp)
            """)
            connection.execute(insert_query, event)
            connection.commit()
        print(f"  -> ✅ Event '{event_id}' posted to Event Bus for student {student_id}.")
        return True
    except Exception as e:
        print(f"  -> ❌ ERROR: Could not post event to Event Bus. {e}")
        return False


def run_watcher_agent():
    """
    Scans for at-risk students and posts an event for each one found.
    """
    print("🤖 Watcher Agent: Starting scan for at-risk students...")
    engine = create_engine(DB_URI)
    
    try:
        students_df = pd.read_sql("SELECT student_id, at_risk_status, department FROM students", engine)
        
        # Get list of students already being processed from the event bus
        events_df = pd.read_sql("SELECT student_id FROM events WHERE status IN ('new', 'in_progress')", engine)
        processing_ids = set(events_df['student_id'].astype(str))

    except Exception as e:
        print(f"ERROR: Could not read from database. {e}")
        return

    at_risk_students = students_df[students_df['at_risk_status'] == 'At-Risk']
    
    if at_risk_students.empty:
        print("👍 No at-risk students found.")
        return
        
    new_cases_found = 0
    for index, student in at_risk_students.iterrows():
        student_id = str(student['student_id'])
        
        # Check if an event for this student is already open
        if student_id not in processing_ids:
            new_cases_found += 1
            print(f"\nFound new at-risk case: Student {student_id}")
            details = {
                "department": student['department'],
                "reason": "Flagged by initial risk model."
            }
            # Post the event to the bus
            post_event_to_bus(student_id, "at_risk_flagged", details)

    if new_cases_found == 0:
        print("👍 All at-risk students are already being processed.")

    print("\n🤖 Watcher Agent: Scan complete.")

if __name__ == "__main__":
    run_watcher_agent()