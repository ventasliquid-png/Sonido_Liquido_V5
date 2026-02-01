import sqlite3
import os

db_path = r'C:\dev\Sonido_Liquido_V5\pilot.db'
vinculo_id = 'a083d634ac3b4ccaabacab4a20eb9ae4' # From debug output

def update_manual():
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print(f"Manually updating role for vinculo {vinculo_id}...")
    cursor.execute("UPDATE vinculos SET rol = 'TEST_MANUAL_UPDATE' WHERE id = ?", (vinculo_id,))
    conn.commit()
    
    # Verify
    cursor.execute("SELECT rol FROM vinculos WHERE id = ?", (vinculo_id,))
    row = cursor.fetchone()
    print(f"New Value in DB: {row[0]}")
    
    conn.close()

if __name__ == "__main__":
    update_manual()
