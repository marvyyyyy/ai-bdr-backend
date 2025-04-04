# pylint: disable = import-error

import csv
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def import_shopify_customers(csv_file_path):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        count = 0

        for row in reader:
            email = row.get("Email", "").strip()
            if not email:
                continue

            first_name = row.get("First Name", "").strip()
            last_name = row.get("Last Name", "").strip()
            phone = row.get("Phone", "").strip()
            total_spent = row.get("Total Spent", "0").replace("$", "").strip()
            orders_count = row.get("Orders Count", "0").strip()

            # Avoid duplicates
            cur.execute("SELECT 1 FROM leads WHERE email = %s", (email,))
            if cur.fetchone():
                continue

            cur.execute("""
                INSERT INTO leads (email, first_name, last_name, phone, total_spent, orders_count, lead_source)
                VALUES (%s, %s, %s, %s, %s, %s, 'shopify')
            """, (email, first_name, last_name, phone, total_spent, orders_count))
            count += 1

        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ Imported {count} Shopify customers.")


if __name__ == "__main__":
    import_shopify_customers("shopify_customers_export.csv")
