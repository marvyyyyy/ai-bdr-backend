import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def sync_shopify_customers():
    df = pd.read_csv("shopify_customers_export.csv")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    imported = 0
    for _, row in df.iterrows():
        email = row.get("Email")
        if not email:
            continue
        cur.execute("SELECT 1 FROM leads WHERE email = %s", (email,))
        if not cur.fetchone():
            cur.execute("INSERT INTO leads (email) VALUES (%s)", (email,))
            imported += 1
    conn.commit()
    cur.close()
    conn.close()
    print(f"Imported {imported} shopify customers")

def sync_shopify_orders():
    df = pd.read_csv("shopify_orders_export_1.csv")
    print(f"Imported {len(df)} shopify orders")  # Placeholder for real logic

def sync_abandoned_checkouts():
    df = pd.read_csv("shopify_checkouts_export_1.csv")
    print(f"Imported {len(df)} abandoned checkouts")  # Placeholder for real logic
