
import sqlite3
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "pilot.db"

def cleanup_pilot():
    if not DB_PATH.exists():
        print("❌ Error: pilot.db not found")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # CUTOFF DATE: Today (2026-01-15 00:00:00)
    # We want to delete ANY client created >= today.
    # Assuming 'created_at' format is 'YYYY-MM-DD HH:MM:SS.ssssss'
    
    cutoff_date = "2026-01-14 23:59:59"
    
    print(f"--- OPERACIÓN ESCOBA: Limpiando pilot.db (New Imports > {cutoff_date}) ---")
    
    # Check count before
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_before = cursor.fetchone()[0]
    print(f"Clientes Antes: {total_before}")
    
    # Find IDs to delete (Visual check)
    cursor.execute("SELECT id, razon_social, created_at FROM clientes WHERE created_at > ?", (cutoff_date,))
    to_delete = cursor.fetchall()
    print(f"Clientes a eliminar (Hoy): {len(to_delete)}")

    if len(to_delete) == 0:
        print("Nada que limpiar (Hoy).")
        conn.close()
        return

    # Execute DELETE
    cursor.execute("DELETE FROM clientes WHERE created_at > ?", (cutoff_date,))
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"✅ {deleted_count} clientes de baja del padrón operativo.")
    
    # Check count after
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_after = cursor.fetchone()[0]
    print(f"Clientes Restantes: {total_after} (Deben ser ~4-5 originales)")
    
    conn.close()

if __name__ == "__main__":
    cleanup_pilot()
