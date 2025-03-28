# pylint: disable = import-error

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def tag_leads():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Tag leads based on abandoned checkout
    cur.execute("""
        SELECT id, customer_email FROM abandoned_checkouts WHERE lead_id IS NULL
    """)
    checkouts = cur.fetchall()

    for checkout_id, email in checkouts:
        cur.execute(
            "SELECT id FROM leads WHERE LOWER(email) = LOWER(%s)", (email,))
        result = cur.fetchone()
        if result:
            lead_id = result[0]
            # Tag as "Abandoned Cart"
            cur.execute(
                "INSERT INTO tags (lead_id, tag_name) VALUES (%s, 'Abandoned Cart')", (lead_id,))
            cur.execute(
                "UPDATE abandoned_checkouts SET lead_id = %s WHERE id = %s", (lead_id, checkout_id))

    # Tag leads based on order value
    cur.execute("""
        SELECT id, customer_email, total_price FROM shopify_orders WHERE lead_id IS NULL
    """)
    orders = cur.fetchall()

    for order_id, email, total_price in orders:
        cur.execute(
            "SELECT id FROM leads WHERE LOWER(email) = LOWER(%s)", (email,))
        result = cur.fetchone()
        if result:
            lead_id = result[0]
            if total_price >= 50:  # High-Value Lead
                # Tag as "High-Value Lead"
                cur.execute(
                    "INSERT INTO tags (lead_id, tag_name) VALUES (%s, 'High-Value Lead')", (lead_id,))
            # Tag as "Repeat Buyer" if they have made a purchase
            cur.execute(
                "INSERT INTO tags (lead_id, tag_name) VALUES (%s, 'Repeat Buyer')", (lead_id,))
            cur.execute(
                "UPDATE shopify_orders SET lead_id = %s WHERE id = %s", (lead_id, order_id))

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tagged leads with behavior-based tags.")


if __name__ == "__main__":
    tag_leads()
