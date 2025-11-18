"""
Módulo Auth (V10.E): Dependencias de Seguridad para FastAPI.
Define dependencias reutilizables para proteger endpoints con autenticación JWT.

--- USO ---
from auth.dependencies import get_current_user, get_current_active_user

@router.post("/endpoint")
def protected_endpoint(
    current_user: Usuario = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # current_user está garantizado como usuario autenticado y activo
    pass
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from jose import JWTError, jwt

from auth import models
from auth import service
from core.database import get_db
from core.config import SECRET_KEY, ALGORITHM

# OAuth2PasswordBearer maneja automáticamente el header "Authorization: Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.Usuario:
    """
    Dependencia OBLIGATORIA para obtener el usuario actual desde el token JWT.
    
    Si el token es inválido o no existe, lanza HTTPException 401.
    Retorna el objeto Usuario completo.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: no se encontró 'sub' (username)",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    usuario = service.get_usuario_by_username(db, username=username)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return usuario

def get_current_active_user(
    current_user: models.Usuario = Depends(get_current_user)
) -> models.Usuario:
    """
    Dependencia OBLIGATORIA para obtener el usuario actual ACTIVO.
    
    Extiende get_current_user verificando que el usuario esté activo.
    Si el usuario está inactivo, lanza HTTPException 403.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    return current_user

print("--- [Atenea V10.E]: Auth/Dependencies (Seguridad JWT) definidas. ---")

