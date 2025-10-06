import pandas as pd
import bcrypt
import getpass  # For securely typing passwords
from sqlalchemy import create_engine, text

# --- Database Setup ---
# Connect to the same database the FastAPI backend uses
DB_URI = 'sqlite:///university.db'
engine = create_engine(DB_URI)

def add_user():
    """
    A command-line script to add a new user (Admin, Teacher, etc.)
    to the 'users' table in the database.
    """
    print("\n--- Add New User to Database ---")
    
    try:
        # Get user details from command line
        username = input("Enter new username: ")
        
        # Check if user already exists in the database
        with engine.connect() as connection:
            check_query = text("SELECT username FROM users WHERE username = :username")
            existing_user = connection.execute(check_query, {"username": username}).fetchone()
        
        if existing_user:
            print(f"\n❌ ERROR: Username '{username}' already exists. Please choose another.")
            return

        # Get password securely without showing it on screen
        password = getpass.getpass("Enter password: ")
        password_confirm = getpass.getpass("Confirm password: ")

        if password != password_confirm:
            print("\n❌ ERROR: Passwords do not match.")
            return
            
        role = input("Enter role (Admin, Teacher, Parent, Student): ").capitalize()
        student_id = input("Enter associated Student ID (or leave blank): ")
        student_id = student_id if student_id else None


        # Hash the password
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        # Create a DataFrame for the new user
        new_user_data = {
            'username': [username],
            'password': [hashed_password.decode('utf-8')],
            'role': [role],
            'student_id': [student_id]
        }
        new_user_df = pd.DataFrame(new_user_data)

        # Append the new user to the 'users' table in the database
        new_user_df.to_sql('users', con=engine, if_exists='append', index=False)

        print(f"\n✅ Success! User '{username}' with role '{role}' has been created in the database.")

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please ensure the 'users' table exists. You may need to run setup_database.py first.")

# This makes the script runnable from the command line
if __name__ == "__main__":
    add_user()