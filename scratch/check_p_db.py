import sqlite3

db_path = r'c:\dev\V5-LS\data\V5_LS_MASTER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"Tables: {tables}")

# Check last pedidos
# If no numero_pedido, maybe we use ROWID or id
try:
    cursor.execute("SELECT id, total, created_at FROM pedidos ORDER BY created_at DESC LIMIT 5")
    print(f"Last Pedidos: {cursor.fetchall()}")
except Exception as e:
    print(f"Error checking pedidos: {e}")

# Check remitos
try:
    cursor.execute("SELECT id, numero_comprobante, total, created_at FROM remitos ORDER BY created_at DESC LIMIT 5")
    print(f"Last Remitos: {cursor.fetchall()}")
except Exception as e:
    print(f"Error checking remitos: {e}")

conn.close()
