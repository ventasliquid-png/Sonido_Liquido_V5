import sqlite3
import pandas as pd
import os
import shutil

DB_PATH = 'pilot_v5x.db'
BACKUP_PATH = 'pilot_v5x_PRE_SANEAMIENTO.db'
SEED_DIR = 'SEMILLAS_MAESTRAS'

def backup_db():
    if os.path.exists(DB_PATH):
        print(f"[*] Creando backup en {BACKUP_PATH}...")
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print("[OK] Backup creado.")

def saneamiento():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n--- INICIANDO PURGA TÉCNICA (PROTOCOLO SOBERANÍA) ---")
    
    # 1. Eliminar pedidos y remitos (Zombies)
    print("[*] Eliminando pedidos y remitos...")
    cursor.execute("DELETE FROM pedidos_items")
    cursor.execute("DELETE FROM pedidos")
    try:
        cursor.execute("DELETE FROM remitos_items")
        cursor.execute("DELETE FROM remitos")
    except: pass
    
    # 2. Eliminar Clientes y Productos (Refresco total)
    print("[*] Limpiando tablas maestras...")
    cursor.execute("DELETE FROM domicilios_clientes")
    cursor.execute("DELETE FROM domicilios")
    cursor.execute("DELETE FROM clientes")
    cursor.execute("DELETE FROM productos_costos")
    cursor.execute("DELETE FROM productos")
    cursor.execute("DELETE FROM rubros")
    
    conn.commit()
    print("[OK] Purga de datos zombies completada.")

    # 3. Re-Importar Rubros
    print("\n--- RE-IMPORTACIÓN DE SEMILLAS MAESTRAS ---")
    rubros_csv = os.path.join(SEED_DIR, "RUBROS_MAESTRO_LATEST.csv")
    if os.path.exists(rubros_csv):
        df = pd.read_csv(rubros_csv)
        df.to_sql('rubros', conn, if_exists='append', index=False)
        print(f"[OK] {len(df)} Rubros importados.")

    # 4. Re-Importar Productos
    prod_csv = os.path.join(SEED_DIR, "PRODUCTOS_MAESTRO_LATEST.csv")
    if os.path.exists(prod_csv):
        df = pd.read_csv(prod_csv)
        # Genoma 64-bit: Asegurar que flags_estado exista
        if 'flags_estado' not in df.columns:
            df['flags_estado'] = 0
        
        # Eliminar columnas que no existan en la tabla destino (schema sanity)
        cursor.execute("PRAGMA table_info(productos)")
        table_cols = [row[1] for row in cursor.fetchall()]
        df = df[[c for c in df.columns if c in table_cols]]
        
        df.to_sql('productos', conn, if_exists='append', index=False)
        print(f"[OK] {len(df)} Productos importados.")

    # 5. Re-Importar Costos
    costos_csv = os.path.join(SEED_DIR, "2025-12-17_17-56_productos_costos.csv")
    if os.path.exists(costos_csv):
        df = pd.read_csv(costos_csv)
        # Mapping: Doctrina Roca Sólida
        if 'margen_mayorista' in df.columns:
            df = df.rename(columns={'margen_mayorista': 'rentabilidad_target'})
        if 'precio_roca' not in df.columns:
            df['precio_roca'] = 0.0
        if 'margen_sugerido' not in df.columns:
            df['margen_sugerido'] = 0.0
        
        # Eliminar columnas deprecadas (precio_fijo_override, permitir_descuentos)
        cursor.execute("PRAGMA table_info(productos_costos)")
        table_cols = [row[1] for row in cursor.fetchall()]
        df = df[[c for c in df.columns if c in table_cols]]

        df.to_sql('productos_costos', conn, if_exists='append', index=False)
        print(f"[OK] {len(df)} Registros de costos importados.")

    # 6. Re-Importar Clientes (Filtrado Anti-Zombi)
    cli_csv = os.path.join(SEED_DIR, "CLIENTES_MAESTRO_LATEST.csv")
    if os.path.exists(cli_csv):
        df = pd.read_csv(cli_csv)
        
        # --- [FILTRO SOBERANÍA] ---
        initial_count = len(df)
        # Excluir CUITs nulos o de prueba, pero EXCEPCIONAR a LAVIMAR
        df = df[
            (~df['cuit'].astype(str).str.contains('00000000000|30-11223344-6|30112233446', na=False) & 
             ~df['razon_social'].astype(str).str.startswith(('EV ', 'cli1', 'test'), na=False)) |
            (df['razon_social'] == 'LAVIMAR')
        ]
        print(f"[*] Filtro de Soberanía: {initial_count} -> {len(df)} clientes legítimos.")
        # ---------------------------

        # Genoma 64-bit & Master Data Integrity
        if 'flags_estado' not in df.columns:
            df['flags_estado'] = 0
        if 'estado_arca' not in df.columns:
            df['estado_arca'] = 'PENDIENTE'
            
        # Al igual que en productos, filtramos columnas reales
        cursor.execute("PRAGMA table_info(clientes)")
        table_cols = [row[1] for row in cursor.fetchall()]
        df = df[[c for c in df.columns if c in table_cols]]
        
        df.to_sql('clientes', conn, if_exists='append', index=False)
        print(f"[OK] {len(df)} Clientes reales importados.")

    conn.commit()
    conn.close()
    print("\n--- PROTOCOLO SANEAMIENTO V5 FINALIZADO ---")

if __name__ == "__main__":
    backup_db()
    saneamiento()
