# --- backend/routers/auth.py (V10.7 - Reconstruido) ---
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Importamos los servicios y modelos (que ahora están en el root)
from database import get_db
from models_auth import Usuario, Rol
from service_auth import get_usuario_by_username, get_password_hash, get_rol_by_name # Debemos importar get_rol_by_name

router = APIRouter(
    prefix="/auth",
    tags=["AuthN / AuthZ"]
)

# Esquema de datos para crear un nuevo usuario (Entrada)
class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
    rol_name: str = "operador" # Rol por defecto

# Esquema de datos para la respuesta (Salida)
class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    rol_id: int
    
    class Config:
        orm_mode = True

# --- Endpoint 1: Registro de Nuevo Usuario ---
@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def register_new_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la base de datos (tabla 'usuarios').
    """
    
    # 1. Verificar si el usuario ya existe por username o email
    if get_usuario_by_username(db, username=usuario.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
    if get_usuario_by_email(db, email=usuario.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado.")

    # 2. Encontrar/Crear el Rol
    rol = get_rol_by_name(db, name=usuario.rol_name)
    if not rol:
        raise HTTPException(status_code=404, detail=f"El rol '{usuario.rol_name}' no existe.")

    # 3. Crear el nuevo usuario
    hashed_password = get_password_hash(usuario.password)
    
    db_usuario = Usuario(
        username=usuario.username,
        email=usuario.email,
        hashed_password=hashed_password,
        rol_id=rol.id 
    )

    # 4. Guardar en la base de datos
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return db_usuario

print("--- [Atenea V10.7]: Router de Seguridad definido. ---")