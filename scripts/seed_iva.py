
import sqlite3
import os

DB_PATH = 'c:\\dev\\Sonido_Liquido_V5\\backend\\pilot.db'

def check_and_seed_iva():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if table exists
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='tasas_iva'")
        if cursor.fetchone()[0] == 0:
            print("Table 'tasas_iva' does not exist. It normally should be created by Alembic/SQLAlchemy.")
            # We can try to create it if it doesn't exist, matching model
            print("Creating table 'tasas_iva'...")
            cursor.execute("""
                CREATE TABLE tasas_iva (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre VARCHAR NOT NULL,
                    valor NUMERIC(5, 2) NOT NULL
                )
            """)
        
        # Check count
        cursor.execute("SELECT count(*) FROM tasas_iva")
        count = cursor.fetchone()[0]
        print(f"Current IVA rates count: {count}")

        if count == 0:
            print("Seeding IVA rates...")
            rates = [
                (1, 'IVA General', 21.00),
                (2, 'IVA Reducido', 10.50),
                (3, 'IVA Exento', 0.00),
                (4, 'IVA Acrecentado', 27.00)
            ]
            cursor.executemany("INSERT INTO tasas_iva (id, nombre, valor) VALUES (?, ?, ?)", rates)
            conn.commit()
            print("Seeded 4 IVA rates.")
            
            # Verify
            cursor.execute("SELECT * FROM tasas_iva")
            rows = cursor.fetchall()
            for r in rows:
                print(r)
        else:
            cursor.execute("SELECT * FROM tasas_iva")
            rows = cursor.fetchall()
            print("Existing rates:")
            for r in rows:
                print(r)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_and_seed_iva()
