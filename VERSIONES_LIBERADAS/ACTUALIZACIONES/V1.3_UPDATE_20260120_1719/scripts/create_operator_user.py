import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.database import SessionLocal
from backend.auth import models, service

def create_operator_user():
    print("--- [SEED] Creating Operator User ---")
    db = SessionLocal()
    try:
        username = "operador"
        password = "operador123"
        email = "operador@sonidoliquido.com"
        # Use existing Role or Create generic one?
        # Let's assign Admin role for now to avoid permission issues, or generic "User".
        # Assuming "Admin" role exists (id 1 usually).
        
        rol = service.get_rol_by_name(db, "Admin") # Give full access for data entry to avoid blocks
        if not rol:
            print("   -> Role Admin not found? Using first available.")
            rol = db.query(models.Rol).first()
        
        # Check if user exists
        existing_user = service.get_usuario_by_username(db, username)
        if existing_user:
            print(f"   -> User '{username}' already exists. Reseting password...")
            existing_user.hashed_password = service.get_password_hash(password)
            db.add(existing_user)
            db.commit()
            print(f"   -> Password for '{username}' reset to '{password}'.")
            return

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
        print(f"   -> Error creating user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_operator_user()
