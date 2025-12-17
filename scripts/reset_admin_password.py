import sys
import os

# Add backend directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from core.database import SessionLocal
from backend.auth import models, service
from sqlalchemy.orm import Session

def reset_password():
    print("--- [AUTH] Realizando Reset de Contraseña Admin ---")
    db = SessionLocal()
    try:
        username = "admin"
        new_password = "admin123"
        
        user = service.get_usuario_by_username(db, username)
        if not user:
            print(f"❌ Error: Usuario '{username}' no encontrado.")
            return

        print(f"   -> Usuario '{username}' encontrado.")
        print(f"   -> Generando nuevo hash para '{new_password}'...")
        
        new_hash = service.get_password_hash(new_password)
        user.hashed_password = new_hash
        
        db.add(user)
        db.commit()
        
        print(f"✅ ÉXITO: La contraseña del usuario '{username}' ha sido reseteada a '{new_password}'.")

    except Exception as e:
        print(f"❌ Error durante el reset: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()
