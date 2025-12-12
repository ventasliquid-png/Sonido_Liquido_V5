
import pandas as pd
import requests
import os
import glob
from colorama import Fore, Style, init

init(autoreset=True)

BASE_URL = "http://localhost:8000"

def restore_clientes():
    # Find latest client seed
    files = glob.glob("SEMILLAS_MAESTRAS/clientes_master_*.csv")
    if not files:
        print(f"{Fore.RED}❌ No hay semillas de clientes.")
        return
    
    latest = max(files, key=os.path.getctime)
    print(f"{Fore.CYAN}📂 Leyendo semilla: {latest}")
    
    df = pd.read_csv(latest)
    print(f"{Fore.CYAN}ℹ️ Encontrados {len(df)} clientes en CSV.")
    
    # Iterate and POST
    success = 0
    for _, row in df.iterrows():
        # Map CSV columns to API Schema
        # Assuming CSV headers match model keys mostly. 
        # Check backend/clientes/schemas.py for exact expected payload if this fails.
        # For now, simplistic mapping.
        payload = {
            "razon_social": row.get('razon_social'),
            "cuit": str(row.get('cuit', '')), # Force string
            "condicion_iva_id": int(row.get('condicion_iva_id')) if pd.notna(row.get('condicion_iva_id')) else 1, # Default Consumidor Final?
            "segmento_id": int(row.get('segmento_id')) if pd.notna(row.get('segmento_id')) else 1,
            "activo": True
        }
        
        # Try Create
        try:
            res = requests.post(f"{BASE_URL}/clientes", json=payload)
            if res.status_code in [200, 201]:
                print(f"{Fore.GREEN}✅ Importado: {payload['razon_social']}")
                success += 1
            else:
                # If 409 (Conflict), maybe ignore?
                if res.status_code == 409:
                     print(f"{Fore.YELLOW}⚠️  Ya existe: {payload['razon_social']}")
                else:
                    print(f"{Fore.RED}❌ Error {res.status_code}: {res.text}")
        except Exception as e:
            print(f"{Fore.RED}❌ Excepción: {e}")

    print(f"{Fore.GREEN}✨ Clientes restaurados: {success}/{len(df)}")

def restore_productos():
    files = glob.glob("SEMILLAS_MAESTRAS/productos_master_*.csv")
    if not files: return
    latest = max(files, key=os.path.getctime)
    print(f"{Fore.CYAN}📂 Leyendo semilla de productos: {latest}")
    df = pd.read_csv(latest)
    
    success = 0
    for _, row in df.iterrows():
        payload = {
            "nombre": row.get('nombre'),
            "sku": str(row.get('sku')),
            "rubro_id": int(row.get('rubro_id')) if pd.notna(row.get('rubro_id')) else 1,
            "precio_minorista": float(row.get('precio_minorista', 0)),
            "activo": True
        }
        try:
            res = requests.post(f"{BASE_URL}/productos", json=payload)
            if res.status_code in [200, 201]:
                success += 1
                print(f"{Fore.GREEN}✅ Prod Importado: {payload['nombre']}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error Prod: {e}")
            
    print(f"{Fore.GREEN}✨ Productos restaurados: {success}/{len(df)}")

if __name__ == "__main__":
    print("--- INICIANDO RESTAURACIÓN DE SEMILLAS ---")
    restore_clientes()
    restore_productos()
