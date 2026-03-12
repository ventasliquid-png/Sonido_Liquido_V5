import sqlite3
import os

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot.db"

def migrate():
    print(f"🔧 Migrating {DB_PATH} for Google Agenda fields...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(personas)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "google_resource_name" not in columns:
            print(" -> Adding column: google_resource_name")
            cursor.execute("ALTER TABLE personas ADD COLUMN google_resource_name TEXT")
            cursor.execute("CREATE UNIQUE INDEX ix_personas_google_resource_name ON personas (google_resource_name)")
        else:
            print(" -> google_resource_name already exists.")

        if "google_etag" not in columns:
            print(" -> Adding column: google_etag")
            cursor.execute("ALTER TABLE personas ADD COLUMN google_etag TEXT")
        else:
            print(" -> google_etag already exists.")

        conn.commit()
        print("✅ Migration successful.")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    if os.path.exists(DB_PATH):
        migrate()
    else:
        print(f"❌ Database not found at {DB_PATH}")
