import sqlite3
import os

# Path to DB
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "pilot.db")

def add_column(cursor, table, col_name, col_type):
    try:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}")
        print(f"[SUCCESS] Added column '{col_name}' to table '{table}'")
    except sqlite3.OperationalError as e:
        if "duplicate column" in str(e).lower():
            print(f"[INFO] Column '{col_name}' already exists in '{table}'")
        else:
            print(f"[ERROR] Could not add column '{col_name}': {e}")

def main():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] Database file not found at {DB_PATH}")
        return

    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Add 'piso' column
        add_column(cursor, "domicilios", "piso", "VARCHAR")
        
        # Add 'depto' column
        add_column(cursor, "domicilios", "depto", "VARCHAR")

        conn.commit()
        print("Schema update completed successfully.")
    except Exception as e:
        print(f"[FATAL ERROR] {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
