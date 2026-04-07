import sqlite3
import os

DEV_DB = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"
PROD_DB = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

def find_duplicates(db_path, label):
    if not os.path.exists(db_path):
        print(f" [!] Error: {label} DB not found in {db_path}")
        return
    
    print(f"\n--- Buscando en {label} ({db_path}) ---")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, razon_social, cuit, flags_estado, activo FROM clientes WHERE razon_social LIKE '%INAPYR%';")
        rows = cursor.fetchall()
        if not rows:
            print(" [OK] No se encontraron registros de INAPYR.")
        else:
            for row in rows:
                print(f" ID: {row[0]} | RS: {row[1]} | CUIT: {row[2]} | FLAGS: {row[3]} | ACTIVO: {row[4]}")
                # Analyze flags
                flags = row[3] or 0
                is_virgin = bool(flags & 2)
                is_gold = bool(flags & 4)
                is_active = bool(flags & 1)
                print(f"   ∟ Status: {'VIRGEN (Bit 1 ON)' if is_virgin else 'NO VIRGEN (Bit 1 OFF)'}, {'GOLD (Bit 2 ON)' if is_gold else 'NO GOLD'}, {'ACTIVO' if is_active else 'INACTIVO'}")
    except Exception as e:
        print(f" [!] Error query: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    find_duplicates(DEV_DB, "DESARROLLO")
    find_duplicates(PROD_DB, "PRODUCCIÓN")
