import csv
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

with open('shopify_checkouts_export_1.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute("""
            INSERT INTO abandoned_checkouts (checkout_id, email, subtotal_price, abandoned_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (checkout_id) DO NOTHING
        """, (
            row['Checkout ID'],
            row['Email'],
            row['Subtotal Price'],
            datetime.strptime(row['Created at'], '%Y-%m-%d %H:%M:%S %z')
        ))

conn.commit()
cur.close()
conn.close()
