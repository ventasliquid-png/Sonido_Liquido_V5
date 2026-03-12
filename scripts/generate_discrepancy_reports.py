import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# URL Definitiva
CLOUD_URL = "postgresql://postgres:SonidoV5_2025@104.197.57.226:5432/postgres?sslmode=require"
LOCAL_DB = "pilot.db"

def generate_discrepancy_txt():
    print("--- 📑 GENERANDO LISTADOS DE DISCREPANCIAS ---")
    
    conn_local = sqlite3.connect(LOCAL_DB)
    engine_cloud = create_engine(CLOUD_URL)
    
    # 1. CLIENTES
    df_loc_cli = pd.read_sql("SELECT id, razon_social, cuit FROM clientes", conn_local)
    df_iow_cli = pd.read_sql("SELECT id, razon_social, cuit FROM clientes", engine_cloud)
    
    # Normalizar IDs
    df_loc_cli['id'] = df_loc_cli['id'].astype(str).str.replace('-', '')
    df_iow_cli['id'] = df_iow_cli['id'].astype(str).str.replace('-', '')
    
    # Solo en Local
    only_local_cli = df_loc_cli[~df_loc_cli['id'].isin(df_iow_cli['id'])]
    with open("discrepancias_solo_local_clientes.txt", "w", encoding="utf-8") as f:
        f.write("CLIENTES PRESENTES SOLO EN BASE LOCAL (pilot.db)\n")
        f.write("================================================\n")
        for _, row in only_local_cli.iterrows():
            f.write(f"- {row['razon_social']} (CUIT: {row['cuit']})\n")
    
    # Solo en IOWA
    only_iowa_cli = df_iow_cli[~df_iow_cli['id'].isin(df_loc_cli['id'])]
    with open("discrepancias_solo_iowa_clientes.txt", "w", encoding="utf-8") as f:
        f.write("CLIENTES PRESENTES SOLO EN IOWA (Cloud)\n")
        f.write("=======================================\n")
        for _, row in only_iowa_cli.iterrows():
            f.write(f"- {row['razon_social']} (CUIT: {row['cuit']})\n")

    # 2. PRODUCTOS
    df_loc_prod = pd.read_sql("SELECT id, nombre, sku FROM productos", conn_local)
    df_iow_prod = pd.read_sql("SELECT id, nombre, sku FROM productos", engine_cloud)
    
    # Normalizar IDs
    df_loc_prod['id'] = df_loc_prod['id'].astype(str).str.replace('-', '')
    df_iow_prod['id'] = df_iow_prod['id'].astype(str).str.replace('-', '')
    
    # Solo en Local
    only_local_prod = df_loc_prod[~df_loc_prod['id'].isin(df_iow_prod['id'])]
    with open("discrepancias_solo_local_productos.txt", "w", encoding="utf-8") as f:
        f.write("PRODUCTOS PRESENTES SOLO EN BASE LOCAL (pilot.db)\n")
        f.write("================================================\n")
        for _, row in only_local_prod.iterrows():
            f.write(f"- {row['nombre']} (SKU: {row['sku']})\n")
            
    # Solo en IOWA
    only_iowa_prod = df_iow_prod[~df_iow_prod['id'].isin(df_loc_prod['id'])]
    with open("discrepancias_solo_iowa_productos.txt", "w", encoding="utf-8") as f:
        f.write("PRODUCTOS PRESENTES SOLO EN IOWA (Cloud)\n")
        f.write("=======================================\n")
        for _, row in only_iowa_prod.iterrows():
            f.write(f"- {row['nombre']} (SKU: {row['sku']})\n")
            
    print("✅ Archivos .txt generados con éxito.")

if __name__ == "__main__":
    generate_discrepancy_txt()
