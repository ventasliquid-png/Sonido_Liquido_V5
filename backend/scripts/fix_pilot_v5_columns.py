import sqlite3
import os

# FORCE PILOT.DB
DB_PATH = "pilot.db" 

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: {DB_PATH} not found in current directory: {os.getcwd()}")
        return

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

    # LOGISTICA V7 COLUMNS
    add_column("pedidos", "domicilio_entrega_id CHAR(32)")
    add_column("pedidos", "transporte_id CHAR(32)")
    add_column("remitos", "cae VARCHAR")
    add_column("remitos", "vto_cae DATE")
    
    # CRITICAL 500 ERROR FIXES
    add_column("clientes", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    add_column("productos", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    add_column("empresas_transporte", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    add_column("pedidos", "flags_estado INTEGER DEFAULT 0 NOT NULL")
    
    conn.commit()
    conn.close()
    print("Migration Fix Complete for PILOT.DB.")

if __name__ == "__main__":
    migrate()
