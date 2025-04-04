# import_abandoned_checkouts.py
# pylint: disable = import-error

import csv
import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def import_abandoned_checkouts():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    with open('shopify_checkouts_export_1.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0

        for row in reader:
            checkout_id = row.get("Id")
            email = row.get("Email")
            total_price = row.get("Total Price")
            created_at = row.get("Created at")

            if not checkout_id or not email:
                continue

            try:
                cur.execute(
                    "SELECT 1 FROM abandoned_checkouts WHERE checkout_id = %s", (checkout_id,))
                if cur.fetchone():
                    continue

                cur.execute("""
                    INSERT INTO abandoned_checkouts (checkout_id, customer_email, total_price, checkout_date)
                    VALUES (%s, %s, %s, %s)
                """, [
                    checkout_id,
                    email,
                    float(total_price) if total_price else 0.0,
                    datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S %z')
                ])

                count += 1
            except psycopg2.Error as e:
                print(f"❌ Error importing row {checkout_id}: {e}")
                continue

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Imported {count} abandoned checkouts.")


if __name__ == "__main__":
    import_abandoned_checkouts()
