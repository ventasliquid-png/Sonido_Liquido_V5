import sqlite3
import os

db_path = 'pilot_v5x.db'
if not os.path.exists(db_path):
    db_path = os.path.join('backend', 'pilot_v5x.db')

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, razon_social, flags_estado FROM clientes WHERE razon_social LIKE '%LAVIMAR%'")
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            print(f'ID: {r[0]} | CLIENTE: {r[1]} | FLAGS: {r[2]}')
    else:
        # Búsqueda total para ver qué hay en la tabla
        cursor.execute("SELECT COUNT(*) FROM clientes")
        count = cursor.fetchone()[0]
        print(f'RESULTADO: NULL (Lavimar no hallado). Total registros en tabla: {count}')
    conn.close()
except Exception as e:
    print(f'ERROR: {str(e)}')
