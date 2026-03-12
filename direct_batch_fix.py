import sqlite3
import sys
import os
import time

# Add RAR_V1 to path for rar_core
RAR_PATH = r"C:\dev\RAR_V1"
if RAR_PATH not in sys.path:
    sys.path.append(RAR_PATH)

try:
    from Conexion_Blindada import get_datos_afip
    print("✅ RAR Conexion Blindada Loaded")
except ImportError:
    print("❌ RAR Conexion Blindada Not Found independent of sys.path")
    try:
        import sys
        sys.path.append(r"C:\dev\RAR_V1")
        from Conexion_Blindada import get_datos_afip
        print("✅ RAR Conexion Blindada Loaded (Second Attempt)")
    except ImportError as e:
        print(f"❌ Failed to load RAR: {e}")
        sys.exit(1)

DB_PATH = r"C:\dev\Sonido_Liquido_V5\pilot.db"

def run():
    print(f"🔌 Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Find pending
    cursor.execute("SELECT id, razon_social, cuit FROM clientes WHERE (estado_arca IS NULL OR estado_arca != 'VALIDADO') AND length(cuit) >= 11")
    clients = cursor.fetchall()
    print(f"📋 Found {len(clients)} clients.")

    GENERIC_CUITS = ['11111111119', '11111111111', '00000000000']

    for client in clients:
        cid, rs, cuit = client
        print(f"   Processing {rs} ({cuit})...")

        # 1. Generic Check
        if cuit in GENERIC_CUITS:
            print("   ⚠️ Generic CUIT. Marking as Validated (Local Bypass).")
            cursor.execute("UPDATE clientes SET estado_arca = 'VALIDADO', datos_arca_last_update = ? WHERE id = ?", (time.strftime('%Y-%m-%d %H:%M:%S'), cid))
            conn.commit()
            continue

        # 2. ARCA Check
        try:
            # Conexion_Blindada.get_datos_afip returns a dict or raises
            data = get_datos_afip(cuit)
            
            if not data or 'error' in data:
                print(f"   ❌ Error RAR: {data.get('error') if data else 'Empty'}")
                continue
            
            # Map Logic
            # UBA Case:
            # If local RS is empty/placeholder, update.
            # If local RS is specific (and different), keep it but maybe append?
            # User wants "Validation". 
            # Strategy: Always update 'estado_arca'. 
            # Update 'razon_social' ONLY if current is empty or 'CONSUMIDOR FINAL'.
            
            should_update_rs = False
            if not rs or rs.strip() == '' or rs == 'CONSUMIDOR FINAL':
                should_update_rs = True
            
            new_rs = data.get('nombre') or data.get('razon_social') # rar_core might return 'nombre'
            final_rs = new_rs if should_update_rs else rs

            # Fiscal Address
            dom_fiscal = data.get('domicilio_fiscal', '')
            
            # IVA
            iva_text = data.get('condicion_iva', 'Responsable Inscripto').upper()
            iva_id = 1
            if 'MONOTRIBUTO' in iva_text: iva_id = 6
            elif 'EXENTO' in iva_text: iva_id = 4
            elif 'FINAL' in iva_text: iva_id = 5

            cursor.execute("""
                UPDATE clientes 
                SET estado_arca = 'VALIDADO', 
                    datos_arca_last_update = ?,
                    razon_social = ?,
                    domicilio_fiscal = ?,
                    condicion_iva_id = ?
                WHERE id = ?
            """, (time.strftime('%Y-%m-%d %H:%M:%S'), final_rs, dom_fiscal, iva_id, cid))
            
            conn.commit()
            print(f"   ✅ Auto-Validated: {final_rs}")
            
        except Exception as e:
            print(f"   ❌ Failed: {e}")

    print("🏁 Done.")
    conn.close()

if __name__ == '__main__':
    run()
