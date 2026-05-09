import sqlite3
import os

def migrate():
    # Path a la DB
    db_path = r'C:\dev\Sonido_Liquido_V5\pilot_v5x.db'
    if not os.path.exists(db_path):
        print(f"Error: No se encuentra la DB en {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        print("Añadiendo columna flags_estado a ingesta_facturas_raw...")
        cur.execute("ALTER TABLE ingesta_facturas_raw ADD COLUMN flags_estado BIGINT DEFAULT 1")
        conn.commit()
        print("Migración completada exitosamente.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("La columna ya existe. Omitiendo.")
        else:
            print(f"Error durante la migración: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
