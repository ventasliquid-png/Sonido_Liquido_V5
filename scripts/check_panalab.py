import sqlite3

def check_client():
    conn = sqlite3.connect('pilot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, razon_social, activo, requiere_auditoria FROM clientes WHERE razon_social LIKE '%panalab%'")
    results = cursor.fetchall()
    conn.close()
    
    if results:
        for r in results:
            print(f"FOUND: ID={r[0]}, Name='{r[1]}', Active={r[2]}, Audit={r[3]}")
    else:
        print("NOT FOUND: 'panalab' does not exist in the database.")

if __name__ == "__main__":
    check_client()
