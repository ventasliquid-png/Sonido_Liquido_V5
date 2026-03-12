from backend.core.database import SessionLocal
from backend.auth.models import Rol

def init_roles():
    db = SessionLocal()
    try:
        # Check Role ID 1
        rol_admin = db.query(Rol).filter(Rol.id == 1).first()
        if not rol_admin:
            print("Rol ID 1 no encontrado. Creando...")
            # Check if name 'Administrador' exists with other ID
            rol_by_name = db.query(Rol).filter(Rol.name == "Administrador").first()
            if rol_by_name:
                print(f"[WARN] Rol 'Administrador' ya existe con ID {rol_by_name.id}. No se puede forzar ID 1 facilmente.")
            else:
                new_rol = Rol(name="Administrador", description="Acceso total")
                db.add(new_rol)
                db.commit()
                print("Rol 'Administrador' creado (debería ser ID 1).")
        else:
            print(f"Rol ID 1 encontrado: {rol_admin.name}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_roles()
