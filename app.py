# app.py

# pylint: disable=missing-module-docstring,missing-function-docstring, import-error, import-outside-toplevel, broad-except

import os
import psycopg2
from flask import Flask, jsonify
# Replace 'send_email' with the correct name from the module
from send_test_email import send_email
from shopify_integration import sync_shopify_customers, sync_shopify_orders, sync_abandoned_checkouts

app = Flask(__name__)


# Basic route to check if app is running


@app.route('/')
def home():
    return "✅ Shailu BDR backend is running!"

# Optional: Test DB connection route


@app.route('/test-db')
def test_db():
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        result = cur.fetchone()
        cur.close()
        conn.close()
        return jsonify({"success": True, "db_response": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/send-test-email")
def run_send_test_email():
    try:
        send_email(
            recipient="test@example.com",
            subject="Test Email",
            body="This is a test email from Shailu BDR backend."
        )
        print("✅ Sent test email from lu@shailusounds.com")
        return "✅ Test email sent successfully!"
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return f"❌ Error sending email: {str(e)}", 500


@app.route("/sync-shopify-customers")
def run_sync_shopify_customers():
    result = sync_shopify_customers()
    print(result)
    return result


@app.route("/sync-abandoned-checkouts")
def run_sync_abandoned_checkouts():
    result = sync_abandoned_checkouts()
    print(result)
    return result


@app.route("/sync-shopify-orders")
def run_sync_shopify_orders():
    result = sync_shopify_orders()
    print(result)
    return result


if __name__ == "__main__":
    app.run(debug=True)
