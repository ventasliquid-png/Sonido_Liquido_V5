# ==================================================================
#  AUXILIAR DE INSTALACION V8 (PowerShell)
#  Ejecutar en una carpeta 100% vacia.
# ==================================================================

$ErrorActionPreference = "Stop" # El script se detendrá ante cualquier error
$ProjectRoot = "C:\dev\Sonido_Liquido_V5"
Set-Location $ProjectRoot

Write-Host "===============================================" -ForegroundColor Green
Write-Host "  INSTALANDO ENTORNO: SONIDO LIQUIDO V5 (V8 - PowerShell)" -ForegroundColor Green
Write-Host "==============================================="
Write-Host "Ubicacion: $ProjectRoot"
Write-Host ""

# --- PASO 0: VERIFICACION DE PRERREQUISITOS ---
Write-Host "--- 0. Verificando Prerrequisitos (Git, Python, Node.js)... ---" -ForegroundColor Cyan
try {
    Get-Command git | Out-Null
    Write-Host "Git... OK." -ForegroundColor Green
    Get-Command python | Out-Null
    Write-Host "Python... OK." -ForegroundColor Green
    Get-Command node | Out-Null
    Write-Host "Node.js... OK." -ForegroundColor Green
    Write-Host "`n¡Prerrequisitos validados!"
} catch {
    Write-Host "[ERROR] Falta un prerrequisito (Git, Python o Node)." -ForegroundColor Red
    Write-Host "Mensaje: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir..."
    exit
}
Write-Host ""

# --- PASO 1: INICIALIZAR REPOSITORIO Y .GITIGNORE ---
Write-Host "--- 1. Inicializando Repositorio local (Git Init) ---" -ForegroundColor Cyan
try {
    git init -b main
    Write-Host "Repositorio local inicializado."

    # Usamos 'Set-Content' que es robusto
    Set-Content -Path .\.gitignore -Value @"
# Entornos virtuales y dependencias
/venv/
/node_modules/

# Archivos de credenciales y secretos
.google_credentials
*.json

# Archivos de sistema y logs
.DS_Store
npm-debug.log*

# Archivos de instalador local
instalador*.ps1
"@
    Write-Host ".gitignore creado."

    git add .gitignore
    git commit -m "CI: Inicializa repositorio y .gitignore"
    Write-Host "Commit inicial de .gitignore realizado."
} catch {
    Write-Host "[ERROR] Falla al inicializar Git." -ForegroundColor Red
    Write-Host "Mensaje: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir..."
    exit
}
Write-Host ""

# --- PASO 2: CONFIGURAR BACKEND (PYTHON) ---
Write-Host "--- 2. Configurando Backend (Python / venv / pip) ---" -ForegroundColor Cyan
try {
    New-Item -ItemType Directory -Path "backend"
    Set-Location "backend"
    Write-Host "Creando entorno virtual (venv)..."
    python -m venv venv

    Write-Host "Creando 'requirements.txt'..."
    Set-Content -Path "requirements.txt" -Value "fastapi`nuvicorn[standard]"

    Write-Host "Activando entorno e instalando dependencias (pip install)..."
    # Ejecutamos pip directamente, es más robusto en scripts
    .\venv\Scripts\pip.exe install -r requirements.txt
    
    Write-Host "Backend configurado."
    Set-Location $ProjectRoot
} catch {
    Write-Host "[ERROR] Falla al configurar el Backend." -ForegroundColor Red
    Write-Host "Mensaje: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir..."
    exit
}
Write-Host ""

# --- PASO 3: CONFIGURAR FRONTEND (NODE.JS) ---
Write-Host "--- 3. Configurando Frontend (Node.js / npm) ---" -ForegroundColor Cyan
try {
    New-Item -ItemType Directory -Path "frontend"
    Set-Location "frontend"
    Write-Host "Creando 'package.json' (temporal)..."
    Set-Content -Path "package.json" -Value @"
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite"
  }
}
"@
    Write-Host "Instalando dependencias (npm install)..."
    npm install
    
    Write-Host "Frontend configurado."
    Set-Location $ProjectRoot
} catch {
    Write-Host "[ERROR] Falla al configurar el Frontend." -ForegroundColor Red
    Write-Host "Mensaje: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir..."
    exit
}
Write-Host ""

# --- PASO 4: GESTION DE CREDENCIALES (GOOGLE) ---
Write-Host "--- 4. Configurando Credenciales de Google (Service Account) ---" -ForegroundColor Cyan
$GoogleCredPath = Read-Host "--> Ingresa la RUTA COMPLETA a tu 'service-account.json' (ej: C:\dev\keys\mi-llave.json)"
Set-Content -Path ".google_credentials" -Value $GoogleCredPath
Write-Host "Ruta de credenciales guardada en .google_credentials (ignorado por Git)."
Write-Host ""

