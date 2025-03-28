"""Script to import Gmail contacts from a CSV file into the leads table."""

# pylint: disable = import-error
import csv
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


def import_gmail_contacts(csv_file_path):
    """
    Import Gmail contacts from a CSV file into a PostgreSQL database.

    :param csv_file_path: The path to the CSV file containing the contacts.
    """
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            count = 0

            for row in reader:
                email = row.get("E-mail 1 - Value") or row.get("Email")
                if email:
                    pass
                else:
                    continue

                cur.execute("SELECT 1 FROM leads WHERE email = %s", (email,))
                if cur.fetchone():
                    continue

                cur.execute("""
                    INSERT INTO leads (email, lead_source)
                    VALUES (%s, %s)
                """, (email, "Sample Pack Email List ::: * myContacts"))
                count += 1

            conn.commit()
            print(f"✅ Imported {count} Gmail contacts.")

    except (psycopg2.OperationalError, psycopg2.Error) as e:
        print(f"Error occurred: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    import_gmail_contacts("gmail_contacts.csv")
