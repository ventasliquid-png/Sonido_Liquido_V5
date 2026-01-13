import sqlite3
import uuid
import json

# Simular la lógica de SQLAlchemy + Pydantic
class GUID_Simulator:
    def process_result_value(self, value):
        if value is None: return None
        if len(value) == 32:
            # Hex to UUID
            return uuid.UUID(value)
        return uuid.UUID(value)

def diagnosis():
    conn = sqlite3.connect('c:/dev/Sonido_Liquido_V5/pilot.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get a client
    client = cursor.execute('SELECT razon_social, condicion_iva_id, segmento_id FROM clientes WHERE razon_social LIKE "%GELATO%"').fetchone()
    
    if client:
        sim = GUID_Simulator()
        iva_uuid = sim.process_result_value(client['condicion_iva_id'])
        seg_uuid = sim.process_result_value(client['segmento_id'])
        
        print(f"Client: {client['razon_social']}")
        print(f"Raw IVA ID: {client['condicion_iva_id']}")
        print(f"As UUID Object: {repr(iva_uuid)}")
        print(f"As JSON String (Pydantic style): {json.dumps(str(iva_uuid))}")
        
        # Check if they exist in masters with same format
        iva_master = cursor.execute('SELECT id, nombre FROM condiciones_iva WHERE id = ?', (client['condicion_iva_id'],)).fetchone()
        print(f"IVA Master found: {dict(iva_master) if iva_master else 'NOT FOUND'}")
        
    conn.close()

if __name__ == "__main__":
    diagnosis()
