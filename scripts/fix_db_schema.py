import sqlite3

db_path = "pilot.db"

def inspect_schema():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(vinculos)")
        columns = cursor.fetchall()
        print("Columns in 'vinculos' table:")
        found = False
        for col in columns:
            print(f" - {col[1]} ({col[2]})")
            if col[1] == 'tipo_contacto_id':
                found = True
        
        if not found:
            print("\n[MISSING] Column 'tipo_contacto_id' is MISSING.")
            print("Attempting to add it...")
            try:
                cursor.execute("ALTER TABLE vinculos ADD COLUMN tipo_contacto_id VARCHAR")
                conn.commit()
                print("[SUCCESS] Column added successfully.")
            except Exception as e:
                print(f"[ERROR] Could not add column: {e}")
        else:
            print("\n[OK] Column 'tipo_contacto_id' exists.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_schema()
