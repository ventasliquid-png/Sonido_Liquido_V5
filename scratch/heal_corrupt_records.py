
import sqlite3
import os

DB_PATH = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

def heal_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("--- [HEALING] Eliminando remitos zombis sin pedido ---")
    # Borrar el remito que causa el bloqueo
    cursor.execute("DELETE FROM remitos WHERE numero_legal = '0016-00001-00002529';")
    print(f"Filas eliminadas: {cursor.rowcount}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    heal_db()
