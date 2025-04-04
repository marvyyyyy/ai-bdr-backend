# pylint: disable=missing-module-docstring,missing-function-docstring, import-error, import-outside-toplevel, broad-except, wrong-import-order

import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def enroll_lead_in_sequence(lead_id, sequence_id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        SELECT id, delay_days
        FROM sequence_steps
        WHERE sequence_id = %s
        ORDER BY step_number ASC
    """, (sequence_id,))
    steps = cur.fetchall()

    if not steps:
        return {"error": "No steps found for this sequence."}

    cur.execute("""
        INSERT INTO sequence_enrollments (lead_id, sequence_id, status, current_step, last_sent_at)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (lead_id, sequence_id, 'active', 0, None))
    enrollment_id = cur.fetchone()[0]

    for step_id, delay_days in steps:
        scheduled_at = datetime.utcnow()  # Can add delay logic later
        cur.execute("""
            INSERT INTO email_engagements (enrollment_id, step_id, status, scheduled_at)
            VALUES (%s, %s, %s, %s)
        """, (enrollment_id, step_id, 'pending', scheduled_at))

    conn.commit()
    cur.close()
    conn.close()

    return {
        "enrollment_id": enrollment_id,
        "steps_created": len(steps),
        "message": "✅ Lead enrolled successfully."
    }
