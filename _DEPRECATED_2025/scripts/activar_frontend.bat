@echo off
ECHO ===============================================
ECHO  ACTIVANDO ENTORNO DE FRONTEND (VUE.JS)
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%%~dp0\.."

ECHO Ubicado en la raiz del proyecto.
ECHO Entrando a la carpeta del frontend...
cd frontend

ECHO Iniciando servidor de desarrollo de Vite...
REM [PARCHE V11.1]: Usamos NPX para evitar la falla de resolucion de ruta de NPM.
npx vite

pause