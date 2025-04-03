import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from send_test_email import send_email

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
    SELECT se.id, se.lead_id, se.sequence_id, se.current_step, se.last_sent_at, l.email
    FROM sequence_enrollments se
    JOIN leads l ON se.lead_id = l.id
    WHERE se.status = 'active'
""")
enrollments = cur.fetchall()

for enrollment in enrollments:
    enrollment_id, lead_id, sequence_id, current_step, last_sent_at, email = enrollment

    cur.execute("""
        SELECT subject, body, delay_days
        FROM sequence_steps
        WHERE sequence_id = %s AND step_number = %s
    """, (sequence_id, current_step))
    step = cur.fetchone()
    if not step:
        continue
    subject, body, delay_days = step

    if last_sent_at and datetime.utcnow() < last_sent_at + timedelta(days=delay_days):
        continue

    send_email(email, subject, body)

    cur.execute("""
        UPDATE sequence_enrollments
        SET current_step = current_step + 1, last_sent_at = %s
        WHERE id = %s
    """, (datetime.utcnow(), enrollment_id))

conn.commit()
cur.close()
conn.close()
print("✅ Sequence processing complete.")
