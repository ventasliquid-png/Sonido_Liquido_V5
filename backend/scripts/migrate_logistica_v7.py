import sqlite3
import os

DB_PATH = "../pilot.db"

def migrate():
    print(f"Migrating {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # helper for column existence
    def add_column(table, col_def):
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_def}")
            print(f"Added column {col_def} to {table}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Column {col_def.split()[0]} already exists in {table}")
            else:
                print(f"Error adding {col_def} to {table}: {e}")

    add_column("pedidos", "domicilio_entrega_id CHAR(32)")
    add_column("pedidos", "transporte_id CHAR(32)")
    add_column("remitos", "cae VARCHAR")
    add_column("remitos", "vto_cae DATE") # DATE type affinity in sqlite is flexible
    
    # [Fix 500 Error] Missing flags_estado in clientes
    add_column("clientes", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    
    # [Fix 500 Error Phase 2] Missing flags_estado in productos & transporte
    add_column("productos", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    add_column("empresas_transporte", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    
    # [Fix 500 Error Phase 3] Missing flags_estado in pedidos
    add_column("pedidos", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    
    conn.commit()
    conn.close()
    print("Migration V7 Complete.")

if __name__ == "__main__":
    if os.path.exists("pilot.db"): # Run from backend root
        DB_PATH = "pilot.db"
    elif os.path.exists("../pilot.db"): # Run from scripts dir
        DB_PATH = "../pilot.db"
        
    migrate()
