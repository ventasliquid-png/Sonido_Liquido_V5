import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.database import SessionLocal
from backend.auth import models, service

def create_admin_user():
    print("--- [SEED] Creating Admin User ---")
    db = SessionLocal()
    try:
        username = "admin"
        password = "admin123"
        email = "admin@sonidoliquido.com"
        rol_name = "Admin" # Assuming roles exist or we need to create them?
        
        # Check if user exists
        existing_user = service.get_usuario_by_username(db, username)
        if existing_user:
            print(f"   -> User '{username}' already exists.")
            return

        # Check/Create Role
        rol = service.get_rol_by_name(db, rol_name)
        if not rol:
            print(f"   -> Role '{rol_name}' not found. Creating it...")
            rol = models.Rol(name=rol_name, description="Administrator with full access")
            db.add(rol)
            db.commit()
            db.refresh(rol)
            print(f"   -> Role '{rol_name}' created.")

        # Create User
        print(f"   -> Creating user '{username}'...")
        hashed_password = service.get_password_hash(password)
        user = models.Usuario(
            username=username,
            email=email,
            hashed_password=hashed_password,
            rol_id=rol.id,
            is_active=True
        )
        db.add(user)
        db.commit()
        print(f"   -> User '{username}' created successfully.")

    except Exception as e:
        print(f"   -> Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()
    print("--- [SEED] Completed ---")

if __name__ == "__main__":
    create_admin_user()
