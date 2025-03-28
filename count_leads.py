# pylint: disable = import-error

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def count_leads():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM leads;")
        count = cur.fetchone()[0]
        print(f"📊 Total leads in the database: {count}")
    except psycopg2.DatabaseError as e:
        print("❌ Database error while checking leads count:", e)
    except Exception as e:
        print("❌ An unexpected error occurred:", e)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    count_leads()
