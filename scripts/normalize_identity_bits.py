import sqlite3
import zlib

DB_PATH = 'pilot_v5x.db'

def calculate_crc32(data_str):
    if data_str is None:
        data_str = ""
    return zlib.crc32(data_str.encode('utf-8')) & 0xFFFFFFFF

def normalize_personas(cursor):
    print("[*] Normalizing PERSONAS...")
    cursor.execute("SELECT id, nombre, apellido FROM personas")
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        pid, nombre, apellido = row
        identity_str = f"{nombre}|{apellido or ''}"
        bit_id = calculate_crc32(identity_str)
        cursor.execute("UPDATE personas SET bit_identidad = ? WHERE id = ?", (bit_id, pid))
        count += 1
    print(f" [x] {count} personas updated.")

def normalize_vinculos(cursor):
    print("[*] Normalizing VINCULOS...")
    cursor.execute("SELECT id, persona_id, entidad_id, entidad_tipo, rol FROM vinculos")
    rows = cursor.fetchall()
    count = 0
    for row in rows:
        vid, pid, eid, etype, rol = row
        identity_str = f"{pid}|{eid}|{etype}|{rol or ''}"
        bit_id = calculate_crc32(identity_str)
        cursor.execute("UPDATE vinculos SET bit_identidad = ? WHERE id = ?", (bit_id, vid))
        count += 1
    print(f" [x] {count} vinculos updated.")

def main():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        normalize_personas(cursor)
        normalize_vinculos(cursor)
        
        conn.commit()
        print("[OK] Normalization complete.")
        conn.close()
    except Exception as e:
        print(f"[ERR] {e}")

if __name__ == "__main__":
    main()
