"""
migrate_048_productos_nombre_canon.py
=====================================
Card #152 (S879): los productos pasan a tener su PROPIA clave canonica de nombre
(backend/productos/normalizacion.py), que conserva los numeros, las unidades y los talles. La clave vieja
(bolsa de palabras compartida con los clientes) los descartaba: «Bidon 5 L» y «Bidon 1 L», o «Talle M» y
«Talle L», daban la misma clave y el chequeo de duplicados bloqueaba el alta de una presentacion legitima.
Ademas los productos nacidos por otros caminos (fallback de remitos, cantera) tenian la clave en NULL.

Esta migracion RECALCULA `productos.nombre_canon` para TODOS los productos, desde `nombre`, con la funcion
nueva. Solo cambia esa columna (un dato derivado y sin restriccion UNIQUE): no toca nombres, SKU, precios
ni ninguna otra tabla. Si dos productos existentes dieran la misma clave nueva, lo informa (son
duplicados reales) y no hace nada con ellos. Idempotente: correrla de nuevo recalcula lo mismo.

MIGRATION_ID = "048_productos_nombre_canon"
NRO_SESION = 879
"""
import importlib.util
import os
import sqlite3

MIGRATION_ID = "048_productos_nombre_canon"
NRO_SESION = 879

AQUI = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DATABASE_URL", "").replace("sqlite:///", "") or os.path.join(AQUI, "..", "pilot_v5x.db")

# La funcion se carga por ruta (es solo libreria estandar): evita importar el backend entero desde una migracion.
_spec = importlib.util.spec_from_file_location(
    "normalizacion_productos", os.path.join(AQUI, "..", "backend", "productos", "normalizacion.py"))
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
normalizar_producto = _mod.normalizar_producto

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
    CREATE TABLE IF NOT EXISTS _migraciones_aplicadas (
        id VARCHAR PRIMARY KEY,
        nro_sesion INTEGER,
        aplicada_en DATETIME DEFAULT (datetime('now'))
    )
""")

if cur.execute("SELECT 1 FROM _migraciones_aplicadas WHERE id = ?", (MIGRATION_ID,)).fetchone():
    print(f"[migrate_048] SKIP -- {MIGRATION_ID} ya aplicada.")
    conn.close()
    exit(0)

try:
    print(f"[migrate_048] Iniciando {MIGRATION_ID}...")
    if not cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='productos'").fetchone():
        raise RuntimeError("No existe la tabla 'productos' en esta base: no es una base de V5 o esta desactualizada.")

    filas = cur.execute("SELECT id, nombre, nombre_canon FROM productos").fetchall()
    cambiados = 0
    por_clave = {}
    for pid, nombre, canon_viejo in filas:
        canon = normalizar_producto(nombre)
        por_clave.setdefault(canon, []).append((pid, nombre))
        if canon != canon_viejo:
            cur.execute("UPDATE productos SET nombre_canon = ? WHERE id = ?", (canon, pid))
            cambiados += 1

    cur.execute("INSERT INTO _migraciones_aplicadas (id, nro_sesion) VALUES (?, ?)", (MIGRATION_ID, NRO_SESION))
    conn.commit()
    print(f"[migrate_048] OK -- {len(filas)} producto(s) revisados, {cambiados} con la clave recalculada; {MIGRATION_ID} registrada.")
    for canon, items in por_clave.items():
        if canon and len(items) > 1:
            print(f"[migrate_048] AVISO -- duplicados reales (misma clave '{canon}'): " + "; ".join(f"#{i} {n}" for i, n in items))

except Exception as e:
    conn.rollback()
    print(f"[migrate_048] ERROR -- se deshizo todo, la base quedo como estaba: {e}")
    conn.close()
    exit(1)

conn.close()
