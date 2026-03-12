import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pilot.db')

def migrate():
    print(f"--- [MIGRATION V1.1.2] Connecting to {DB_PATH} ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Check/Seed TasasIVA
    print("--- [CHECK] TasasIVA ---")
    cursor.execute("SELECT count(*) FROM tasas_iva")
    count = cursor.fetchone()[0]
    if count == 0:
        print("[SEEDING] Inserting default IVA rates...")
        tasas = [
            (1, "IVA 0% (Exento)", 0.00),
            (2, "IVA 10.5% (Reducido)", 10.50),
            (3, "IVA 21% (General)", 21.00),
            (4, "IVA 27% (Telecos/Energia)", 27.00)
        ]
        cursor.executemany("INSERT INTO tasas_iva (id, nombre, valor) VALUES (?, ?, ?)", tasas)
        print("  -> Inserted 4 rates.")
    else:
        print(f"  -> OK. Found {count} rates.")

    # 2. Add venta_minima to productos
    print("--- [CHECK] Column 'venta_minima' in 'productos' ---")
    cursor.execute("PRAGMA table_info(productos)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'venta_minima' not in columns:
        print("[MIGRATING] Adding column 'venta_minima'...")
        cursor.execute("ALTER TABLE productos ADD COLUMN venta_minima DECIMAL(10,2) DEFAULT 1.0")
        print("  -> Column added successfully.")
    else:
        print("  -> OK. Column already exists.")

    conn.commit()
    conn.close()
    print("--- [DONE] Migration Complete ---")

if __name__ == "__main__":
    migrate()
