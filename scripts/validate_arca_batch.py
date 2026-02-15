import sys
import os

# Robust Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now we can import from backend
from backend.database import SessionLocal
from backend.clientes.services.afip_bridge import AfipBridgeService
import time
from sqlalchemy import text

def validate_batch():
    session = SessionLocal()
    try:
        print("🔍 Buscando clientes pendientes de validación ARCA...")
        
        # Get all clients that are NOT validated (or have no status)
        # We can also filter by having a CUIT
        query = text("""
            SELECT id, razon_social, cuit, estado_arca 
            FROM clientes 
            WHERE (estado_arca IS NULL OR estado_arca != 'VALIDADO')
            AND cuit IS NOT NULL 
            AND LENGTH(cuit) >= 11
        """)
        
        clients = session.execute(query).fetchall()
        
        total = len(clients)
        print(f"📋 Se encontraron {total} clientes para validar.")
        
        success_count = 0
        error_count = 0
        
        for idx, client in enumerate(clients):
            print(f"\n[{idx+1}/{total}] Procesando: {client.razon_social} ({client.cuit})")
            
            try:
                # 1. Call Bridge
                data = AfipBridgeService.get_datos_afip(client.cuit)
                
                if not data or 'error' in data:
                    print(f"   ❌ Error del Puente: {data.get('error') if data else 'Sin Datos'}")
                    error_count += 1
                    continue
                    
                # 2. Update DB
                # Logic for UBA/Multiparty CUITs:
                # If local Razon Social is set and different from ARCA, we might want to keep local (e.g. "Facultad X")
                # But typically ARCA is the "Legal" name.
                # Compromise: precise_update. 
                # If current name is empty or looks like a placeholder, update it.
                # If it looks specific, maybe append or leave it?
                # User asked: "How do we handle it?" -> "El CUIT validará UBA but not Facultad".
                # Decision: Update Razon Social to Legal Name (ARCA), move old name to Fantasia if empty? 
                # OR: Just validate status and IVA, and only update RS if it's clearly wrong/empty.
                
                current_rs = client.razon_social or ''
                new_rs = data.get('razon_social')
                
                # Check if we should overwrite RS
                should_update_rs = False
                if not current_rs or current_rs == 'CONSUMIDOR FINAL' or current_rs == 'S/D':
                    should_update_rs = True
                elif new_rs and new_rs != current_rs:
                    # If they differ, we enforce Legal Name for tax purposes
                    # But we could log the conflict. 
                    # For batch, let's enforce Legal Name to be "Green".
                    should_update_rs = True

                update_query = text("""
                    UPDATE clientes 
                    SET 
                        estado_arca = 'VALIDADO',
                        datos_arca_last_update = :now,
                        razon_social = :rs,
                        domicilio_fiscal = :dom,
                        condicion_iva_id = :iva_id
                    WHERE id = :id
                """)
                
                # Map IVA Text to ID
                iva_text = data.get('condicion_iva', '').upper()
                iva_id = 1 # Default RI
                if 'MONOTRIBUTO' in iva_text: iva_id = 6
                elif 'EXENTO' in iva_text: iva_id = 4
                elif 'CONSUMIDOR FINAL' in iva_text: iva_id = 5
                
                final_rs = new_rs if should_update_rs else current_rs
                
                session.execute(update_query, {
                    "now": time.strftime('%Y-%m-%d %H:%M:%S'),
                    "rs": final_rs,
                    "dom": data.get('domicilio_fiscal', ''),
                    "iva_id": iva_id,
                    "id": client.id
                })
                
                session.commit()
                print(f"   ✅ Validado! Actualizado a: {data.get('razon_social')}")
                success_count += 1
                
                # Gentle pacing
                time.sleep(0.5) 
                
            except Exception as e:
                print(f"   ❌ Excepción: {e}")
                error_count += 1
                
        print("\n" + "="*40)
        print(f"🏁 Lote Completado.")
        print(f"✅ Exitosos: {success_count}")
        print(f"❌ Fallidos: {error_count}")
        print("="*40)
        
    finally:
        session.close()

if __name__ == "__main__":
    validate_batch()
