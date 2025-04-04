# Placeholder if needed – Shopify doesn’t export abandoned carts by default
# Often, these are tracked via app/webhooks. You might not have a file for this.
# But here's a basic version if you manually export it.

import csv
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

with open('abandoned_carts.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute("""
            INSERT INTO abandoned_carts (cart_id, email, recovery_url, abandoned_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (cart_id) DO NOTHING
        """, (
            row['Cart ID'],
            row['Email'],
            row['Recovery URL'],
            datetime.strptime(row['Abandoned At'], '%Y-%m-%d %H:%M:%S')
        ))

conn.commit()
cur.close()
conn.close()
