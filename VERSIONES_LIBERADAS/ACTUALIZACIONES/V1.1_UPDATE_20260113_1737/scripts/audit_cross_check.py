import sqlite3
import pandas as pd

def compare_db(local_path, cloud_path):
    print(f"--- ⚖️  INICIANDO AUDITORÍA DE PARIDAD ---")
    print(f"LOCAL: {local_path}")
    print(f"IOWA (Snapshot): {cloud_path}\n")
    
    conn_local = sqlite3.connect(local_path)
    conn_cloud = sqlite3.connect(cloud_path)
    
    tables = ['productos', 'clientes']
    
    for table in tables:
        print(f"--- Tabla: {table.upper()} ---")
        df_local = pd.read_sql(f"SELECT * FROM {table}", conn_local)
        df_cloud = pd.read_sql(f"SELECT * FROM {table}", conn_cloud)
        
        count_local = len(df_local)
        count_cloud = len(df_cloud)
        
        print(f"  Conteo: Local({count_local}) vs IOWA({count_cloud})")
        
        # Identificar Huérfanos en IOWA (No están en Local)
        id_col = 'id' # Asumiendo UUID/ID como clave
        
        # Asegurarnos de que los IDs sean comparables (strings)
        df_local[id_col] = df_local[id_col].astype(str).str.replace('-', '')
        df_cloud[id_col] = df_cloud[id_col].astype(str).str.replace('-', '')
        
        huerfanos_iowa = df_cloud[~df_cloud[id_col].isin(df_local[id_col])]
        huerfanos_local = df_local[~df_local[id_col].isin(df_cloud[id_col])]
        
        if not huerfanos_iowa.empty:
            print(f"  ⚠️  HUÉRFANOS EN IOWA (Faltan en Local): {len(huerfanos_iowa)}")
            if table == 'productos':
                print(f"      SKUs: {huerfanos_iowa.get('sku', huerfanos_iowa.get('nombre')).tolist()[:5]}...")
        else:
            print(f"  ✅ No hay huérfanos en IOWA.")
            
        if not huerfanos_local.empty:
            print(f"  📢 NOVEDADES EN LOCAL (No están en IOWA): {len(huerfanos_local)}")
        
        # Comparación de "Gemelos con Desvío" (Mismo ID, distintos datos)
        # Hacemos un merge para comparar columnas críticas
        common_ids = df_local.merge(df_cloud, on=id_col, suffixes=('_loc', '_iow'))
        
        if table == 'productos':
            # Comparar nombres o SKUs para detectar desincronización
            desvios = common_ids[common_ids['nombre_loc'] != common_ids['nombre_iow']]
            if not desvios.empty:
                print(f"  🚨 DESVÍOS DETECTADOS (Mismo ID, diferente Nombre): {len(desvios)}")
        
        print("")

    conn_local.close()
    conn_cloud.close()

if __name__ == "__main__":
    compare_db('pilot.db', 'iowa_snapshot.sqlite')
