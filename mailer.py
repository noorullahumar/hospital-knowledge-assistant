import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_otp_email(receiver_email, otp_code):
    """Sends a 6-digit OTP to the specified email address."""
    sender_email = os.getenv("EMAIL_USER")
    sender_password = os.getenv("EMAIL_PASS")

    if not sender_email or not sender_password:
        print("Error: Email credentials missing in .env")
        return False

    msg = EmailMessage()
    msg.set_content(f"""
    Your Hospital AI Portal Password Reset Code:
    
    {otp_code}
    
    If you did not request this, please ignore this email.
    """)

    msg['Subject'] = '🔐 Your Password Reset Code'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        # Connect to Gmail's SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender_email, sender_password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False