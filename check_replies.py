import os
import psycopg2
import re
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

creds = None
if os.path.exists(TOKEN_FILE):
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as token:
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
lookup = {email.lower(): (id, last_sent) for id, email, last_sent in enrollments}

response = service.users().messages().list(userId="me", labelIds=["INBOX"], q="newer_than:2d").execute()
messages = response.get("messages", [])

for msg in messages:
    msg_detail = service.users().messages().get(userId="me", id=msg["id"]).execute()
    headers = msg_detail.get("payload", {}).get("headers", [])
    from_email = next((h["value"] for h in headers if h["name"].lower() == "from"), None)
    match = re.search(r'<(.+?)>', from_email or "")
    clean_email = match.group(1).lower() if match else (from_email or "").lower()
    if clean_email in lookup:
        enrollment_id, last_sent = lookup[clean_email]
        internal_date = int(msg_detail.get("internalDate", 0)) / 1000
        reply_time = datetime.utcfromtimestamp(internal_date)
        if not last_sent or reply_time > last_sent:
            cur.execute("UPDATE sequence_enrollments SET status = 'replied' WHERE id = %s", (enrollment_id,))
            conn.commit()

cur.close()
conn.close()
print("✅ Done checking replies.")
