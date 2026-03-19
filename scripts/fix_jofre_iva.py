import sqlite3
import os

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"

def fix_iva_corruption():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Intentar encontrar el ID de "RESPONSABLE INSCRIPTO" o similar
    cursor.execute("SELECT id FROM condiciones_iva WHERE nombre LIKE '%RESPONSABLE INSCRIPTO%' LIMIT 1")
    iva_res = cursor.fetchone()
    if not iva_res:
         print("IVA Condition not found.")
         return
    
    iva_id = iva_res[0]
    
    # Reparar a Sergio Jofre
    cursor.execute("UPDATE clientes SET condicion_iva_id = ? WHERE razon_social LIKE '%Jofre%'", (iva_id,))
    conn.commit()
    print(f"✅ CORRUPTION FIXED: Sergio Jofre now has IVA ID {iva_id}")
    
    conn.close()

if __name__ == "__main__":
    fix_iva_corruption()
