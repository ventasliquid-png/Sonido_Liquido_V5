
import sqlite3
import os
import uuid
from datetime import datetime, timezone

db_path = 'pilot_v5x.db'
if not os.path.exists(db_path):
    print(f"ERROR: DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path, timeout=60)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

def get_now():
    return datetime.now(timezone.utc).isoformat()

try:
    print("--- [VAULT PHASE 2] DATA MIGRATION ---")
    
    # --- 1. MIGRAR CLIENTES (Desde tabla domicilios actual) ---
    print("Migrando domicilios de Clientes...")
    cur.execute("SELECT * FROM domicilios WHERE cliente_id IS NOT NULL")
    doms = cur.fetchall()
    
    for dom in doms:
        vg_id = str(uuid.uuid4())
        flags = 0
        if dom['es_fiscal']: flags |= 1
        if dom['es_predeterminado']: flags |= 2
        
        cur.execute("""
            INSERT INTO vinculos_geograficos (id, entidad_tipo, entidad_id, domicilio_id, alias, flags_relacion, activo, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vg_id, 'CLIENTE', dom['cliente_id'], dom['id'], dom['alias'], flags, dom['activo'], get_now(), get_now()))

    # --- 2. MIGRAR PERSONAS (Desde tabla personas, campo domicilio_personal) ---
    print("Migrando domicilios de Personas...")
    cur.execute("SELECT id, nombre, domicilio_personal FROM personas WHERE domicilio_personal IS NOT NULL AND domicilio_personal != ''")
    pers = cur.fetchall()
    
    for p in pers:
        # Crear Domicilio Geográfico
        dom_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO domicilios (id, calle, localidad, provincia_id, activo, flags_infra)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (dom_id, p['domicilio_personal'], 'S/D', 'X', 1, 0))
        
        # Crear Vínculo (Rol: Principal Personal)
        vg_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO vinculos_geograficos (id, entidad_tipo, entidad_id, domicilio_id, alias, flags_relacion, activo, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (vg_id, 'PERSONA', p['id'], dom_id, 'Particular', 2, 1, get_now(), get_now()))

    # --- 3. MIGRAR TRANSPORTES (Desde empresas_transporte) ---
    print("Migrando domicilios de Transportes...")
    cur.execute("SELECT id, nombre, direccion, localidad, provincia_id, direccion_despacho FROM empresas_transporte")
    trps = cur.fetchall()
    
    for t in trps:
        # A. Dirección Central/Fiscal
        if t['direccion']:
            dom_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO domicilios (id, calle, localidad, provincia_id, activo, flags_infra)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dom_id, t['direccion'], t['localidad'], t['provincia_id'] or 'X', 1, 0))
            
            vg_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO vinculos_geograficos (id, entidad_tipo, entidad_id, domicilio_id, alias, flags_relacion, activo, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (vg_id, 'TRANSPORTE', t['id'], dom_id, 'Administrativa', 1, 1, get_now(), get_now()))

        # B. Dirección Despacho (si existe)
        if t['direccion_despacho'] and t['direccion_despacho'] != t['direccion']:
            dom_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO domicilios (id, calle, localidad, provincia_id, activo, flags_infra)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dom_id, t['direccion_despacho'], t['localidad'], t['provincia_id'] or 'X', 1, 0))
            
            vg_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO vinculos_geograficos (id, entidad_tipo, entidad_id, domicilio_id, alias, flags_relacion, activo, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (vg_id, 'TRANSPORTE', t['id'], dom_id, 'Despacho', 2, 1, get_now(), get_now()))

    # --- 4. MIGRAR NODOS LOGISTICOS (Desde nodos_transporte) ---
    print("Migrando domicilios de Nodos Logísticos...")
    cur.execute("SELECT id, nombre_nodo, direccion_completa, localidad, provincia_id FROM nodos_transporte")
    nods = cur.fetchall()
    
    for n in nods:
        if n['direccion_completa']:
            dom_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO domicilios (id, calle, localidad, provincia_id, activo, flags_infra)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (dom_id, n['direccion_completa'], n['localidad'], n['provincia_id'], 1, 0))
            
            vg_id = str(uuid.uuid4())
            cur.execute("""
                INSERT INTO vinculos_geograficos (id, entidad_tipo, entidad_id, domicilio_id, alias, flags_relacion, activo, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (vg_id, 'NODO_TRANSPORTE', n['id'], dom_id, n['nombre_nodo'], 2, 1, get_now(), get_now()))

    conn.commit()
    print("--- [VAULT PHASE 2] SUCCESS: Data trasvased to vinculos_geograficos ---")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    conn.rollback()
finally:
    conn.close()
