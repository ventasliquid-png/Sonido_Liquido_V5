
import sys
import os
import uuid
import json
from datetime import datetime, timezone

# Add project root to path
sys.path.append(os.getcwd())

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
# from backend.core.database import DATABASE_URL # Skip env var to force SQLite
from backend.contactos.models import Persona, Vinculo, Base

def run_migration():
    print("🚀 Iniciando Migración Multiplex (V6)...")
    
    # FORCE SQLITE (PILOT.DB)
    # backend/core/database.py logic fallback
    project_root = os.getcwd() # Assumes running from root
    pilot_db_path = os.path.join(project_root, "pilot.db")
    DATABASE_URL = f"sqlite:///{pilot_db_path}"
    print(f"--- [MIGRATION] Forzando DB Local: {DATABASE_URL} ---")
    
    # Init DB
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # 0. Limpiar tablas nuevas si existen (Schema Reset)
        print("🧹 Limpiando tablas previas 'personas' y 'vinculos'...")
        Vinculo.__table__.drop(engine, checkfirst=True)
        Persona.__table__.drop(engine, checkfirst=True)

        # 1. Crear Tablas Nuevas
        print("🛠️  Creando tablas 'personas' y 'vinculos'...")
        Base.metadata.create_all(engine)
        
        # 2. Leer Datos Legacy
        print("📖 Leyendo tabla 'contactos' (Legacy)...")
        try:
            result = session.execute(text("SELECT * FROM contactos"))
            rows = result.mappings().all()
        except Exception as e:
            print(f"❌ Error leyendo 'contactos': {e}")
            print("   (Tal vez la tabla no existe o ya fue migrada?)")
            return

        if not rows:
            print("⚠️  Tabla 'contactos' vacía. Nada que migrar.")
            return

        migrated_count = 0
        
        def parse_date(date_val):
            if not date_val: return datetime.now(timezone.utc)
            if isinstance(date_val, (datetime,)): return date_val
            if isinstance(date_val, str):
                try:
                    # Intenta formato ISO standard
                    return datetime.fromisoformat(date_val)
                except ValueError:
                    try:
                        # Fallback comun en SQLite "YYYY-MM-DD HH:MM:SS.ssssss"
                        return datetime.strptime(date_val, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        return datetime.now(timezone.utc)
            return datetime.now(timezone.utc)

        for row in rows:
            # 3. Crear Persona
            # Importante: Generamos nueva ID para Persona para empezar limpio.
            nueva_persona_id = uuid.uuid4()
            
            created_at = parse_date(row['created_at'])
            updated_at = parse_date(row['updated_at'])

            persona = Persona(
                id=nueva_persona_id,
                nombre=row['nombre'],
                apellido=row['apellido'],
                notas_globales=row['notas'],
                domicilio_personal=row['domicilio_personal'],
                canales_personales=[], # Vacio por seguridad
                # Fechas
                created_at=created_at,
                updated_at=updated_at
            )
            session.add(persona)

            # 4. Crear Vínculo (Si corresponde)
            entidad_tipo = None
            entidad_id = None
            
            if row['cliente_id']:
                entidad_tipo = 'CLIENTE'
                entidad_id = row['cliente_id']
            elif row['transporte_id']:
                entidad_tipo = 'TRANSPORTE'
                entidad_id = row['transporte_id']
            
            if entidad_tipo:
                # Mover Canales a Laborales
                canales_laborales = []
                if row['canales']:
                    # Asegurar que es lista (depende del driver DB, a veces viene como string)
                    if isinstance(row['canales'], str):
                        try:
                            canales_laborales = json.loads(row['canales'])
                        except:
                            canales_laborales = []
                    else:
                        canales_laborales = row['canales']

                vinculo = Vinculo(
                    id=uuid.uuid4(),
                    persona_id=nueva_persona_id,
                    entidad_tipo=entidad_tipo,
                    entidad_id=entidad_id,
                    rol=row['puesto'], # Puesto mapea a Rol en el vínculo
                    area=None,
                    canales_laborales=canales_laborales,
                    notas_vinculo=f"Migrado desde Contacto Legacy (Ref: {row['referencia_origen'] or 'N/A'})",
                    activo=row['estado'],
                    fecha_inicio=created_at.date() # Convertir a date object
                )
                session.add(vinculo)
            
            migrated_count += 1
            if migrated_count % 10 == 0:
                print(f"   ... procesados {migrated_count}")

        # 5. Commit
        session.commit()
        print(f"✅ Migración Exitosa: {migrated_count} registros transformados.")
        
        # Opcional: Renombrar tabla vieja para backup
        # print("📦 Archivando tabla 'contactos' a 'contactos_old_v5'...")
        # session.execute(text("ALTER TABLE contactos RENAME TO contactos_old_v5"))
        # session.commit()
        
    except Exception as e:
        session.rollback()
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    run_migration()
