from fastapi import APIRouter, HTTPException
import asyncio
import random

router = APIRouter(prefix="/agenda/google", tags=["Agenda Google Mock"])

@router.get("/auth")
async def mock_auth():
    """Simula el inicio del flujo OAuth"""
    # En producción esto redirigiría a Google
    return {"status": "redirect", "url": "http://localhost:8000/agenda/google/callback?code=mock_code_123"}

@router.get("/callback")
async def mock_callback(code: str):
    """Simula el callback de Google"""
    return {
        "status": "success", 
        "message": "Autenticación Simulada Exitosa (Estrategia Local First)",
        "mock_token": "ya29.mock_token_xyz"
    }

@router.post("/sync")
async def mock_sync():
    """Simula el proceso de sincronización"""
    await asyncio.sleep(2) # Simular latencia de red
    
    # Simular coin toss para errores
    if random.random() < 0.1:
        raise HTTPException(status_code=503, detail="Error de conexión simulado con Google API")
        
    return {
        "status": "success",
        "synced_count": 0,
        "message": "Sincronización Simulada Completada. (Modo Local: No se enviaron datos a la nube)"
    }
