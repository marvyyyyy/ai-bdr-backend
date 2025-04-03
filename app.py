from flask import Flask, jsonify
from dotenv import load_dotenv
import os
import psycopg2

# Load environment variables from .env
load_dotenv()

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


# Only used for local testing
if __name__ == '__main__':
    app.run(debug=True)
