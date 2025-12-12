from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.auth import models
from backend.auth.service import get_password_hash

def check_roles(db: Session):
    """Verifica y crea los roles básicos (idempotente)."""
    admin_rol = db.query(models.Rol).filter(models.Rol.id == 1).first()
    if not admin_rol:
        print("[SEED] Creando Rol 'Administrador' (ID 1)...")
        # Intentamos buscar por nombre para evitar duplicados si ID difiere
        existing = db.query(models.Rol).filter(models.Rol.name == "Administrador").first()
        if existing:
             print(f"[WARN] [SEED] Rol 'Administrador' ya existe con ID {existing.id}. Saltando creación forzada de ID 1.")
        else:
            new_rol = models.Rol(id=1, name="Administrador", description="Acceso total al sistema")
            db.add(new_rol)
            db.commit()
            print("[OK] [SEED] Rol 'Administrador' creado.")
    else:
        print("[OK] [SEED] Rol 'Administrador' verificado.")

def check_admin_user(db: Session):
    """Verifica y crea el usuario admin (idempotente)."""
    admin_user = db.query(models.Usuario).filter(models.Usuario.username == "admin").first()
    if not admin_user:
        print("[SEED] Creando Usuario 'admin'...")
        hashed = get_password_hash("admin")
        new_admin = models.Usuario(
            username="admin",
            email="admin@sonidoliquido.com",
            hashed_password=hashed,
            is_active=True,
            rol_id=1
        )
        db.add(new_admin)
        db.commit()
        print("[OK] [SEED] Usuario 'admin' creado exitosamente.")
    else:
        print("[OK] [SEED] Usuario 'admin' verificado.")

def seed_all():
    """Ejecuta toda la lógica de siembra."""
    print("--- [Atenea V5 Seed]: Iniciando Protocolo de Siembra... ---")
    db = SessionLocal()
    try:
        check_roles(db)
        check_admin_user(db)
        print("--- [Atenea V5 Seed]: Protocolo Finalizado CORRECTAMENTE. ---")
    except Exception as e:
        print(f"[ERROR] [SEED ERROR] Fallo en siembra automática: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
