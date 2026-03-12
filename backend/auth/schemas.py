"""
Módulo Auth (V10.E): Esquemas Pydantic.
Define los modelos de datos de entrada (Create) y salida (Out) para la API.

--- [ACTUALIZADO A V10.E (SEGURIDAD)] ---
Añadidos esquemas para 'Token' y 'TokenData'.
"""
from pydantic import BaseModel
from typing import Optional # <--- Añadido en V10.E

# --- Esquemas de Usuario (Existentes) ---

class UsuarioCreate(BaseModel):
    username: str
    email: str
    password: str
    rol_name: str = "operador" # Rol por defecto si no se especifica

class UsuarioOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    rol_id: int
    
    class Config:
        from_attributes = True 

# --- [INICIO FASE 10.E (SEGURIDAD)] ---

class Token(BaseModel):
    """
    El esquema que se devuelve al cliente/frontend al iniciar sesión.
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    El esquema de los datos que guardamos DENTRO del JWT.
    (El 'sub' es el 'subject', que usaremos para guardar el username).
    """
    username: Optional[str] = None

# --- [FIN FASE 10.E] ---

print("--- [Atenea V10.E]: Auth/Schemas (Pydantic con Tokens) definidos. ---")