# --- PASO 5: CREAR SCRIPTS HOMOLOGOS (Metodo robusto 'Here-String') ---
Write-Host "--- 5. Creando scripts auxiliares en la carpeta 'scripts\' ---" -ForegroundColor Cyan
New-Item -ItemType Directory -Path "scripts"

# Creamos 'activar_backend.bat'
# @" ... "@ es la 'here-string' que evita todos los errores de parsing de cmd
Set-Content -Path "scripts\activar_backend.bat" -Value @"
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
"@
Write-Host "scripts\activar_backend.bat... Creado."

# Creamos 'activar_frontend.bat'
Set-Content -Path "scripts\activar_frontend.bat" -Value @"
@echo off
ECHO ===============================================
ECHO  ACTIVANDO ENTORNO DE FRONTEND (VUE.JS)
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%%~dp0\.."

ECHO Ubicado en la raiz del proyecto.
Entrando a la carpeta del frontend...
cd frontend

ECHO Iniciando servidor de desarrollo de Vite...
npm run dev

pause
"@
Write-Host "scripts\activar_frontend.bat... Creado."

# Creamos 'actualizar_nube_git.bat'
Set-Content -Path "scripts\actualizar_nube_git.bat" -Value @"
@echo off
ECHO ===============================================
ECHO  GUARDANDO Y ENVIANDO CAMBIOS AL REPOSITORIO
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%%~dp0\.."

ECHO 1. Preparando todos los archivos (git add .)
git add .
echo.

set /p commit_message="--> Ingresa el mensaje para el commit y presiona Enter: "
echo.
ECHO 2. Guardando cambios locales (git commit)
git commit -m "%%commit_message%%"
echo.

ECHO 3. Enviando cambios a la nube (git push)
git push
echo.
echo.
ECHO *** SINCRONIZACION FINALIZADA ***
echo.
pause
"@
Write-Host "scripts\actualizar_nube_git.bat... Creado."

# Creamos 'actualizar_pc_desde_nube.bat'
Set-Content -Path "scripts\actualizar_pc_desde_nube.bat" -Value @"
@echo off
ECHO ===============================================
ECHO  ACTUALIZANDO PC DESDE EL REPOSITORIO (NUBE)
ECHO ===============================================

REM Navega al directorio raíz del proyecto
cd /d "%%~dp0\.."

ECHO Trayendo cambios desde la nube (git pull)
git pull
echo.
echo.
ECHO *** ACTUALIZACION FINALIZADA ***
echo.
pause
"@
Write-Host "scripts\actualizar_pc_desde_nube.bat... Creado."
Write-Host "Todos los scripts auxiliares han sido creados."
Write-Host ""

# --- PASO 6: SINCRONIZACION INICIAL CON GITHUB ---
Write-Host "--- 6. Sincronizando la estructura inicial con GitHub ---" -ForegroundColor Cyan
try {
    Write-Host "Preparando el commit inicial (venv y node_modules estan ignorados)..."
    git add .
    git commit -m "CI: Agrega estructura de carpetas y scripts de activacion"

    $RepoURL = Read-Host "--> Pega la URL del repo V5 (la que copiaste del nuevo repo vacio)"
    git remote add origin $RepoURL
    
    Write-Host "¡Empujando (push) la estructura inicial a GitHub!"
    git push -u origin main
    
    Write-Host "¡Sincronizacion inicial exitosa!"
} catch {
    Write-Host "[ERROR] Falla al 'empujar' (push) a GitHub." -ForegroundColor Red
    Write-Host "Mensaje: $_" -ForegroundColor Red
    Read-Host "Presiona Enter para salir..."
    exit
}
Write-Host ""

# --- FINALIZACION ---
Write-Host "===============================================" -ForegroundColor Green
Write-Host "  ¡INSTALACION COMPLETA!" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Green
Write-Host "El entorno en '$ProjectRoot' esta listo y conectado a GitHub."
Write-Host ""
Write-Host "Para trabajar:"
Write-Host "1. Entra a la carpeta 'scripts'"
Write-Host "2. Ejecuta 'activar_backend.bat' para iniciar el servidor."
Write-Host "3. Ejecuta 'activar_frontend.bat' para iniciar la web."
Write-Host "4. Usa 'actualizar_nube_git.bat' para guardar cambios."
Write-Host ""
Read-Host "Presiona Enter para finalizar..."