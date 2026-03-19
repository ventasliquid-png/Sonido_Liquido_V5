
import sqlite3
import os

database = "pilot_v5x.db"
uuid_lavimar = "e1be0585cd3443efa33204d00e199c4e"

def verify():
    if not os.path.exists(database):
        print(f"ERROR: No se encuentra {database}")
        return

    try:
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        # En V5 Atenea, 'id' es el UUID (CHAR 32)
        cursor.execute("SELECT razon_social, flags_estado FROM clientes WHERE id = ?", (uuid_lavimar,))
        row = cursor.fetchone()
        
        if row:
            razon_social, flags = row
            print(f"LAVIMAR_FOUND: {razon_social}")
            print(f"FLAGS_ESTADO: {flags}")
            if flags == 13:
                print("CALIBRACION_OK: 13 (V14.8.4 - Soberanía del 13)")
            else:
                print(f"ALERT: Calibración incorrecta. Se esperaba 13, se obtuvo {flags}")
        else:
            print(f"ERROR: Registro LAVIMAR ({uuid_lavimar}) no encontrado.")
            
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    verify()
