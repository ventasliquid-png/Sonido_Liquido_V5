import sqlite3
import os

db_path = "pilot_v5x.db"

def sync_table(cursor, table_name, schema_dict):
    print(f"--- Auditing table: {table_name} ---")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    
    for col, type_str in schema_dict.items():
        if col not in columns:
            print(f"Adding {col} ({type_str}) to {table_name}...")
            try:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {type_str}")
            except Exception as e:
                print(f"Error: {e}")
        else:
            # print(f"Column {col} OK.")
            pass

def fix_all():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Table: domicilios
    dom_schema = {
        "bit_identidad": "BIGINT DEFAULT 0",
        "flags_estado": "BIGINT DEFAULT 0",
        "flags_infra": "BIGINT DEFAULT 0",
        "is_maps_manual": "BOOLEAN DEFAULT 0",
        "observaciones": "TEXT",
        "calle_entrega": "VARCHAR",
        "numero_entrega": "VARCHAR",
        "piso_entrega": "VARCHAR",
        "depto_entrega": "VARCHAR",
        "cp_entrega": "VARCHAR",
        "localidad_entrega": "VARCHAR",
        "provincia_entrega_id": "VARCHAR(5)",
        "transporte_habitual_nodo_id": "CHAR(32)",
        "transporte_id": "CHAR(32)",
        "intermediario_id": "CHAR(32)",
        "metodo_entrega": "VARCHAR",
        "modalidad_envio": "VARCHAR",
        "origen_logistico": "VARCHAR"
    }
    sync_table(cursor, "domicilios", dom_schema)
    
    # 2. Table: productos_costos
    cost_schema = {
        "margen_sugerido": "DECIMAL(12,4) DEFAULT 0",
        "precio_roca": "DECIMAL(12,4) DEFAULT 0",
        "moneda_costo": "VARCHAR(3) DEFAULT 'ARS'",
        "iva_alicuota": "DECIMAL(5,2) DEFAULT 21.00"
    }
    sync_table(cursor, "productos_costos", cost_schema)
    
    # 3. Table: rubros
    rub_schema = {
        "padre_id": "INTEGER",
        "margen_default": "DECIMAL(10,2) DEFAULT 0",
        "activo": "BOOLEAN DEFAULT 1"
    }
    sync_table(cursor, "rubros", rub_schema)
    
    # 4. Table: clientes (Final Check)
    cli_schema = {
        "transporte_habitual_id": "CHAR(32)",
        "legacy_id_bas": "VARCHAR",
        "whatsapp_empresa": "VARCHAR",
        "web_portal_pagos": "VARCHAR",
        "datos_acceso_pagos": "TEXT",
        "vendedor_id": "CHAR(32)",
        "estrategia_precio": "VARCHAR",
        "saldo_actual": "DECIMAL(12,2) DEFAULT 0",
        "historial_cache": "TEXT",
        "estado_arca": "VARCHAR",
        "datos_arca_last_update": "DATETIME"
    }
    sync_table(cursor, "clientes", cli_schema)

    conn.commit()
    conn.close()
    print("Full schema sync completed.")

if __name__ == "__main__":
    fix_all()
