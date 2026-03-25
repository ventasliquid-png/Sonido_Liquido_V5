import sys
import os
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import SessionLocal
from backend.clientes.models import Domicilio, Cliente, domicilios_clientes
from backend.pedidos.models import Pedido

def heal():
    db = SessionLocal()
    try:
        print("--- [CURA DE ESTRATOS] Iniciando Sanación de Domicilios (V5.2.3 GOLD) ---")
        
        # 1. Total Count
        total = db.query(Domicilio).count()
        print(f"Total Domicilios en DB: {total}")
        
        domicilios = db.query(Domicilio).all()
        healed_count = 0
        hub_count = 0
        history_count = 0
        
        for dom in domicilios:
            original_bits = dom.bit_identidad or 0
            new_bits = original_bits
            
            # [BIT 0] ACTIVO (1) - Base state
            if original_bits == 0:
                new_bits |= 1
            
            # [BIT 1] HISTORIAL (2) - Protection against deletion
            # Check orders or remitos
            has_orders = db.query(Pedido).filter(Pedido.domicilio_entrega_id == dom.id).count() > 0
            if has_orders:
                new_bits |= 2
            
            # [BIT 6] HUB (64) - Auto-Set: Links > 1
            usage = db.query(domicilios_clientes).filter(domicilios_clientes.c.domicilio_id == dom.id).count()
            if usage > 1:
                new_bits |= 64
            else:
                new_bits &= ~64
            
            # [BIT 12] SOBERANIA GOLD (4096)
            # Requirements: Alias, Provincia, Maps Verified (Manual)
            has_alias = bool(dom.alias)
            has_provincia = bool(dom.provincia_id)
            is_verified = bool(dom.is_maps_manual)
            
            if has_alias and has_provincia and is_verified:
                new_bits |= 4096
            else:
                new_bits &= ~4096 # Clear if not fully sovereign yet
            
            if new_bits != original_bits:
                dom.bit_identidad = new_bits
                db.add(dom)
                healed_count += 1
        
        db.commit()
        print(f"--- [RESULTADOS] ---")
        print(f"Domicilios Sanados: {healed_count}")
        print(f"HUBs Detectados: {hub_count}")
        print(f"Con Historia Logística: {history_count}")
        print("--- [CURA COMPLETADA] ---")
        
    except Exception as e:
        db.rollback()
        print(f"Error durante la cura: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    heal()
