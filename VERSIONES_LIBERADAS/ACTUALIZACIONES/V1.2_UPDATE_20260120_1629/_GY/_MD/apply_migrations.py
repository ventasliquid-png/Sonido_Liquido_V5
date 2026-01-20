import sqlite3

db_path = 'pilot.db'
queries = [
    "ALTER TABLE pedidos ADD COLUMN domicilio_entrega_id TEXT;",
    "ALTER TABLE pedidos ADD COLUMN transporte_id TEXT;"
]

# Note: Using TEXT for UUIDs as SQLite doesn't have a native UUID type and existing schema uses TEXT/GUID mapping.

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for q in queries:
        try:
            cursor.execute(q)
            print(f"Executed: {q}")
        except sqlite3.OperationalError as e:
            print(f"Skipped/Error: {q} -> {e}")
    conn.commit()
    conn.close()
    print("Migration finished.")
except Exception as e:
    print(f"Critical Migration Error: {e}")
