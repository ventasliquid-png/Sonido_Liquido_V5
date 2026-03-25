import sqlite3
import os

def heal_address_sync():
    db_path = "c:/dev/Sonido_Liquido_V5/pilot_v5x.db"
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # Sync is_active with Bit 0 of bit_identidad
        cursor.execute("""
            UPDATE domicilios 
            SET is_active = (CASE WHEN (bit_identidad & 1) THEN 1 ELSE 0 END)
        """)
        changes = conn.total_changes
        conn.commit()
        print(f"Healed {changes} addresses. is_active is now synced with Bit 0 of bit_identidad.")
        
    finally:
        conn.close()

if __name__ == "__main__":
    heal_address_sync()
