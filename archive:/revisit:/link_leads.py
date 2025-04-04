# pylint: disable = import-error

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def link_leads():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Link shopify_orders → leads
    cur.execute(
        "SELECT id, customer_email FROM shopify_orders WHERE lead_id IS NULL")
    orders = cur.fetchall()

    for order_id, email in orders:
        cur.execute(
            "SELECT id FROM leads WHERE LOWER(email) = LOWER(%s)", (email,))
        result = cur.fetchone()
        if result:
            lead_id = result[0]
            cur.execute(
                "UPDATE shopify_orders SET lead_id = %s WHERE id = %s", (lead_id, order_id))

    # Link abandoned_checkouts → leads
    cur.execute(
        "SELECT id, customer_email FROM abandoned_checkouts WHERE lead_id IS NULL")
    checkouts = cur.fetchall()

    for checkout_id, email in checkouts:
        cur.execute(
            "SELECT id FROM leads WHERE LOWER(email) = LOWER(%s)", (email,))
        result = cur.fetchone()
        if result:
            lead_id = result[0]
            cur.execute(
                "UPDATE abandoned_checkouts SET lead_id = %s WHERE id = %s", (lead_id, checkout_id))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Linked leads to orders and abandoned checkouts.")


if __name__ == "__main__":
    link_leads()
