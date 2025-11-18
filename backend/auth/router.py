"""
Módulo Auth (V10.E): Rutas de API (/auth).
Define los endpoints para '/register' y '/token'.

--- [ACTUALIZADO A V10.E (SEGURIDAD)] ---
Añadido endpoint '/token' para login y generación de JWT.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# --- [INICIO FASE 10.E (SEGURIDAD)] ---
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
# --- [FIN FASE 10.E] ---

# --- [INICIO REFACTOR V10.10] ---
from core.database import get_db
from auth import models
from auth import service
# --- [FIN REFACTOR V10.10] ---

# --- [INICIO FASE 10.E (SEGURIDAD)] ---
# Importamos los schemas y servicios de token actualizados
from auth.schemas import UsuarioCreate, UsuarioOut, Token
from core.config import ACCESS_TOKEN_EXPIRE_MINUTES
# --- [FIN FASE 10.E] ---


router = APIRouter(
    prefix="/auth",
    tags=["AuthN / AuthZ (V10.E)"] # Etiqueta actualizada
)

# --- Endpoint 1: Registro de Nuevo Usuario (Existente) ---
@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def register_new_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en la base de datos (tabla 'usuarios').
    """
    
    # 1. Verificar si el usuario ya existe
    if service.get_usuario_by_username(db, username=usuario.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado.")
    if service.get_usuario_by_email(db, email=usuario.email):
        raise HTTPException(status_code=400, detail="El email ya está registrado.")

    # 2. Encontrar/Crear el Rol
    rol = service.get_rol_by_name(db, name=usuario.rol_name)
    if not rol:
        raise HTTPException(status_code=404, detail=f"El rol '{usuario.rol_name}' no existe.")

    # 3. Crear el nuevo usuario
    hashed_password = service.get_password_hash(usuario.password)
    
    db_usuario = models.Usuario(
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

# --- [INICIO FASE 10.E (NUEVO ENDPOINT DE LOGIN)] ---

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Endpoint de Login.
    Recibe un formulario (username/password) y devuelve un Token JWT.
    """
    # 1. Autenticar al usuario (verificar si el user/pass son correctos)
    usuario = service.authenticate_user(db, form_data.username, form_data.password)
    
    if not usuario:
        # Si falla, denegamos el acceso
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. Crear el Token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = service.create_access_token(
        data={"sub": usuario.username}, # Guardamos el 'username' como el "subject" (sub) del token
        expires_delta=access_token_expires
    )
    
    # 3. Devolver el token
    return {"access_token": access_token, "token_type": "bearer"}

# --- [FIN FASE 10.E] ---

print("--- [Atenea V10.E]: Auth/Router (Seguridad y Login) definido. ---")
