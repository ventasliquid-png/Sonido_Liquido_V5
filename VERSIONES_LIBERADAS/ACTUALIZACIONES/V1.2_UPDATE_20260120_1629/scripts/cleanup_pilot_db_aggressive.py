
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "pilot.db"

# The 4 Original "Safe" Clients (Recovered from JSON Mirror history)
SAFE_IDS = [
    "2fbeb6ebffc649ff81d1e324f410eed6", # Gelato S.A.
    "d3747f3facc04c1a85025f14984a69ed", # Lácteos de Poblet S.A.
    "4af49a480dca4f87af3871d85c4f5b2c", # EDUARDO DELUCA S.A.C.I.
    "0c2866b2444a4d9b8878ddb88a5dd2e2"  # Consumidor Final
]

def aggressive_cleanup():
    if not DB_PATH.exists():
        print("❌ Error: pilot.db not found")
        return

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print(f"--- OPERACIÓN ESCOBA: Limpieza Agresiva (Keep Safe List) ---")
    
    # Check count before
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_before = cursor.fetchone()[0]
    print(f"Clientes Totales Antes: {total_before}")
    
    # Verify Safe IDs existence
    placeholders = ",".join(["?"] * len(SAFE_IDS))
    cursor.execute(f"SELECT count(*) FROM clientes WHERE id IN ({placeholders})", SAFE_IDS)
    safe_found = cursor.fetchone()[0]
    print(f"Clientes Seguros Encontrados: {safe_found}/{len(SAFE_IDS)}")
    
    if safe_found == 0:
        print("⚠️ ALERTA: No se encontraron los clientes seguros. ¿Estamos en la DB correcta? Abortando para evitar vaciado total.")
        conn.close()
        return

    # Execute DELETE NOT IN
    # We delete everyone who is NOT in the safe list
    cursor.execute(f"DELETE FROM clientes WHERE id NOT IN ({placeholders})", SAFE_IDS)
    deleted_count = cursor.rowcount
    
    conn.commit()
    print(f"✅ {deleted_count} clientes 'intrusos' eliminados.")
    
    # Check count after
    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_after = cursor.fetchone()[0]
    print(f"Clientes Restantes: {total_after} (Deben ser {len(SAFE_IDS)})")
    
    conn.close()

if __name__ == "__main__":
    aggressive_cleanup()
