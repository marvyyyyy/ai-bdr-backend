# pylint: disable=unused-variable, unused-argument, too-many-locals, too-many-statements, too-many-branches, too-many-return-statements, broad-except, missing-function-docstring, wrong-import-order

import psycopg2
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from send_test_email import send_email  # re-use your existing send function!

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def process_sequences():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Get active enrollments that haven't had a step recently
    cur.execute("""
        SELECT se.id, se.lead_id, se.sequence_id, se.current_step, se.last_sent_at, l.email
        FROM sequence_enrollments se
        JOIN leads l ON se.lead_id = l.id
        WHERE se.status = 'active'
    """)
    enrollments = cur.fetchall()

    for enrollment in enrollments:
        enrollment_id, lead_id, sequence_id, current_step, last_sent_at, email = enrollment

        # Get the step details
        cur.execute("""
            SELECT subject, body, delay_days
            FROM sequence_steps
            WHERE sequence_id = %s AND step_number = %s
        """, (sequence_id, current_step))
        step = cur.fetchone()

        if not step:
            print(f"❌ No step {current_step} found for sequence {sequence_id}")
            continue

        subject, body, delay_days = step

        # Check if it's time to send this step
        now = datetime.utcnow()
        if last_sent_at:
            wait_until = last_sent_at + timedelta(days=delay_days)
            if now < wait_until:
                print(f"⏳ Waiting for next step for {email}")
                continue

        # Send the email using your send_email helper
        try:
            send_email(email, subject, body)
            print(f"✅ Sent step {current_step} to {email}")
        except Exception as e:
            print(f"❌ Error sending to {email}: {e}")
            continue

        # Check if there is a next step
        cur.execute("""
            SELECT COUNT(*) FROM sequence_steps
            WHERE sequence_id = %s AND step_number = %s
        """, (sequence_id, current_step + 1))
        next_step_exists = cur.fetchone()[0] > 0

        # Update sequence_enrollments
        if next_step_exists:
            cur.execute("""
                UPDATE sequence_enrollments
                SET current_step = %s, last_sent_at = %s
                WHERE id = %s
            """, (current_step + 1, now, enrollment_id))
        else:
            cur.execute("""
                UPDATE sequence_enrollments
                SET status = 'completed', last_sent_at = %s
                WHERE id = %s
            """, (now, enrollment_id))

    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    process_sequences()
    print("✅ Processed sequences successfully.")
