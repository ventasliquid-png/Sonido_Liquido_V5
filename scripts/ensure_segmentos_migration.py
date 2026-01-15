
import sqlite3
import os

def apply_segmentos_migration():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(root_dir, 'pilot.db')
    if not os.path.exists(db_path): db_path = os.path.join(root_dir, 'backend', 'pilot.db')
    
    print(f"Checking Segmentos table in: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("PRAGMA table_info(segmentos)")
        cols = [c[1] for c in cursor.fetchall()]
        if 'nivel' not in cols:
            print("Applying: ALTER TABLE segmentos ADD COLUMN nivel INTEGER DEFAULT 1;")
            cursor.execute("ALTER TABLE segmentos ADD COLUMN nivel INTEGER DEFAULT 1;")
            conn.commit()
            print("✅ Migration applied.")
        else:
            print("INFO: 'nivel' exists.")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_segmentos_migration()
