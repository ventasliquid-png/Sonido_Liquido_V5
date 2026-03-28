import sqlite3
import os

db_path = "pilot_v5x.db"

def check_productos():
    print(f"Checking schema for productos in {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(productos)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Current columns in 'productos': {columns}")
    
    # Check for columns added in recent versions
    # We should look at productos/models.py
    required = ["proveedor_habitual_id", "presentacion_compra", "unidades_bulto", "tipo_producto", "factor_compra", "venta_minima", "flags_estado"]
    
    for col in required:
        if col not in columns:
            print(f"Adding missing column '{col}' to 'productos'...")
            # Try to determine type
            type_str = "CHAR(32)" if "id" in col else "VARCHAR"
            if "flags" in col: type_str = "BIGINT"
            if "unidades" in col or "factor" in col or "venta" in col: type_str = "DECIMAL(10,2)"
            
            try:
                cursor.execute(f"ALTER TABLE productos ADD COLUMN {col} {type_str}")
                print(f"Successfully added '{col}'.")
            except Exception as e:
                print(f"Error adding {col}: {e}")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    check_productos()
