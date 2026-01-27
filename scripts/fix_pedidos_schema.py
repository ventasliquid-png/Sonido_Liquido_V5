import sqlite3
import os

DB_PATH = "c:/dev/Sonido_Liquido_V5/pilot.db"

def fix_schema():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    table_name = "pedidos"
    
    # Define columns to check and add
    # Name, Type, UI Description
    columns_to_add = [
        ("costo_envio_cliente", "REAL", "Costo Envio Cliente"),
        ("costo_flete_interno", "REAL", "Costo Flete Interno"),
        ("estado_logistico", "TEXT DEFAULT 'PENDIENTE'", "Estado Logistico"),
        ("domicilio_entrega_id", "CHAR(32)", "Domicilio ID"),
        ("transporte_id", "CHAR(32)", "Transporte ID"),
        ("descuento_global_porcentaje", "REAL DEFAULT 0", "Descuento %"),
        ("descuento_global_importe", "REAL DEFAULT 0", "Descuento $"),
        ("oc", "TEXT", "Orden de Compra"),
        ("origen", "TEXT DEFAULT 'DIRECTO'", "Origen"),
        ("tipo_facturacion", "TEXT DEFAULT 'X'", "Tipo Facturacion"),
        ("fecha_compromiso", "DATETIME", "Fecha Compromiso"),
        ("liberado_despacho", "BOOLEAN DEFAULT 0", "Liberado Despacho")
    ]
    
    print(f"Checking schema for table '{table_name}'...")
    
    # Get existing columns
    cursor.execute(f"PRAGMA table_info({table_name})")
    existing_columns = [row[1] for row in cursor.fetchall()]
    
    for col_name, col_type, desc in columns_to_add:
        if col_name not in existing_columns:
            print(f"Adding missing column: {col_name} ({col_type})")
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}")
            except Exception as e:
                print(f"Error adding {col_name}: {e}")
        else:
            print(f"Column exists: {col_name}")
            
    conn.commit()
    conn.close()
    print("Schema check/update complete.")

if __name__ == "__main__":
    fix_schema()
