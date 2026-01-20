import sqlite3
import os
import sys

db_path = os.path.join('backend', 'data', 'pilot.db')

print(f"--- DIAGNOSTICO DE DAÑOS ---")
print(f"Objetivo: {db_path}")

if not os.path.exists(db_path):
    print(f"CRITICAL: Archivo {db_path} NO ENCONTRADO.")
    sys.exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. INTEGRIDAD FISICA
    print(f"Ejecutando PRAGMA integrity_check...")
    cursor.execute("PRAGMA integrity_check")
    result = cursor.fetchone()
    integrity = result[0] if result else "UNKNOWN"
    print(f"INTEGRIDAD: {integrity}")

    if integrity != "ok":
         print("ALERTA: Integridad de base de datos comprometida.")

    # 2. CONSISTENCIA DE DATOS
    print(f"Consultando SELECT COUNT(*) FROM clientes...")
    cursor.execute("SELECT COUNT(*) FROM clientes")
    count = cursor.fetchone()[0]
    print(f"CLIENTES_COUNT: {count}")
    
    conn.close()

except Exception as e:
    print(f"ERROR DURANTE DIAGNOSTICO: {e}")
    sys.exit(1)
