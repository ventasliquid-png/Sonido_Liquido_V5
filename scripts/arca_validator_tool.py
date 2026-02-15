
import sys
import os
import sqlite3
import pandas as pd
from typing import List, Optional

# Add project root to sys.path to allow imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.clientes.services.afip_bridge import AfipBridgeService
from backend.clientes.models import Cliente, Domicilio
# We need a minimal DB session here without full Backend overhead if possible, 
# but reusing backend logic is safer for integrity.
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- CONFIG ---
DATABASE_URL = "sqlite:///./pilot.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def scan_pending_clients(db):
    print("\n--- [SCAN] Buscando clientes PENDIENTES o SIN VALIDAR ---")
    clients = db.query(Cliente).filter(
        (Cliente.estado_arca != 'VALIDADO') | (Cliente.estado_arca == None)
    ).all()
    
    if not clients:
        print("✅ No hay clientes pendientes de validación.")
        return []
    
    data = []
    for c in clients:
        data.append({
            "ID": str(c.id)[:8],
            "Razon Social": c.razon_social,
            "CUIT": c.cuit,
            "Estado": c.estado_arca or "N/A"
        })
    
    df = pd.DataFrame(data)
    print(df.to_string(index=False))
    print(f"\nTotal Pendientes: {len(clients)}")
    return clients

def validate_client(db, client_id=None, manual_cuit=None):
    """
    Validates a client against ARCA.
    If client_id provided, updates that client.
    If manual_cuit provided, looks for client with that CUIT or CREATE/UPDATE suggestion?
    User asked: 'me dé el cuit que tiene La Toronja SA... O bien vos... ponees en google... Yo te pondría "Ok"'
    """
    
    target_cuit = manual_cuit
    client_obj = None

    if client_id:
        # Find by internal ID (UUID or partial)
        # For simplicity in this CLI we might use UUID or exact match
        # Let's assume we pass the object or UUID
        client_obj = db.query(Cliente).filter(Cliente.id.like(f"{client_id}%")).first()
        if client_obj:
            print(f"\n[*] Validando Cliente Existente: {client_obj.razon_social} ({client_obj.cuit})")
            target_cuit = client_obj.cuit
        else:
            print(f"❌ Cliente ID {client_id} no encontrado.")
            return

    if not target_cuit:
        print("❌ No se especificó CUIT.")
        return

    # --- CALL ARCA ---
    print(f"    >> Consultando AFIP para CUIT: {target_cuit}...")
    res = AfipBridgeService.get_datos_afip(target_cuit)
    
    if "error" in res:
        print(f"    ❌ ERROR ARCA: {res['error']}")
        return

    # --- SHOW RESULT ---
    print("\n    ✅ [RESULTADO ARCA]")
    print(f"    Razón Social: {res['razon_social']}")
    print(f"    Condición IVA: {res['condicion_iva']}")
    print(f"    Domicilio Fiscal: {res['domicilio_fiscal']}")
    
    # Check for smart address fields
    raw_data = res.get("raw_debug", {}) # rar_core might not pass extra fields in standard dict unless we update normalize_for_v5
    # Wait, existing AfipBridgeService.normalize_for_v5() returns a dict.
    # We need to check if 'piso'/'depto' are in res (if we updated rar_core and bridge to pass them).
    # RAR Core update in previous step adds 'parsed_address' to logic, but `get_datos_afip` returns the dict.
    # We need to make sure `AfipBridgeService` passes these through.
    
    # Interactive Confirmation
    confirm = input("\n    ¿Aplicar cambios a la base de datos? (S/N): ").strip().upper()
    if confirm != 'S':
        print("    [X] Cancelado por usuario.")
        return

    # --- APPLY UPDATE ---
    # Smart Address Update logic
    # If client exists, update. If not (Manual CUIT mode), implies creation or search?
    if not client_obj:
        # Search by CUIT
        client_obj = db.query(Cliente).filter(Cliente.cuit == target_cuit).first()
    
    if client_obj:
        client_obj.razon_social = res['razon_social']
        client_obj.estado_arca = 'VALIDADO'
        client_obj.datos_arca_last_update = "NOW()" # Use real timestamp
        
        # Update Domicilio Fiscal
        # We need to be careful not to overwrite 'Entrega' if it's different?
        # Usually Fiscal is separate.
        # Find Fiscal Domicile
        dom_fiscal = next((d for d in client_obj.domicilios if d.es_fiscal), None)
        if not dom_fiscal:
            # Create one?
             pass 
        else:
            dom_fiscal.calle = res.get('domicilio_fiscal', dom_fiscal.calle) # Ideally use parsed fields
            # For now simple string update unless we patch Bridge to return parsed fields
        
        db.commit()
        print("    ✅ Base de datos actualizada.")
    else:
        print("    ⚠️ El cliente no existe en la BD local. (Creación no implementada en este script simple).")

def main():
    db = SessionLocal()
    try:
        while True:
            print("\n=== PINTOR ARCA (V5 Validator Tool) ===")
            print("1. Escanear Pendientes")
            print("2. Validar Cliente por ID")
            print("3. Validar CUIT Manual (Arbitrario)")
            print("4. Validar 'Lácteos de Poblet' (33-66072685-9)")
            print("0. Salir")
            
            op = input("\nOpción: ").strip()
            
            if op == '1':
                scan_pending_clients(db)
            elif op == '2':
                cid = input("Ingrese ID (primeros 8 chars): ").strip()
                validate_client(db, client_id=cid)
            elif op == '3':
                c = input("Ingrese CUIT (sin guiones): ").strip()
                validate_client(db, manual_cuit=c)
            elif op == '4':
                validate_client(db, manual_cuit="33660726859")
            elif op == '0':
                break
    finally:
        db.close()

if __name__ == "__main__":
    main()
