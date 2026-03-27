import sqlite3

DB_PATH = 'pilot_v5x.db'

def reparacion_estructural():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("\n--- INICIANDO REPARACIÓN ESTRUCTURAL ---")
    
    # 1. Cirugía de Clientes
    print("[*] Agregando 'transporte_habitual_id' a clientes...")
    try:
        cursor.execute("ALTER TABLE clientes ADD COLUMN transporte_habitual_id INTEGER")
        print("[OK] Columna agregada.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("[SKIP] La columna ya existe.")
        else:
            print(f"[ERR] Error inesperado en clientes: {e}")

    # 2. Saneamiento de Rubros
    print("[*] Reparando 'margen_default' NULL en rubros...")
    try:
        cursor.execute("UPDATE rubros SET margen_default = 0.0 WHERE margen_default IS NULL")
        print(f"[OK] {cursor.rowcount} rubros actualizados.")
    except Exception as e:
        print(f"[ERR] Error en rubros: {e}")

    # 3. Cirugía de Domicilios
    print("[*] Reparando 'domicilios' (Genoma 64-bit)...")
    try:
        cursor.execute("ALTER TABLE domicilios ADD COLUMN flags_estado BIGINT DEFAULT 0")
        print("[OK] flags_estado agregado a domicilios.")
    except sqlite3.OperationalError:
        print("[SKIP] flags_estado ya existe en domicilios.")

    # 4. Cirugía de Puente Domicilios-Clientes
    print("[*] Reparando tabla puente 'domicilios_clientes'...")
    try:
        cursor.execute("ALTER TABLE domicilios_clientes ADD COLUMN flags BIGINT DEFAULT 2097152")
        print("[OK] flags agregado a domicilios_clientes.")
    except sqlite3.OperationalError:
        print("[SKIP] flags ya existe en domicilios_clientes.")

    # 5. Auditoría de Roca Sólida en productos_costos
    print("[*] Verificando consistencia en productos_costos...")
    cursor.execute("PRAGMA table_info(productos_costos)")
    cols = [row[1] for row in cursor.fetchall()]
    print(f" [+] Columnas actuales: {cols}")
    
    if "margen_sugerido" not in cols:
        print(" [!] Falta 'margen_sugerido'. Agregando...")
        cursor.execute("ALTER TABLE productos_costos ADD COLUMN margen_sugerido NUMERIC DEFAULT 0.0")
        print(" [OK] margen_sugerido agregado.")
    else:
        print(" [OK] margen_sugerido presente.")

    conn.commit()
    conn.close()
    print("\n--- REPARACIÓN FINALIZADA ---")

if __name__ == "__main__":
    reparacion_estructural()
