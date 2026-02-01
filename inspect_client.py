import sqlite3
import pandas as pd

def inspect():
    conn = sqlite3.connect('pilot.db')
    
    cursor = conn.cursor()
    cursor.execute("SELECT id, razon_social, condicion_iva_id FROM clientes WHERE razon_social LIKE '%Laboratorio%'")
    row = cursor.fetchone()
    print(f"ID: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"IVA ID: {row[2]}")
    
    cursor.execute("SELECT id, nombre FROM condiciones_iva LIMIT 1")
    iva = cursor.fetchone()
    print(f"Target IVA ID: {iva[0]} ({iva[1]})")
    
    conn.close()

if __name__ == "__main__":
    inspect()
