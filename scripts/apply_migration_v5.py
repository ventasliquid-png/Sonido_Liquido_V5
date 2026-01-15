
import sqlite3
import os

def apply_migration():
    # LOCATE DB
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(root_dir, 'pilot.db')
    
    if not os.path.exists(db_path):
        db_path = os.path.join(root_dir, 'backend', 'pilot.db')
    
    print(f"Applying migration to: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column exists
        cursor.execute("PRAGMA table_info(listas_precios)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'orden_calculo' not in columns:
            print("Applying: ALTER TABLE listas_precios ADD COLUMN orden_calculo INTEGER;")
            cursor.execute("ALTER TABLE listas_precios ADD COLUMN orden_calculo INTEGER;")
            conn.commit()
            print("✅ Migration applied successfully.")
        else:
            print("INFO: 'orden_calculo' already exists.")
            
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    apply_migration()
