from backend.core.database import SessionLocal
from backend.auth.models import Usuario
from backend.auth.service import get_password_hash

def reset_admin():
    db = SessionLocal()
    try:
        user = db.query(Usuario).filter(Usuario.username == "admin").first()
        if not user:
            print("Usuario 'admin' no encontrado. Creando...")
            user = Usuario(
                username="admin",
                email="admin@sonidoliquido.com",
                hashed_password=get_password_hash("admin"),
                is_active=True,
                is_superuser=True
            )
            db.add(user)
        else:
            print("Usuario 'admin' encontrado. Reseteando password...")
            user.hashed_password = get_password_hash("admin")
            user.is_active = True
        
        db.commit()
        print("EXITO: Usuario 'admin' configurado con password 'admin'")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin()
