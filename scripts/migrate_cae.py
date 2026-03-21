import sqlite3
import os

db_path = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: No se encuentra la base de datos en {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Migrando tabla remitos...")
    
    try:
        cursor.execute("ALTER TABLE remitos ADD COLUMN cae TEXT")
        print("Columna 'cae' agregada.")
    except sqlite3.OperationalError as e:
        print(f"Aviso: {e}")

    try:
        cursor.execute("ALTER TABLE remitos ADD COLUMN vto_cae DATETIME")
        print("Columna 'vto_cae' agregada.")
    except sqlite3.OperationalError as e:
        print(f"Aviso: {e}")

    conn.commit()
    conn.close()
    print("Migración finalizada.")

if __name__ == "__main__":
    migrate()
