import sys
import os

# FORCE ABSOLUTE PATH TO PROJECT ROOT
ROOT_DIR = r"C:\dev\Sonido_Liquido_V5"
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.core.database import SessionLocal
from backend.clientes.services.afip_bridge import AfipBridgeService
import time
from sqlalchemy import text

def validate_batch():
    session = SessionLocal()
    try:
        print("🔍 Buscando clientes pendientes de validación ARCA...")
        
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
        
        # Generic CUITs to skip
        GENERIC_CUITS = ['11111111119', '11111111111', '00000000000']
        
        for idx, client in enumerate(clients):
            print(f"\n[{idx+1}/{total}] Procesando: {client.razon_social} ({client.cuit})")
            
            # Skip Generics
            if client.cuit in GENERIC_CUITS:
                print(f"   ⚠️ CUIT Genérico detectado. Saltando validación externa.")
                # We could mark them as VALIDADO to stop asking?
                # Let's mark them as VALIDADO with local data preservation
                update_query = text("""
                    UPDATE clientes SET estado_arca = 'VALIDADO', datos_arca_last_update = :now 
                    WHERE id = :id
                """)
                session.execute(update_query, {"now": time.strftime('%Y-%m-%d %H:%M:%S'), "id": client.id})
                session.commit()
                continue

            try:
                data = AfipBridgeService.get_datos_afip(client.cuit)
                
                if not data or 'error' in data:
                    print(f"   ❌ Error del Puente: {data.get('error') if data else 'Sin Datos'}")
                    error_count += 1
                    continue
                    
                # UBA / Specific Name Logic
                current_rs = client.razon_social or ''
                new_rs = data.get('razon_social')
                
                should_update_rs = False
                if not current_rs or current_rs in ['CONSUMIDOR FINAL', 'S/D', '']:
                    should_update_rs = True
                elif new_rs and new_rs != current_rs:
                    # Check similarity? For now, if different, we update (Tax Compliant)
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
                
                iva_text = data.get('condicion_iva', '').upper()
                iva_id = 1
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
                print(f"   ✅ Validado! Actualizado a: {final_rs}")
                success_count += 1
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
