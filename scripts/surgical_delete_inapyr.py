import sqlite3
import os
import json
from datetime import datetime
import uuid

PROD_DB = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"
TARGET_ID = "70ab1441f2b046a09e78edfc7d72dea2" # INAPYR S. R. L.

def surgical_delete():
    print(f"=== OPERACIÓN QUIRÚRGICA: LIMPIEZA DE DUPLICADO INAPYR ===")
    
    if not os.path.exists(PROD_DB):
        print(f" [!] Error: DB no encontrada en {PROD_DB}")
        return

    conn = sqlite3.connect(PROD_DB)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # 1. Fetch Client Data for Backup
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (TARGET_ID,))
        client = cursor.fetchone()
        
        if not client:
            print(f" [!] Error: No se encontró el cliente con ID {TARGET_ID}")
            return
            
        print(f" [+] Cliente encontrado: {client['razon_social']} ({client['cuit']})")
        
        # 2. Check for Orders (Double Check)
        cursor.execute("SELECT count(*) FROM pedidos WHERE cliente_id = ?", (TARGET_ID,))
        order_count = cursor.fetchone()[0]
        if order_count > 0:
            print(f" [!] ABORTO: El cliente tiene {order_count} pedidos. No se puede borrar físicamente.")
            return

        # 3. Create Backup in core_papelera
        client_dict = dict(client)
        # Serialize UUIDs and dates
        for k, v in client_dict.items():
             if isinstance(v, (datetime, uuid.UUID)):
                 client_dict[k] = str(v)
        
        data_json = json.dumps(client_dict)
        
        # Check if papelera_registros exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='papelera_registros'")
        if not cursor.fetchone():
            print(" [!] Error: La tabla papelera_registros no existe. Abortando.")
            return

        print(" [>] Generando Backup en Papelera...")
        cursor.execute("""
            INSERT INTO papelera_registros (id, entidad_tipo, entidad_id, data, fecha_borrado, borrado_por)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), 'CLIENTE', TARGET_ID, data_json, datetime.now().isoformat(), 'GY_SURGICAL_PIN_1974'))
        
        # 4. Physical Delete
        print(" [>] Ejecutando Borrado Físico...")
        cursor.execute("DELETE FROM clientes WHERE id = ?", (TARGET_ID,))
        
        conn.commit()
        print("\n [OK] Operación exitosa. Registro eliminado y backupeado.")
        
    except Exception as e:
        conn.rollback()
        print(f" [X] ERROR CRÍTICO: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    surgical_delete()
