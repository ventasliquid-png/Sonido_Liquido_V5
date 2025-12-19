
import sqlite3
import time

def migrate():
    db_path = 'pilot.db'
    max_retries = 5
    retry_delay = 1

    for i in range(max_retries):
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            cur = conn.cursor()
            
            # Check existing columns
            cur.execute('PRAGMA table_info(pedidos)')
            columns = [col[1] for col in cur.fetchall()]
            
            to_add = [
                ('tipo_facturacion', 'VARCHAR DEFAULT "X"'),
                ('origen', 'VARCHAR DEFAULT "DIRECTO"'),
                ('fecha_compromiso', 'DATETIME'),
                ('liberado_despacho', 'BOOLEAN DEFAULT 0')
            ]
            
            for col_name, col_def in to_add:
                if col_name not in columns:
                    print(f"Agregando columna {col_name}...")
                    cur.execute(f"ALTER TABLE pedidos ADD COLUMN {col_name} {col_def}")
                else:
                    print(f"La columna {col_name} ya existe.")
            
            conn.commit()
            print("✅ Migración completada exitosamente.")
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                print(f"Base de datos bloqueada, reintentando {i+1}/{max_retries}...")
                time.sleep(retry_delay)
            else:
                print(f"🔥 Error operacional: {e}")
                break
        except Exception as e:
            print(f"🔥 Error inesperado: {e}")
            break

if __name__ == "__main__":
    migrate()
