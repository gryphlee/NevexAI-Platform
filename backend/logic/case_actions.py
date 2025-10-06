# case_actions.py
from sqlalchemy import create_engine, text
from meta_agent_manager import log_system_event
import os
import json

# --- Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
DB_PATH = os.path.join(ROOT_DIR, 'university.db')
DB_URI = f'sqlite:///{DB_PATH}'

def update_event_status(event_id, new_status, payload=None):
    """Updates the status and optionally the payload of an event."""
    engine = create_engine(DB_URI)
    try:
        with engine.connect() as connection:
            if payload:
                update_query = text("UPDATE events SET status = :status, payload = :payload WHERE event_id = :event_id")
                connection.execute(update_query, {"status": new_status, "payload": json.dumps(payload), "event_id": event_id})
            else:
                update_query = text("UPDATE events SET status = :status WHERE event_id = :event_id")
                connection.execute(update_query, {"status": new_status, "event_id": event_id})
            connection.commit()
        return True
    except Exception as e:
        print(f"  -> ❌ ERROR updating event status: {e}")
        return False

def approve_plan(event_id, student_id, approver_username):
    """Handles logic for approving a plan."""
    if update_event_status(event_id, "approved"):
        log_message = f"Plan for event '{event_id}' (Student: {student_id}) was APPROVED by {approver_username}."
        log_system_event(log_message)
        return True, "Plan approved and logged successfully."
    return False, f"Failed to approve plan for event {event_id}."

def modify_plan(event_id, student_id, approver_username, modifications):
    """Handles logic for modifying a plan."""
    log_message = f"Plan for event '{event_id}' (Student: {student_id}) was MODIFIED by {approver_username}. Reason: {modifications}"
    log_system_event(log_message)
    # You could also save the modified plan to the database payload here
    if update_event_status(event_id, "modified"):
        return True, "Plan modifications logged successfully."
    return False, "Failed to log plan modifications."

def reject_plan(event_id, student_id, approver_username, reason, comments):
    """Handles logic for rejecting a plan."""
    log_message = f"Plan for event '{event_id}' (Student: {student_id}) was REJECTED by {approver_username}. Reason: {reason}. Comments: {comments}"
    log_system_event(log_message)
    if update_event_status(event_id, "rejected"):
        return True, "Plan rejection logged successfully."
    return False, "Failed to log plan rejection."