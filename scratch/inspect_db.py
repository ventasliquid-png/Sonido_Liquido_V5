import sqlite3

def inspect():
    try:
        conn = sqlite3.connect('pilot_v5x.db')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facturas';")
        if not cursor.fetchone():
            print("Table 'facturas' does not exist.")
            return

        cursor.execute("SELECT COUNT(*) FROM facturas;")
        count = cursor.fetchone()[0]
        print(f"Total facturas: {count}")

        cursor.execute("SELECT id, tipo_comprobante, estado, total FROM facturas LIMIT 10;")
        rows = cursor.fetchall()
        for row in rows:
            print(row)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
