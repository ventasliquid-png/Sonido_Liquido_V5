@echo off
ECHO ===============================================
ECHO  ACTIVANDO ENTORNO DE BACKEND (FASTAPI)
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%%~dp0\.."

ECHO Ubicado en la raiz del proyecto.
ECHO Entrando a la carpeta del backend...
cd backend

ECHO Activando entorno virtual de Python...
call venv\Scripts\activate

ECHO Leyendo ruta de credenciales de Google...
set /p GOOGLE_APPLICATION_CREDENTIALS=<..\.google_credentials
ECHO Variable GOOGLE_APPLICATION_CREDENTIALS establecida.

ECHO Iniciando servidor FastAPI con Uvicorn...
uvicorn main:app --reload

ECHO Servidor detenido.
pause
