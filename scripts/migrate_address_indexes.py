import sqlite3
import os

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"

def run_migration():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        print("Checking existing indexes...")
        cursor.execute("PRAGMA index_list('domicilios')")
        existing_indexes = [row[1] for row in cursor.fetchall()]

        indexes_to_create = [
            ("ix_domicilios_alias", "alias"),
            ("ix_domicilios_calle", "calle"),
            ("ix_domicilios_localidad", "localidad")
        ]

        for index_name, column_name in indexes_to_create:
            if index_name in existing_indexes:
                print(f"Index {index_name} already exists.")
            else:
                print(f"Creating index {index_name} on {column_name}...")
                cursor.execute(f"CREATE INDEX {index_name} ON domicilios({column_name})")
        
        conn.commit()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    run_migration()
