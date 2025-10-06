# setup_database.py
import sqlite3

# --- Configuration ---
DB_FILE = 'university.db'

def setup_database():
    """
    Connects to the SQLite database and creates the necessary tables
    if they do not already exist.
    """
    print(f"--- Setting up database: {DB_FILE} ---")
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # --- Create the 'users' table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                student_id TEXT
            )
        ''')
        print("✅ 'users' table is ready.")

        # --- Create the 'students' table ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY,
                quiz_avg REAL,
                assignment_submissions INTEGER,
                attendance_percentage REAL,
                lms_hours REAL,
                at_risk_status TEXT,
                department TEXT,
                year_level TEXT,
                parent_username TEXT,
                custom_data TEXT
            )
        ''')
        print("✅ 'students' table is ready.")

        # --- NEW: Create the 'events' table (The Event Bus) ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                event_id TEXT PRIMARY KEY,
                student_id TEXT,
                event_type TEXT NOT NULL,
                payload TEXT,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        print("✅ 'events' table (Event Bus) is ready.")


        # Commit the changes and close the connection
        conn.commit()
        conn.close()
        
        print("\n--- Database setup complete! ---")

    except sqlite3.Error as e:
        print(f"\n❌ An error occurred: {e}")

if __name__ == "__main__":
    setup_database()