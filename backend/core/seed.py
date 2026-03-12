from sqlalchemy.orm import Session
from backend.core.database import SessionLocal
from backend.auth import models
from backend.auth.service import get_password_hash
from backend.maestros import models as maestros_models

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

def check_condiciones_iva(db: Session):
    """Crea condiciones de IVA básicas si no existen."""
    defaults = [
        "Responsable Inscripto",
        "Monotributista",
        "Exento",
        "Consumidor Final",
        "No Responsable"
    ]
    for nombre in defaults:
        exists = db.query(maestros_models.CondicionIva).filter(maestros_models.CondicionIva.nombre == nombre).first()
        if not exists:
            print(f"[SEED] Creando Condición IVA: {nombre}")
            db.add(maestros_models.CondicionIva(nombre=nombre))
    db.commit()

def check_segmentos(db: Session):
    """Crea segmentos básicos si no existen."""
    defaults = ["General", "Premium", "Distribuidor", "Retail"]
    for nombre in defaults:
        exists = db.query(maestros_models.Segmento).filter(maestros_models.Segmento.nombre == nombre).first()
        if not exists:
            print(f"[SEED] Creando Segmento: {nombre}")
            db.add(maestros_models.Segmento(nombre=nombre, activo=True))
    db.commit()

def check_provincias(db: Session):
    """Crea provincias de Argentina si no existen."""
    defaults = [
        ("A", "Salta"),
        ("B", "Buenos Aires"),
        ("C", "Capital Federal"),
        ("D", "San Luis"),
        ("E", "Entre Ríos"),
        ("F", "La Rioja"),
        ("G", "Santiago del Estero"),
        ("H", "Chaco"),
        ("J", "San Juan"),
        ("K", "Catamarca"),
        ("L", "La Pampa"),
        ("M", "Mendoza"),
        ("N", "Misiones"),
        ("P", "Formosa"),
        ("Q", "Neuquén"),
        ("R", "Río Negro"),
        ("S", "Santa Fe"),
        ("T", "Tucumán"),
        ("U", "Chubut"),
        ("V", "Tierra del Fuego"),
        ("W", "Corrientes"),
        ("X", "Córdoba"),
        ("Y", "Jujuy"),
        ("Z", "Santa Cruz")
    ]
    for id_prov, nombre in defaults:
        exists = db.query(maestros_models.Provincia).filter(maestros_models.Provincia.id == id_prov).first()
        if not exists:
            print(f"[SEED] Creando Provincia: {nombre} ({id_prov})")
            db.add(maestros_models.Provincia(id=id_prov, nombre=nombre))
        else:
            # Sync name if already exists but different (Update protocol)
            if exists.nombre != nombre:
                exists.nombre = nombre
    db.commit()

def check_vendedores(db: Session):
    """Crea vendedor por defecto si no existe."""
    exists = db.query(maestros_models.Vendedor).first()
    if not exists:
        print("[SEED] Creando Vendedor por defecto: CASA CENTRAL")
        db.add(maestros_models.Vendedor(nombre="CASA CENTRAL", activo=True))
    db.commit()

def seed_all():
    """Ejecuta toda la lógica de siembra."""
    print("--- [Atenea V5 Seed]: Iniciando Protocolo de Siembra... ---")
    db = SessionLocal()
    try:
        check_roles(db)
        check_admin_user(db)
        check_condiciones_iva(db)
        check_segmentos(db)
        check_provincias(db)
        check_vendedores(db)
        print("--- [Atenea V5 Seed]: Protocolo Finalizado CORRECTAMENTE. ---")
    except Exception as e:
        print(f"[ERROR] [SEED ERROR] Fallo en siembra automática: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
