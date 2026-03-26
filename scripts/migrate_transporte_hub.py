# scripts/migrate_transporte_hub.py
import os
import sys
import uuid
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.getcwd())

# FORCE SQLITE for local migration
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(os.getcwd(), 'pilot_v5x.db')}"

from backend.core.database import SessionLocal
from sqlalchemy.orm import configure_mappers

# Comprehensive model import to avoid mapper errors
import backend.maestros.models
import backend.auth.models
import backend.proveedores.models
import backend.productos.models
import backend.clientes.models
import backend.pedidos.models
import backend.contactos.models
import backend.logistica.models
import backend.remitos.models

# Force mapper configuration
try:
    configure_mappers()
except Exception as e:
    print(f"[!] Warning during configure_mappers: {e}")

from backend.logistica.models import EmpresaTransporte, NodoTransporte
from backend.clientes.models import Domicilio
from backend.contactos.models import VinculoGeografico

def migrate():
    db = SessionLocal()
    try:
        transportes = db.query(EmpresaTransporte).all()
        print(f"[*] Iniciando migración de {len(transportes)} transportes...")

        for t in transportes:
            print(f"  > Procesando: {t.nombre}")
            
            # 1. Calibrar Flags (Si no están seteados)
            # Bit 0: Existence (1), Bit 1: Active (2)
            # Bit 2: Pickup (4), Bit 5: Web Required (32)
            new_flags = 1 | 2 # Base
            if t.servicio_retiro_domicilio: new_flags |= 4
            if t.requiere_carga_web: new_flags |= 32
            
            # Bit 21: Mirror (2097152) - Por defecto asumimos espejo si no hay otra direccion
            is_mirror = False
            if not t.direccion_despacho or t.direccion_despacho == t.direccion:
                new_flags |= 2097152
                is_mirror = True
            
            t.flags_estado = new_flags

            # 2. Migrar Dirección Fiscal -> Hub
            if t.direccion:
                # Buscar si ya tiene vínculo fiscal
                vinculo_fiscal = db.query(VinculoGeografico).filter(
                    VinculoGeografico.entidad_id == t.id,
                    VinculoGeografico.entidad_tipo == 'TRANSPORTE',
                    VinculoGeografico.flags_relacion.op('&')(1) == 1
                ).first()

                if not vinculo_fiscal:
                    dom = Domicilio(
                        alias=f"Fiscal - {t.nombre}",
                        calle=t.direccion,
                        localidad=t.localidad,
                        provincia_id=t.provincia_id,
                        es_fiscal=True
                    )
                    db.add(dom)
                    db.flush()
                    
                    vg = VinculoGeografico(
                        entidad_id=t.id,
                        entidad_tipo='TRANSPORTE',
                        domicilio_id=dom.id,
                        alias="FISCAL",
                        flags_relacion=1 # FISCAL
                    )
                    db.add(vg)
                    print(f"    [+] Dirección Fiscal migrada al Hub.")
                else:
                    print(f"    [.] Dirección Fiscal ya existe en el Hub.")

            # 3. Migrar Dirección Despacho (Si no es espejo)
            if not is_mirror and t.direccion_despacho:
                vinculo_despacho = db.query(VinculoGeografico).filter(
                    VinculoGeografico.entidad_id == t.id,
                    VinculoGeografico.entidad_tipo == 'TRANSPORTE',
                    VinculoGeografico.flags_relacion.op('&')(2) == 2
                ).first()

                if not vinculo_despacho:
                    dom = Domicilio(
                        alias=f"Despacho - {t.nombre}",
                        calle=t.direccion_despacho,
                        localidad="CABA", # Según doctrina en models.py
                        provincia_id="CABA",
                        es_entrega=True
                    )
                    db.add(dom)
                    db.flush()
                    
                    vg = VinculoGeografico(
                        entidad_id=t.id,
                        entidad_tipo='TRANSPORTE',
                        domicilio_id=dom.id,
                        alias="DESPACHO",
                        flags_relacion=2 # ENTREGA/DESPACHO
                    )
                    db.add(vg)
                    print(f"    [+] Dirección Despacho migrada al Hub (Espejo Roto).")
            
        db.commit()
        print("[*] Migración finalizada con éxito.")
    except Exception as e:
        db.rollback()
        print(f"[!] Error en migración: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
