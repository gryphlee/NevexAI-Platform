# email_sender.py
import smtplib
import ssl
from email.message import EmailMessage
import os
from dotenv import load_dotenv

# Load credentials from .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# --- Email Templates ---
TEMPLATES = {
    "Day 1 Check-In": {
        "subject": "Checking In - Student Success Platform",
        "body": """
        Hi {student_name},

        This is a quick, automated check-in from the Student Success Platform. We noticed you may be facing some challenges in your coursework recently.

        Hope everything is okay. Just a reminder that you can find lecture notes and resources on the student dashboard.

        No need to reply, just wanted to reach out.

        Regards,
        Your Automated Academic Advisor
        """
    },
    "Day 3 Follow-Up": {
        "subject": "Following Up - Academic Support Available",
        "body": """
        Hi {student_name},

        Following up on my last message. We're here to help if you're facing any difficulties. Your success is our top priority.

        Your advisor has opened up their schedule to help. You can book a 15-minute slot directly on their calendar to create a plan to get back on track.

        **Book a time here: https://calendly.com/leenatividad5/30min**

        Please schedule a time that works for you.

        Regards,
        Your Automated Academic Advisor
        """
    }
}

def send_outreach_email(receiver_email, student_name, template_name):
    """
    Sends a real, templated outreach email to a student.
    """
    if not SENDER_EMAIL or not EMAIL_PASSWORD:
        print("    -> 📧 Email credentials not found in .env file. Skipping email.")
        return False
    
    template = TEMPLATES.get(template_name)
    if not template:
        print(f"    -> 📧 Email template '{template_name}' not found. Skipping email.")
        return False

    # Personalize the email
    subject = template['subject']
    body = template['body'].format(student_name=student_name)
    
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email
    msg.set_content(body)

    context = ssl.create_default_context()
    print(f"    -> 📧 Sending REAL email using template '{template_name}' to {receiver_email}...")
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(SENDER_EMAIL, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print("    -> ✅ Email sent successfully.")
        return True
    except Exception as e:
        print(f"    -> ❌ FAILED to send email. Error: {e}")
        return False