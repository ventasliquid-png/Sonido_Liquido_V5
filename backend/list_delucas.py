import sqlite3
import json

def audit():
    try:
        conn = sqlite3.connect('c:/dev/Sonido_Liquido_V5/pilot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        clients = cursor.execute('''
            SELECT id, razon_social, cuit, activo, condicion_iva_id, segmento_id
            FROM clientes
            WHERE razon_social LIKE "%DELUCA%"
        ''').fetchall()
        
        print(json.dumps([dict(c) for c in clients], indent=2))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit()
