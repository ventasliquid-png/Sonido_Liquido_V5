import os
import sys

db_path = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from backend.core.database import engine
from sqlalchemy import text

def inspect_data():
    with engine.connect() as conn:
        print("--- SAMPLE CLIENTE ---")
        res = conn.execute(text("SELECT id, razon_social, cuit, historial_direcciones FROM clientes LIMIT 5")).fetchall()
        for r in res:
            print(f"ID: {r[0]} | Name: {r[1]} | CUIT: {r[2]} | Historial: {r[3]}")
            
        print("\n--- SAMPLE DOMICILIO ---")
        res = conn.execute(text("SELECT id, cliente_id, calle, numero, es_fiscal, es_entrega FROM domicilios WHERE cliente_id IS NOT NULL LIMIT 5")).fetchall()
        for r in res:
            print(f"ID: {r[0]} | ClienteID: {r[1]} | Calle: {r[2]} | Num: {r[3]} | Fiscal: {r[4]} | Entrega: {r[5]}")

if __name__ == "__main__":
    inspect_data()
