import sqlite3
import os

DB_PATH = 'pilot_v5x.db'

def migrate():
    print(f"[*] Conectando a {DB_PATH}...")
    if not os.path.exists(DB_PATH):
        print(f"[!] Error: {DB_PATH} no existe.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Verificar tabla productos_costos
    print("[*] Verificando tabla 'productos_costos'...")
    cursor.execute("PRAGMA table_info(productos_costos)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'margen_sugerido' not in columns:
        print("[+] Agregando columna 'margen_sugerido' a 'productos_costos'...")
        try:
            cursor.execute("ALTER TABLE productos_costos ADD COLUMN margen_sugerido FLOAT DEFAULT 0.0")
            print("[OK] Columna agregada.")
        except Exception as e:
            print(f"[!] Error al agregar columna: {e}")
    else:
        print("[OK] La columna 'margen_sugerido' ya existe.")

    # 2. Verificar otras tablas si es necesario
    # Agregamos esto por si acaso el usuario detectó otras
    
    conn.commit()
    conn.close()
    print("[*] Migración finalizada.")

if __name__ == "__main__":
    migrate()
