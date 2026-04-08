import sqlite3
import os

db_path = "pilot_v5x.db"

def check_pedidos():
    print(f"Checking schema for pedidos in {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(pedidos)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns in 'pedidos': {columns}")
    
    # Check for columns added in recent versions
    required = ["domicilio_entrega_id", "transporte_id", "costo_envio_cliente", "costo_flete_interno", "estado_logistico", "flags_estado"]
    
    for col in required:
        if col not in columns:
            print(f"Adding missing column '{col}' to 'pedidos'...")
            type_str = "CHAR(32)" if "id" in col else "VARCHAR"
            if "flags" in col: type_str = "BIGINT"
            if "costo" in col: type_str = "DECIMAL(12,2)"
            
            try:
                cursor.execute(f"ALTER TABLE pedidos ADD COLUMN {col} {type_str}")
                print(f"Successfully added '{col}'.")
            except Exception as e:
                print(f"Error adding {col}: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    check_pedidos()
