
import sqlite3
import os

db_path = 'pilot_v5x.db'
if not os.path.exists(db_path):
    print(f"ERROR: DB not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path, timeout=60)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("PRAGMA busy_timeout = 60000")

def clean_dash(s):
    if s and isinstance(s, str) and '-' in s:
        return s.replace('-', '')
    return s

try:
    print("--- [SURGICAL FIX] Cleaning Dashes from Universal Vault ---")
    
    # 1. Clean 'vinculos_geograficos'
    cur.execute("SELECT id, entidad_id, domicilio_id FROM vinculos_geograficos")
    vgs = cur.fetchall()
    for vg in vgs:
        new_id = clean_dash(vg['id'])
        new_ent = clean_dash(vg['entidad_id'])
        new_dom = clean_dash(vg['domicilio_id'])
        if new_id != vg['id'] or new_ent != vg['entidad_id'] or new_dom != vg['domicilio_id']:
            cur.execute("""
                UPDATE vinculos_geograficos 
                SET id = ?, entidad_id = ?, domicilio_id = ? 
                WHERE id = ?
            """, (new_id, new_ent, new_dom, vg['id']))

    # 2. Clean 'domicilios'
    # We only care about IDs and cliente_id
    cur.execute("SELECT id, cliente_id FROM domicilios")
    doms = cur.fetchall()
    for dom in doms:
        new_id = clean_dash(dom['id'])
        new_cli = clean_dash(dom['cliente_id'])
        if new_id != dom['id'] or new_cli != dom['cliente_id']:
            # We need to update this ID everywhere it is used as FK
            old_id = dom['id']
            
            # Update Domicilio itself
            cur.execute("UPDATE domicilios SET id = ?, cliente_id = ? WHERE id = ?", (new_id, new_cli, old_id))
            
            # Update FK in Pedidos
            cur.execute("UPDATE pedidos SET domicilio_entrega_id = ? WHERE domicilio_entrega_id = ?", (new_id, old_id))
            
            # Update FK in Remitos
            cur.execute("UPDATE remitos SET domicilio_entrega_id = ? WHERE domicilio_entrega_id = ?", (new_id, old_id))
            
            # (vinculos_geograficos already handled in step 1 if it pointed to this)
            # Actually, handle it explicitly just in case
            cur.execute("UPDATE vinculos_geograficos SET domicilio_id = ? WHERE domicilio_id = ?", (new_id, old_id))

    conn.commit()
    print("--- [SURGICAL FIX] SUCCESS: All UUIDs are now dash-free ---")
    
except Exception as e:
    print(f"ERROR: {str(e)}")
    conn.rollback()
finally:
    conn.close()
