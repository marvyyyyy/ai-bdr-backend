# pylint: disable=missing-module-docstring,missing-function-docstring, import-error, import-outside-toplevel, broad-except, wrong-import-order

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
SEQUENCE_ID = os.getenv("SEQUENCE_ID")  # Load sequence ID from .env

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Fetch all lead IDs
cur.execute("SELECT id FROM leads")
lead_ids = [row[0] for row in cur.fetchall()]

# Enroll each lead into the sequence
for lead_id in lead_ids:
    cur.execute("""
        INSERT INTO sequence_enrollments (lead_id, sequence_id, current_step, status)
        VALUES (%s, %s, %s, %s)
    """, (lead_id, SEQUENCE_ID, 1, "active"))

conn.commit()
cur.close()
conn.close()
print(f"✅ Enrolled {len(lead_ids)} leads into sequence {SEQUENCE_ID}")
