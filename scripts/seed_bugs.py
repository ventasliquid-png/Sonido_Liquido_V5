import sys
import os
import uuid
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.core.database import SessionLocal, engine
from backend.core.models import BugTracking, SistemaConfig
from datetime import datetime, timezone
from sqlalchemy import text

def run_migration():
    print("--- Ejecutando migración SQL manual ---")
    with engine.begin() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sistema_config (
            id INTEGER PRIMARY KEY,
            flags_estado INTEGER DEFAULT 0,
            version_sistema VARCHAR,
            fecha_ultima_sync DATETIME
        );
        """))
        
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS bugs (
            id CHAR(32) PRIMARY KEY,
            nro_sesion INTEGER,
            descripcion VARCHAR,
            detalle VARCHAR,
            fecha_ocurrencia DATETIME,
            fecha_resolucion DATETIME,
            resuelto BOOLEAN DEFAULT 0,
            entorno VARCHAR,
            version_sistema VARCHAR
        );
        """))

def run_seed():
    print("--- Ejecutando seed_bugs ---")
    db = SessionLocal()
    
    # 1. Asegurar config base
    config = db.query(SistemaConfig).filter(SistemaConfig.id == 1).first()
    if not config:
        print("Creando registro SistemaConfig inicial...")
        config = SistemaConfig(id=1, flags_estado=0)
        db.add(config)
        db.commit()

    # 2. Insertar bugs
    bugs_data = [
        {"nro_sesion": 793, "descripcion": "Vínculos invisibles ficha cliente", "resuelto": True, "detalle": "", "entorno": "D"},
        {"nro_sesion": None, "descripcion": "Bug A — buscador modal pisa referencia PDF", "resuelto": False, "detalle": "IngestaItemSearchTerm.value = ''", "entorno": "D"},
        {"nro_sesion": None, "descripcion": "Bug B — ESC no restaura modal 409", "resuelto": False, "detalle": "", "entorno": "D"},
        {"nro_sesion": None, "descripcion": "Bug C — flujo pedido→factura→remito incompleto", "resuelto": False, "detalle": "", "entorno": "D"},
        {"nro_sesion": None, "descripcion": "Clientes azules — multi-entidad CUIT compartido", "resuelto": False, "detalle": "", "entorno": "D"},
        {"nro_sesion": None, "descripcion": "Build P — frontend no compilado", "resuelto": False, "detalle": "", "entorno": "D"},
        {"nro_sesion": None, "descripcion": "DESPERTAR encoding", "resuelto": True, "detalle": "", "entorno": "D"}
    ]
    
    for b in bugs_data:
        bug = BugTracking(**b)
        db.add(bug)
    
    hay_pendientes = any(not b["resuelto"] for b in bugs_data)
    
    if hay_pendientes:
        config.flags_estado |= 32
    else:
        config.flags_estado &= ~32
        
    db.commit()
    print("Seed exitoso.")

if __name__ == "__main__":
    run_migration()
    run_seed()
