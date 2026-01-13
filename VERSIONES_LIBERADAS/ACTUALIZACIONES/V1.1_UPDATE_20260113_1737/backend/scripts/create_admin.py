import sys
import os

# Add project root and backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
backend_dir = os.path.join(root_dir, "backend")
sys.path.append(root_dir)
sys.path.append(backend_dir)

from sqlalchemy.orm import Session
from core.database import SessionLocal
from backend.auth import models, service

def create_admin():
    print("--- Creando Usuario Admin ---")
    db = SessionLocal()
    try:
        # 1. Crear Rol Admin
        rol_admin = service.get_rol_by_name(db, "Admin")
        if not rol_admin:
            print("Creando rol 'Admin'...")
            rol_admin = models.Rol(name="Admin", description="Administrador del Sistema")
            db.add(rol_admin)
            db.commit()
            db.refresh(rol_admin)
        else:
            print("Rol 'Admin' ya existe.")

        # 2. Crear Usuario Admin
        user_admin = service.get_usuario_by_username(db, "admin")
        if not user_admin:
            print("Creando usuario 'admin'...")
            hashed_pwd = service.get_password_hash("admin123")
            user_admin = models.Usuario(
                username="admin",
                email="admin@sonidoliquido.com",
                hashed_password=hashed_pwd,
                rol_id=rol_admin.id,
                is_active=True
            )
            db.add(user_admin)
            db.commit()
            print("✅ Usuario 'admin' creado (Pass: admin123).")
        else:
            print("Usuario 'admin' ya existe.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
