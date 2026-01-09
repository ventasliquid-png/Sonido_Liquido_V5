import psycopg2
import sqlite3
import pandas as pd
from datetime import datetime

# Definir Credenciales
CLOUD_URL_POSTGRES = "host='104.197.57.226' user='postgres' password='SonidoV5_2025' dbname='postgres' sslmode='require'"
LOCAL_DB = "pilot.db"

def forensic_audit():
    print("--- 🕵️ AUDITORÍA FORENSE DE FECHAS Y MANIOBRAS ---")
    
    # 1. Fechas Local
    try:
        conn_l = sqlite3.connect(LOCAL_DB)
        cur_l = conn_l.cursor()
        cur_l.execute("SELECT MAX(updated_at), MAX(created_at) FROM clientes")
        cli_l = cur_l.fetchone()
        cur_l.execute("SELECT MAX(updated_at), MAX(created_at) FROM productos")
        pro_l = cur_l.fetchone()
        print(f"Local (pilot.db):")
        print(f"  Clientes  - Última Mod: {cli_l[0]} | Creado: {cli_l[1]}")
        print(f"  Productos - Última Mod: {pro_l[0]} | Creado: {pro_l[1]}")
    except Exception as e:
        print(f"Error Local: {e}")

    # 2. Fechas IOWA
    try:
        conn_i = psycopg2.connect(CLOUD_URL_POSTGRES)
        cur_i = conn_i.cursor()
        
        # Primero chequear columnas
        cur_i.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'clientes'")
        cli_cols = [c[0] for c in cur_i.fetchall()]
        cur_i.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'productos'")
        pro_cols = [c[0] for c in cur_i.fetchall()]
        
        print(f"\nIOWA (Cloud):")
        
        q_cli = "SELECT MAX(updated_at), MAX(created_at) FROM clientes"
        if 'updated_at' in cli_cols:
            cur_i.execute(q_cli)
            res_cli = cur_i.fetchone()
            print(f"  Clientes  - Última Mod: {res_cli[0]} | Creado: {res_cli[1]}")
        else:
            print(f"  Clientes  - (Sin columnas de timestamp)")
            
        q_pro = "SELECT MAX(updated_at) FROM productos" # Test basic first
        if 'updated_at' in pro_cols:
            cur_i.execute(q_pro)
            res_pro = cur_i.fetchone()
            print(f"  Productos - Última Mod: {res_pro[0]}")
        else:
            print(f"  Productos - (Sin columnas de timestamp)")
            
        conn_i.close()
    except Exception as e:
        print(f"Error IOWA: {e}")

if __name__ == "__main__":
    forensic_audit()
