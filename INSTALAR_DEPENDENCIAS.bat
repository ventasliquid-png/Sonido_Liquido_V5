@echo off
chcp 65001 > nul
echo ------------------------------------------------------------------
echo      SONIDO LIQUIDO V5 - INSTALADOR DE DEPENDENCIAS
echo ------------------------------------------------------------------
echo.
echo NOTA: Requiere Python 3.10+ y Node.js instalados previamente.
echo.

echo [1/2] INSTALANDO LIBRERIAS PYTHON (Backend)...
pip install fastapi uvicorn sqlalchemy pydantic pandas openpyxl reportlab pikepdf pypdf customtkinter python-dotenv psycopg2-binary langchain langchain-community langchain-google-vertexai pgvector
if %errorlevel% neq 0 (
    echo [ERROR] Falló la instalación de Python. Verifique su conexión o instalación de Python.
    pause
    exit /b
)
echo [OK] Backend listo.
echo.

echo [2/2] INSTALANDO MODULOS NODE.JS (Frontend)...
cd frontend
if not exist "package.json" (
    echo [ERROR] No encuentro la carpeta frontend/package.json
    pause
    exit /b
)
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Falló la instalación de Node.js.
    pause
    exit /b
)
cd ..
echo [OK] Frontend listo.
echo.

echo ------------------------------------------------------------------
echo        ¡INSTALACION COMPLETADA EXITOSAMENTE!
echo ------------------------------------------------------------------
echo Ya puede ejecutar INICIAR_SISTEMA.bat
pause
