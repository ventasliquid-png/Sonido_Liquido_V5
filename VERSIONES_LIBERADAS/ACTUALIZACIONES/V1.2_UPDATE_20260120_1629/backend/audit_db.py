import sqlite3
import json

def audit():
    try:
        conn = sqlite3.connect('c:/dev/Sonido_Liquido_V5/pilot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Check Masters
        segments = cursor.execute('SELECT id, nombre FROM segmentos').fetchall()
        ivas = cursor.execute('SELECT id, nombre FROM condiciones_iva').fetchall()
        
        # Check Clients
        clients = cursor.execute('''
            SELECT c.id, c.razon_social, c.condicion_iva_id, c.segmento_id, c.activo,
                   ci.nombre as condicion_iva_nombre, s.nombre as segmento_nombre
            FROM clientes c
            LEFT JOIN condiciones_iva ci ON c.condicion_iva_id = ci.id
            LEFT JOIN segmentos s ON c.segmento_id = s.id
            WHERE c.razon_social LIKE "%GELATO%" OR c.razon_social LIKE "%DELUCA%"
        ''').fetchall()
        
        results = {
            "master_segments": [dict(s) for s in segments],
            "master_ivas": [dict(i) for i in ivas],
            "clients": [dict(c) for c in clients],
            "domiciles": []
        }
        
        for client in clients:
            doms = cursor.execute('''
                SELECT id, calle, numero, cp, provincia_id, es_fiscal, es_entrega, activo
                FROM domicilios
                WHERE cliente_id = ?
            ''', (client['id'],)).fetchall()
            results["domiciles"].extend([dict(d) for d in doms])
            
        print(json.dumps(results, indent=2))
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit()
