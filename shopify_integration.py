# pylint: disable=missing-module-docstring,missing-function-docstring, import-error, import-outside-toplevel, broad-except, wrong-import-order, fixme

# TODO: Fix customer_email fallback logic (def sync_abandoned_checkouts section)
# Right now, we're only using `checkout.email`, but many records miss `customer_email`.
# Later, improve this by safely extracting customer.email from checkout.customer if available.

import shopifyapi as shopify
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

SHOP_URL = os.getenv("SHOPIFY_URL")
ACCESS_TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")


def connect_to_shopify():
    shopify.ShopifyResource.set_site(f"https://{SHOP_URL}")
    session = shopify.Session(SHOP_URL, "2025-01", ACCESS_TOKEN)
    shopify.ShopifyResource.activate_session(session)


def sync_shopify_customers():
    connect_to_shopify()
    customers = shopify.Customer.find()
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for customer in customers:
        email = customer.email
        if not email:
            continue

        first_name = customer.first_name or ''
        last_name = customer.last_name or ''
        phone = customer.phone or ''
        total_spent = customer.total_spent or 0
        orders_count = customer.orders_count or 0

        # Insert into leads if email doesn't already exist
        cur.execute("""
            INSERT INTO leads (email, first_name, last_name, phone, total_spent, orders_count, lead_source)
            VALUES (%s, %s, %s, %s, %s, %s, 'shopify')
            ON CONFLICT (email) DO NOTHING
        """, (email, first_name, last_name, phone, total_spent, orders_count))

    conn.commit()
    cur.close()
    conn.close()
    return f"✅ Synced {len(customers)} customers from Shopify."


def sync_shopify_orders():
    connect_to_shopify()
    orders = shopify.Order.find()
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    inserted_count = 0

    for order in orders:
        email = order.email
        total_price = float(order.total_price) if order.total_price else 0.0
        order_id = str(order.id)
        order_date = order.created_at

        if not email:
            continue

        # Find matching lead
        cur.execute("SELECT id FROM leads WHERE email = %s", (email,))
        lead_result = cur.fetchone()
        if not lead_result:
            continue

        lead_id = lead_result[0]

        # Insert order
        cur.execute("""
            INSERT INTO shopify_orders (customer_email, total_price, order_id, order_date, lead_id)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (order_id) DO NOTHING
        """, (email, total_price, order_id, order_date, lead_id))

        inserted_count += 1

    conn.commit()
    cur.close()
    conn.close()
    return f"✅ Synced {inserted_count} orders from Shopify."


def sync_abandoned_checkouts():
    connect_to_shopify()
    checkouts = shopify.Checkout.find()
    for checkout in checkouts:
        print("🔍 Full checkout object:")
        print(checkout.to_dict())

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for checkout in checkouts:
        # Use fallback logic: prefer checkout.email, fall back to checkout.customer.email
        email = checkout.email
        customer_email = getattr(checkout.customer, 'email', None) if getattr(
            checkout, 'customer', None) else None

        # Log what we found
        print(f"📬 customer.email: {customer_email} | fallback email: {email}")

        abandoned_at = checkout.created_at
        checkout_id = str(checkout.id)

        product_titles = []
        for item in checkout.line_items:
            product_titles.append(item.title)
        product_name = ", ".join(product_titles)

        # Check if the combination of checkout_id and product_name already exists
        cur.execute("""
            SELECT 1 FROM abandoned_checkouts
            WHERE checkout_id = %s AND product_name = %s
        """, (checkout_id, product_name))
        exists = cur.fetchone()

        if not exists:
            cur.execute("""
                INSERT INTO abandoned_checkouts 
                (customer_email, email, abandoned_at, checkout_id, product_name)
                VALUES (%s, %s, %s, %s, %s)
            """, (customer_email, email, abandoned_at, checkout_id, product_name))

    conn.commit()
    cur.close()
    conn.close()

    return f"✅ Synced {len(checkouts)} abandoned checkouts from Shopify."
