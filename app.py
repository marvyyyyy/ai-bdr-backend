# app.py

# pylint: disable=missing-module-docstring,missing-function-docstring, import-error, import-outside-toplevel, broad-except

import os
import psycopg2
from enroll_leads import enroll_lead_in_sequence
from flask import request
from flask import Flask, jsonify
from flask_cors import CORS
from send_test_email import send_email
from shopify_integration import sync_shopify_customers, sync_shopify_orders, sync_abandoned_checkouts
from check_replies import check_email_replies

app = Flask(__name__)
CORS(app)

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


@app.route("/send-test-email", methods=["POST"])
def run_send_test_email():
    try:
        send_email(
            recipient="test@example.com",
            subject="Test Email",
            body="This is a test email from Shailu BDR backend."
        )
        print("✅ Sent test email from lu@shailusounds.com")
        return jsonify({"status": "success", "message": "✅ Test email sent successfully!"}), 200
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return jsonify({"status": "error", "message": f"❌ Error sending email: {str(e)}"}), 500


@app.route("/sync-shopify-customers", methods=["POST"])
def run_sync_shopify_customers():
    result = sync_shopify_customers()
    print(result)
    return jsonify({"status": "success", "result": result}), 200


@app.route("/sync-abandoned-checkouts", methods=["POST"])
def run_sync_abandoned_checkouts():
    result = sync_abandoned_checkouts()
    print(result)
    return jsonify({"status": "success", "result": result}), 200


@app.route("/sync-shopify-orders", methods=["POST"])
def run_sync_shopify_orders():
    result = sync_shopify_orders()
    print(result)
    return jsonify({"status": "success", "result": result}), 200


@app.route("/check-replies", methods=["POST"])
def run_check_replies():
    result = check_email_replies()
    return jsonify({
        "status": "success",
        "message": "✅ Replies checked successfully.",
        "result": result
    }), 200


@app.route("/enroll-lead", methods=["POST"])
def run_enroll_lead():
    data = request.get_json()
    lead_id = data.get("lead_id")
    sequence_id = data.get("sequence_id")

    if not lead_id or not sequence_id:
        return jsonify({"status": "error", "message": "Missing lead_id or sequence_id"}), 400

    result = enroll_lead_in_sequence(lead_id, sequence_id)
    return jsonify({"status": "success", "result": result}), 200


if __name__ == "__main__":
    app.run(debug=True)
