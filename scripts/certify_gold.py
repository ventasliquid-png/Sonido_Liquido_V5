import sqlite3

DB_PATH = 'pilot_v5x.db'

def certify():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("[*] Buscando registro LAVIMAR para certificación...")
    # Buscamos por razon_social para ser agnósticos del ID generado por CSV
    cursor.execute("SELECT id, razon_social, flags_estado FROM clientes WHERE razon_social LIKE 'LAVIMAR%'")
    rows = cursor.fetchall()
    
    if not rows:
        print("[!] ERROR: No se encontró LAVIMAR en la base de datos.")
        return

    for row in rows:
        print(f" [+] Calibrando {row[1]} (ID: {row[0]}) de {row[2]} a 8205...")
        cursor.execute("UPDATE clientes SET flags_estado = 8205 WHERE id = ?", (row[0],))
    
    conn.commit()
    conn.close()
    print("[OK] Certificación Gold completada.")

if __name__ == "__main__":
    certify()
