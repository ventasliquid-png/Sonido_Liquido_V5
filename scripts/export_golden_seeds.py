
import os
import sys
import csv
import glob
from datetime import datetime
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# -----------------------------------------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------------------------------------
# Aseguramos que el path del proyecto esté en sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

try:
    from backend.core.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL
except ImportError:
    # Fallback si falla la importación directa (ej: ejecutando desde dentro de scripts/)
    print("⚠️  Error importando configuración de DB. Intentando ruta relativa...")
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from backend.core.database import DATABASE_URL as SQLALCHEMY_DATABASE_URL

# Directorio de salida
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "SEMILLAS_MAESTRAS")

# Tablas críticas a exportar (Ordenadas por dependencia para futura importación)
TABLAS_CRITICAS = [
    "condiciones_iva",
    "listas_precios",
    "unidades",
    "tasas_iva",
    "rubros",
    "usuarios", # Vendedores
    "empresas_transporte",
    "nodos_transporte",
    "segmentos",
    "proveedores",
    "clientes",
    "domicilios", # Depende de Clientes
    "productos", # Depende de Rubros, Proveedores, Unidades
    "productos_costos", # Depende de Productos
    "vinculos_comerciales", # Agenda
]

# -----------------------------------------------------------------------------
# LÓGICA
# -----------------------------------------------------------------------------
def init_backup_dir():
    if not os.path.exists(OUTPUT_DIR):
        print(f"📁 Creando directorio de semillas: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR)
    else:
        print(f"📂 Directorio de semillas encontrado: {OUTPUT_DIR}")

def export_table(engine, table_name, timestamp):
    """Exporta una tabla completa a CSV usando SQL puro para velocidad."""
    try:
        with engine.connect() as connection:
            # Verificar si la tabla existe
            insp = inspect(engine)
            if not insp.has_table(table_name):
                print(f"⚠️  Tabla '{table_name}' no encontrada. Saltando.")
                return

            # Query select all
            query = text(f"SELECT * FROM {table_name}")
            result = connection.execute(query)
            
            # Obtener headers
            headers = result.keys()
            
            # Nombre de archivo: YYYY-MM-DD_HH-MM_tablename.csv
            filename = f"{timestamp}_{table_name}.csv"
            filepath = os.path.join(OUTPUT_DIR, filename)
            
            # Escribir CSV
            row_count = 0
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers) # Header
                
                for row in result:
                    writer.writerow(row)
                    row_count += 1
            
            print(f"✅ {table_name.ljust(25)} -> Exportados {row_count} registros.")
            
    except Exception as e:
        print(f"❌ Error exportando tabla '{table_name}': {e}")

def cleanup_old_backups(retention_count=5):
    """Mantiene solo los últimos N sets de backups para no llenar el disco."""
    # Agrupar archivos por timestamp (primeros 16 chars: YYYY-MM-DD_HH-MM)
    all_files = glob.glob(os.path.join(OUTPUT_DIR, "*.csv"))
    if not all_files:
        return

    timestamps = set()
    for f in all_files:
        basename = os.path.basename(f)
        ts = basename[:16] # "2025-12-12_10-00"
        timestamps.add(ts)
    
    sorted_ts = sorted(list(timestamps), reverse=True)
    
    if len(sorted_ts) > retention_count:
        print(f"\n🧹 Limpieza: Manteniendo los últimos {retention_count} snapshots...")
        old_ts = sorted_ts[retention_count:]
        
        removed_count = 0
        for ts in old_ts:
            pattern = os.path.join(OUTPUT_DIR, f"{ts}*.csv")
            for f in glob.glob(pattern):
                os.remove(f)
                removed_count += 1
        print(f"🗑️  Eliminados {removed_count} archivos antiguos.")

def run_export():
    print(f"\n🌱 INICIANDO EXPORTACIÓN DE SEMILLAS MAESTRAS (Golden Seeds)")
    print(f"🔌 Base de Datos: {SQLALCHEMY_DATABASE_URL}")
    print("="*60)
    
    init_backup_dir()
    
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    for table in TABLAS_CRITICAS:
        export_table(engine, table, timestamp)
        
    # cleanup_old_backups()
    
    print("="*60)
    print(f"✨ Proceso Finalizado. Semillas guardadas en: {OUTPUT_DIR}\n")

if __name__ == "__main__":
    run_export()
