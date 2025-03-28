"""
send_test_email.py — Sends a test email using environment variables and Gmail SMTP.
"""

import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def send_test_email():
    """Sends a test email using environment variables and Gmail SMTP."""
    try:
        subject = "✅ Test Email from the AI BDR App"
        body = (
            "This is a test email sent from lu@shailusounds.com via Python!"
        )
        sender = os.getenv("EMAIL_USERNAME")
        recipient = "a.ferdousian94@gmail.com"

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        with smtplib.SMTP(os.getenv("EMAIL_HOST"), int(os.getenv("EMAIL_PORT"))) as server:
            server.starttls()
            server.login(sender, os.getenv("EMAIL_PASSWORD"))
            server.send_message(msg)

        print("✅ Test email sent successfully!")

    except smtplib.SMTPException as e:
        print("❌ Failed to send email:", e)

if __name__ == "__main__":
    send_test_email()
