# email_tester.py (Final version with explicit path)
import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# --- NEW FIX: Explicitly define the path to the .env file ---
# This gets the directory where the script is running and joins it with '.env'
script_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(script_dir, '.env')

print(f"--- SCRIPT STARTED: Forcing load from path ---")
print(f"Attempting to load .env file from: {dotenv_path}")
was_loaded = load_dotenv(dotenv_path=dotenv_path)
print(f"Was .env file loaded successfully? -> {was_loaded}")
print("------------------------------------------------")

# Load credentials from .env file
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_test_email(receiver_email):
    """Sends a simple test email."""
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        print("❌ ERROR: SENDER_EMAIL or EMAIL_PASSWORD not found in environment.")
        print(f"   Value found for SENDER_EMAIL: {SENDER_EMAIL}")
        print(f"   Value found for EMAIL_PASSWORD: {EMAIL_PASSWORD}")
        return

    # Create the email message
    subject = "AI Agent Test Email"
    body = "This is a test message from the Python Student Success Platform. If you received this, the email configuration is working correctly!"
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg.set_content(body)

    # Send the email
    context = ssl.create_default_context()
    print(f"📧 Attempting to send test email from '{SENDER_EMAIL}' to '{receiver_email}'...")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("✅ Success! Test email sent.")
    except Exception as e:
        print(f"❌ FAILED to send email. Error: {e}")

if __name__ == "__main__":
    test_receiver = "email_address_you_can_check@example.com"
    send_test_email(test_receiver)