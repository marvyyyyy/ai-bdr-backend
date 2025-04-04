# pylint: disable=no-member, wrong-import-order, broad-except, missing-module-docstring, missing-function-docstring, too-many-locals, too-many-statements

import os
import re
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
TOKEN_FILE = "token_lu.json"
SCOPES = ['https://mail.google.com/']


def check_email_replies():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, "w", encoding="utf-8") as token:
                token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT se.id, l.email, se.last_sent_at
        FROM sequence_enrollments se
        JOIN leads l ON se.lead_id = l.id
        WHERE se.status = 'active'
    """)
    enrollments = cur.fetchall()

    enrollment_lookup = {
        email.lower(): {"enrollment_id": enrollment_id, "last_sent_at": last_sent_at}
        for enrollment_id, email, last_sent_at in enrollments
    }

    response = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        q="is:inbox newer_than:1d"
    ).execute()

    messages = response.get("messages", [])
    print(f"📨 Found {len(messages)} messages in inbox...")

    replies_detected = 0
    reply_emails = []

    for msg in messages:
        msg_detail = service.users().messages().get(
            userId="me", id=msg["id"]
        ).execute()

        headers = msg_detail.get("payload", {}).get("headers", [])
        from_email = next(
            (h["value"] for h in headers if h["name"].lower() == "from"), None)

        if not from_email:
            continue

        match = re.search(r'<(.+?)>', from_email)
        clean_email = match.group(1).lower() if match else from_email.lower()

        if clean_email in enrollment_lookup:
            enrollment_id = enrollment_lookup[clean_email]["enrollment_id"]
            last_sent = enrollment_lookup[clean_email]["last_sent_at"]

            internal_date = int(msg_detail.get("internalDate", 0)) / 1000
            reply_time = datetime.utcfromtimestamp(internal_date)

            if not last_sent or reply_time > last_sent:
                print(
                    f"📥 Reply detected from {clean_email}, updating status to 'replied'...")

                cur.execute("""
                    UPDATE sequence_enrollments
                    SET status = 'replied'
                    WHERE id = %s
                """, (enrollment_id,))
                conn.commit()

                replies_detected += 1
                reply_emails.append(clean_email)

    cur.close()
    conn.close()
    print("✅ Done checking for replies.")

    return {
        "total_messages_checked": len(messages),
        "replies_detected": replies_detected,
        "reply_emails": reply_emails
    }
