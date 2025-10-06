# communication_manager.py
import json
import os
from datetime import datetime

# --- Configuration ---
DATA_DIR = 'data'
COMMUNICATION_LOG_FILE = os.path.join(DATA_DIR, 'communication_log.json')
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# --- Core Functions ---

def load_log():
    """Loads the communication log from the JSON file."""
    # Create the data directory if it doesn't exist
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    if not os.path.exists(COMMUNICATION_LOG_FILE):
        return {}
    try:
        with open(COMMUNICATION_LOG_FILE, 'r') as f:
            # Handle empty file case
            content = f.read()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_log(log_data):
    """Saves the updated log data to the JSON file."""
    with open(COMMUNICATION_LOG_FILE, 'w') as f:
        json.dump(log_data, f, indent=4)

def get_student_status(student_id):
    """
    Gets the communication status for a specific student.
    Returns the status and the last update time, or (None, None) if not found.
    """
    log = load_log()
    student_record = log.get(str(student_id))
    if student_record:
        return student_record.get('status'), student_record.get('last_update')
    return None, None

def update_student_status(student_id, new_status):
    """
    Updates the status for a student in the communication log.
    Creates a new entry if the student doesn't exist.
    """
    log = load_log()
    current_time = datetime.now().strftime(DATETIME_FORMAT)
    
    log[str(student_id)] = {
        'status': new_status,
        'last_update': current_time
    }
    
    save_log(log)
    print(f"    -> Log Updated: Student {student_id} status set to '{new_status}'.")

# --- Test Block ---
if __name__ == "__main__":
    print("--- Testing Communication Manager ---")
    
    # Simulate updating a student's status
    test_student_id = "2025001"
    print(f"\n1. Updating status for student {test_student_id}...")
    update_student_status(test_student_id, "Day 1 Email Sent")
    
    # Simulate checking that student's status
    print(f"\n2. Checking status for student {test_student_id}...")
    status, last_update = get_student_status(test_student_id)
    if status:
        print(f"   - Found Status: {status}")
        print(f"   - Last Updated: {last_update}")
    else:
        print("   - No status found.")

    # Simulate checking a student who is not in the log yet
    print("\n3. Checking status for a new student (9999999)...")
    status, last_update = get_student_status("9999999")
    if not status:
        print("   - Correctly found no status for the new student.")

    print("\n--- Test Complete ---")
    print(f"Check your '{COMMUNICATION_LOG_FILE}' file to see the result.")