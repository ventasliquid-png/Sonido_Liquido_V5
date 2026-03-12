import os
import sqlite3
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from decimal import Decimal

load_dotenv()

def get_local_conn():
    return sqlite3.connect('pilot.db')

def get_cloud_conn():
    url = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")
    if url:
        return psycopg2.connect(url)
    
    return psycopg2.connect(
        host=os.getenv("POSTGRES_SERVER", "34.136.191.139"),
        database=os.getenv("POSTGRES_DB", "iowa"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )

def audit_pricing():
    print("🔍 INICIANDO AUDITORÍA DE COSTOS (IOWA vs LOCAL)...")
    
    l_conn = get_local_conn()
    c_conn = get_cloud_conn()
    
    try:
        l_cursor = l_conn.cursor()
        c_cursor = c_conn.cursor(cursor_factory=RealDictCursor)
        
        # 1. Verificar conteo de costos
        l_cursor.execute("SELECT COUNT(*) FROM productos_costos")
        l_count = l_cursor.fetchone()[0]
        
        c_cursor.execute("SELECT COUNT(*) FROM productos_costos")
        c_count = c_cursor.fetchone()['count']
        
        print(f"📊 Registros en productos_costos: LOCAL={l_count} | CLOUD={c_count}")
        
        # 2. Muestreo de discrepancias en costos de reposición
        # Traer top 50 de la nube para comparar
        c_cursor.execute("""
            SELECT p.sku, pc.costo_reposicion, pc.margen_mayorista
            FROM productos_costos pc
            JOIN productos p ON pc.producto_id = p.id
            LIMIT 100
        """)
        cloud_data = c_cursor.fetchall()
        
        differences = []
        for row in cloud_data:
            sku = row['sku']
            c_costo = Decimal(str(row['costo_reposicion']))
            
            l_cursor.execute("""
                SELECT pc.costo_reposicion
                FROM productos_costos pc
                JOIN productos p ON pc.producto_id = p.id
                WHERE p.sku = ?
            """, (sku,))
            res = l_cursor.fetchone()
            
            if res:
                l_costo = Decimal(str(res[0]))
                if abs(l_costo - c_costo) > 0.01:
                    differences.append({
                        "sku": sku,
                        "local": float(l_costo),
                        "cloud": float(c_costo)
                    })
            else:
                print(f"⚠️ SKU {sku} no encontrado en LOCAL")

        if differences:
            print(f"❌ SE ENCONTRARON {len(differences)} DISCREPANCIAS EN PRECIOS.")
            for diff in differences[:5]:
                print(f"   SKU {diff['sku']}: Local ${diff['local']} != Cloud ${diff['cloud']}")
        else:
            print("✅ LOS COSTOS ESTÁN SINCRONIZADOS.")

    finally:
        l_conn.close()
        c_conn.close()

if __name__ == "__main__":
    audit_pricing()
