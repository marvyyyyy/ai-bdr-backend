import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Insert a test sequence
cur.execute("""
    INSERT INTO sequences (name, description)
    VALUES (%s, %s)
    RETURNING id
""", ("Test Sequence", "This is a test sequence"))
sequence_id = cur.fetchone()[0]

# Insert sequence steps
steps = [
    (sequence_id, 1, "Step 1 Subject", "Step 1 Body", 0),
    (sequence_id, 2, "Step 2 Subject", "Step 2 Body", 2),
    (sequence_id, 3, "Step 3 Subject", "Step 3 Body", 5),
]
cur.executemany("""
    INSERT INTO sequence_steps (sequence_id, step_number, subject, body, delay_days)
    VALUES (%s, %s, %s, %s, %s)
""", steps)

conn.commit()
cur.close()
conn.close()
print(f"✅ Sequence {sequence_id} and steps created.")
