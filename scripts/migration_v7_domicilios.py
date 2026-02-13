import sqlite3
import os

DB_PATH = "pilot.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🚀 Starting V7 Domicilios Migration (Enhanced)...")

    # 1. Add new columns if they don't exist
    new_columns = {
        # V7 Base
        "piso": "TEXT",
        "depto": "TEXT",
        "maps_link": "TEXT",
        "notas_logistica": "TEXT",
        "contacto_id": "INTEGER",
        
        # V7.1 Observaciones
        "observaciones": "TEXT",
        
        # V7.2 Split Delivery Address
        "calle_entrega": "TEXT",
        "numero_entrega": "TEXT",
        "piso_entrega": "TEXT",
        "depto_entrega": "TEXT",
        "cp_entrega": "TEXT",
        "localidad_entrega": "TEXT",
        "provincia_entrega_id": "TEXT", # String(5)
        
        # Logistica / Transport
        "transporte_habitual_nodo_id": "TEXT", # GUID as TEXT
        "transporte_id": "TEXT",
        "intermediario_id": "TEXT",
        "metodo_entrega": "TEXT",
        "modalidad_envio": "TEXT",
        "origen_logistico": "TEXT"
    }

    cursor.execute("PRAGMA table_info(domicilios)")
    existing_columns = [info[1] for info in cursor.fetchall()]

    added_count = 0
    for col, dtype in new_columns.items():
        if col not in existing_columns:
            print(f"➕ Adding column: {col}")
            try:
                cursor.execute(f"ALTER TABLE domicilios ADD COLUMN {col} {dtype}")
                added_count += 1
            except sqlite3.OperationalError as e:
                print(f"⚠️ Error adding {col}: {e}")
        else:
            # print(f"✅ Column {col} already exists.")
            pass

    print(f"   -> Added {added_count} new columns.")
    conn.commit()

    # 2. Data Rescue (Split Logic)
    print("🧹 Starting Data Rescue (Removing pipes '|')...")
    
    # We need to ensure we don't crash if columns are missing in select, 
    # but we just added them so it's fine.
    cursor.execute("SELECT id, calle, numero FROM domicilios")
    rows = cursor.fetchall()
    
    updates = 0
    for row in rows:
        dom_id, calle, numero = row
        piso = None
        depto = None
        new_calle = calle
        new_numero = numero
        changed = False

        # Check 'numero' for pipes (Most common: "1234 | 4 B")
        if numero and "|" in numero:
            parts = numero.split("|")
            new_numero = parts[0].strip()
            rest = parts[1].strip()
            
            # Simple heuristic for '4 B' -> piso=4, depto=B
            # If rest is short and has space, split it.
            if " " in rest:
                p_parts = rest.split(" ")
                piso = p_parts[0]
                depto = " ".join(p_parts[1:])
            else:
                piso = rest # Assume it's just floor or just depto? Put in piso for now.
            
            changed = True
            print(f"   🔧 Split Numero: '{numero}' -> Num:'{new_numero}', Piso:'{piso}', Depto:'{depto}'")

        # Check 'calle' for pipes (Legacy error)
        if calle and "|" in calle:
            parts = calle.split("|")
            new_calle = parts[0].strip()
            extra = parts[1].strip()
            if not piso: # Only if not found in numero
                piso = extra
            else:
                depto = extra 
            changed = True
            print(f"   🔧 Split Calle: '{calle}' -> Calle:'{new_calle}', Extra:'{extra}'")

        if changed:
            cursor.execute("""
                UPDATE domicilios 
                SET calle = ?, numero = ?, piso = ?, depto = ?
                WHERE id = ?
            """, (new_calle, new_numero, piso, depto, dom_id))
            updates += 1

    conn.commit()
    conn.close()
    print(f"🎉 Migration Complete. {updates} records updated.")

if __name__ == "__main__":
    migrate()
