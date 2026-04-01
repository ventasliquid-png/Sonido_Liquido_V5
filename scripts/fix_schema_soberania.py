import sqlite3
import os

db_path = "pilot_v5x.db"

def fix_schema():
    print(f"--- [FIX] Iniciando Reparación Quirúrgica de Esquema en {db_path} ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. clientes.transporte_habitual_id
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN transporte_habitual_id CHAR(32);")
        print("[OK] Columna 'transporte_habitual_id' inyectada en 'clientes'.")
    except sqlite3.OperationalError as e:
        print(f"[WARN] Columna 'transporte_habitual_id' ya existe o error: {e}")

    # 2. domicilios.flags_estado
    try:
        cursor.execute("ALTER TABLE domicilios ADD COLUMN flags_estado BIGINT DEFAULT 0;")
        print("[OK] Columna 'flags_estado' inyectada en 'domicilios'.")
    except sqlite3.OperationalError as e:
        print(f"[WARN] Columna 'flags_estado' ya existe o error: {e}")

    # 3. productos_costos.margen_sugerido
    try:
        cursor.execute("ALTER TABLE productos_costos ADD COLUMN margen_sugerido NUMERIC DEFAULT 0;")
        print("[OK] Columna 'margen_sugerido' inyectada en 'productos_costos'.")
    except sqlite3.OperationalError as e:
        print(f"[WARN] Columna 'margen_sugerido' ya existe o error: {e}")

    conn.commit()
    conn.close()
    print("--- [FIX] Reparación FINALIZADA ---")

if __name__ == "__main__":
    fix_schema()
