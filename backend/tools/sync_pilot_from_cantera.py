"""
Script Táctico: Sincronización Fuerza Bruta (Frankenstein)
----------------------------------------------------------
Objetivo: Leer los espejos JSON (Cantera) e inyectarlos en la DB Principal (Pilot).
Uso: python backend/tools/sync_pilot_from_cantera.py
Autor: Antigravity
Fecha: 2026-01-14
"""
import sys
import os
import json
import sqlite3
from pathlib import Path

# Configuración de Rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
MIRROR_DIR = BACKEND_DIR / "data" / "json_mirror"
DB_PATH = BASE_DIR / "pilot.db"

# Asegurar imports
sys.path.insert(0, str(BASE_DIR))

def get_db_connection():
    return sqlite3.connect(str(DB_PATH))

def sync_productos(conn):
    print("--- [SYNC] Sincronizando PRODUCTOS ---")
    json_path = MIRROR_DIR / "productos.json"
    if not json_path.exists():
        print(f"[ERROR] No se encontró {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor = conn.cursor()
    count = 0
    updated = 0
    
    # Pre-check columns
    cursor.execute("PRAGMA table_info(productos)")
    cols = [info[1] for info in cursor.fetchall()]
    has_venta_minima = 'venta_minima' in cols

    for item in data:
        # Normalizar datos
        p_id = item.get("id") # Keep original ID if possible, mostly int or string
        nombre = item.get("nombre")
        sku = item.get("sku", "AUTO")
        rubro_id = item.get("rubro_id")
        activo = 1 # FORCE ACTIVE
        
        # Check if exists
        cursor.execute("SELECT id FROM productos WHERE id = ?", (p_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Update
            cursor.execute("""
                UPDATE productos 
                SET nombre = ?, sku = ?, rubro_id = ?, activo = ? 
                WHERE id = ?
            """, (nombre, sku, rubro_id, activo, p_id))
            updated += 1
        else:
            # Insert
            # Handle generic fields. Costos are separate but we need the product first.
            if has_venta_minima:
                cursor.execute("""
                    INSERT INTO productos (id, nombre, sku, rubro_id, activo, venta_minima)
                    VALUES (?, ?, ?, ?, ?, 1.0)
                """, (p_id, nombre, sku, rubro_id, activo))
            else:
                 cursor.execute("""
                    INSERT INTO productos (id, nombre, sku, rubro_id, activo)
                    VALUES (?, ?, ?, ?, ?)
                """, (p_id, nombre, sku, rubro_id, activo))
            count += 1
            
            # Ensure basic cost entry exists if new
            cursor.execute("SELECT id FROM productos_costos WHERE producto_id = ?", (p_id,))
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO productos_costos (producto_id, costo_reposicion, rentabilidad_target, precio_roca, iva_alicuota)
                    VALUES (?, 0, 30, 0, 21)
                """, (p_id,))

    conn.commit()
    print(f"[OK] Productos: {count} insertados, {updated} actualizados.")

def sync_clientes(conn):
    print("--- [SYNC] Sincronizando CLIENTES ---")
    json_path = MIRROR_DIR / "clientes.json"
    if not json_path.exists():
        print(f"[WARN] No se encontró {json_path}")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cursor = conn.cursor()
    count = 0
    updated = 0

    for item in data:
        c_id = item.get("id")
        razon_social = item.get("razon_social")
        cuit = item.get("cuit")
        activo = 1 # FORCE
        
        cursor.execute("SELECT id FROM clientes WHERE id = ?", (c_id,))
        exists = cursor.fetchone()
        
        if exists:
            cursor.execute("UPDATE clientes SET razon_social = ?, cuit = ?, activo = ? WHERE id = ?", 
                           (razon_social, cuit, activo, c_id))
            updated += 1
        else:
            cursor.execute("INSERT INTO clientes (id, razon_social, cuit, activo) VALUES (?, ?, ?, ?)",
                           (c_id, razon_social, cuit, activo))
            count += 1

    conn.commit()
    print(f"[OK] Clientes: {count} insertados, {updated} actualizados.")

def main():
    print(f"--- PROTOCOLO FRANKENSTEIN V1.0 ---")
    print(f"Target DB: {DB_PATH}")
    print(f"Source: {MIRROR_DIR}")
    
    if not DB_PATH.exists():
        print("[ERROR] No existe pilot.db!")
        return

    conn = get_db_connection()
    try:
        sync_productos(conn)
        sync_clientes(conn)
        print("--- Sincronización Finalizada ---")
    except Exception as e:
        print(f"[FATAL] Error en sync: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
