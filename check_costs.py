import sqlite3
import os

db_path = 'pilot.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

query = """
SELECT p.id, p.nombre, pc.costo_reposicion, pc.rentabilidad_target, pc.precio_roca 
FROM productos p 
LEFT JOIN productos_costos pc ON p.id = pc.producto_id 
LIMIT 10;
"""

try:
    cursor.execute(query)
    rows = cursor.fetchall()
    print("ID | Nombre | Costo Reposición | Rentabilidad Target | Precio Roca")
    print("-" * 80)
    for row in rows:
        print(f"{row[0]} | {row[1]} | {row[2]} | {row[3]} | {row[4]}")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
