import sqlite3
import os

db_path = r'C:\dev\Sonido_Liquido_V5\pilot.db'

def inspect():
    if not os.path.exists(db_path):
        print(f"ERROR: DB not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("--- Inspecting VINCULOS Table ---")
    cursor.execute("SELECT id, persona_id, entidad_tipo, rol, tipo_contacto_id, activo FROM vinculos")
    rows = cursor.fetchall()
    
    if not rows:
        print("No vinculos found.")
    else:
        for r in rows:
            print(f"ID: {r[0]} | Persona: {r[1]} | Tipo: {r[2]} | ROL (Text): '{r[3]}' | RoleID: '{r[4]}' | Activo: {r[5]}")

    conn.close()

if __name__ == "__main__":
    inspect()
