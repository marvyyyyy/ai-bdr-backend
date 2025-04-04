# pylint: disable = import-error

import csv
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

with open('shopify_orders_export_1.csv', newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute("""
            INSERT INTO shopify_orders (order_id, customer_email, total_price, order_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
        """, (
            row['Name'],
            row['Email'],
            float(row['Total'].replace('$', '').replace(',', '').strip() or 0),
            datetime.strptime(row['Created at'], '%Y-%m-%d %H:%M:%S %z')
        ))

conn.commit()
cur.close()
conn.close()
