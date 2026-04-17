import os
import sqlite3
from datetime import datetime

# CONFIGURACIÓN DE PRODUCCIÓN (TOMY)
# Ajustar estas rutas según el entorno de V5-LS
DB_PATH = r"C:\dev\V5-LS\data\V5_LS_MASTER.db" 

def migrate_production_v59():
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] No se encontró la base de datos en: {DB_PATH}")
        return

    print(f"--- [MIGRACIÓN V5.9] Iniciando saneamiento en: {DB_PATH} ---")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Agregar columna flags_estado a rubros
        print("[1/2] Verificando columna flags_estado en tabla 'rubros'...")
        try:
            cursor.execute("ALTER TABLE rubros ADD COLUMN flags_estado BIGINT DEFAULT 0 NOT NULL;")
            print("      [OK] Columna flags_estado agregada correctamente.")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("      [SKIP] La columna flags_estado ya existe.")
            else:
                raise e

        # 2. Asegurar existencia del Rubro 'General' (Asilo de Exiliados)
        print("[2/2] Verificando existencia del rubro maestro 'General'...")
        cursor.execute("SELECT id FROM rubros WHERE nombre = 'General'")
        res = cursor.fetchone()
        
        if not res:
            # Encontrar un código disponible o usar '000'
            cursor.execute("INSERT INTO rubros (codigo, nombre, activo, flags_estado) VALUES ('000', 'General', 1, 0)")
            print(f"      [OK] Rubro 'General' creado (ID asignado: {cursor.lastrowid}).")
        else:
            print(f"      [SKIP] Rubro 'General' ya existe (ID: {res[0]}).")

        conn.commit()
        print("\n--- [MIGRACIÓN COMPLETADA] El sistema está listo para el protocolo de Exilio V5.9 ---")

    except Exception as e:
        conn.rollback()
        print(f"\n[CRITICAL ERROR] Falló la migración: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_production_v59()
