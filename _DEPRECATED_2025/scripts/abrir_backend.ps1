# --- abrir_backend.ps1 (V11.1 - Corrección Modular) ---
# Ejecución: .\scripts\abrir_backend.ps1

# --- 0. ESTABLECER RUTAS ROBUSTAS ---
$ScriptDir = Split-Path -Parent $PSCommandPath
$RootDir = Join-Path -Path $ScriptDir -ChildPath ".."
$BackendDir = Join-Path -Path $RootDir -ChildPath "backend"
$VenvActivate = Join-Path -Path $BackendDir -ChildPath "venv\Scripts\activate"
$GAC_PATH = Join-Path -Path $RootDir -ChildPath ".google_credentials"


Write-Host "=============================================" -ForegroundColor Green
Write-Host "  ACTIVANDO ENTORNO DE BACKEND (V11.1 Modular)" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# 1. SOLICITAR LA CONTRASEÑA DE FORMA SEGURA
$USER = "postgres"
$IP = "34.95.172.190"
$DB_NAME = "postgres"
$PORT = "5432"

$Password = Read-Host -Prompt "Ingrese la contraseña de Cloud SQL" -AsSecureString
$PasswordClear = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($Password))

# 2. CONSTRUIR Y ESTABLECER VARIABLES
$DB_URL = "postgresql://${USER}:$($PasswordClear)@${IP}:${PORT}/${DB_NAME}"
$env:DATABASE_URL = $DB_URL
$env:GOOGLE_APPLICATION_CREDENTIALS = $GAC_PATH

Write-Host "Conectando al servidor: $IP" -ForegroundColor Cyan
Write-Host "Variables de entorno establecidas. Iniciando Uvicorn..." -ForegroundColor Green

# 3. ACTIVAR VENV y EJECUTAR UVICORN
if (Test-Path $VenvActivate) {
    # Activamos el entorno
    & $VenvActivate
    
    # --- [INICIO PARCHE V10.11] ---
    # Nos posicionamos en la RAÍZ del proyecto (NO en backend/)
    Push-Location $RootDir 
    # Lanzamos Uvicorn usando la ruta de paquete (dot notation)
    uvicorn backend.main:app --reload
    # --- [FIN PARCHE V10.11] ---
    Pop-Location
} else {
    Write-Host "❌ ERROR: No se encontró el entorno virtual VENV." -ForegroundColor Red
}

pause