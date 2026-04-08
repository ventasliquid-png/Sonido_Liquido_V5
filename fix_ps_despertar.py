content_ps1 = """$ErrorActionPreference = "SilentlyContinue"

[console]::Title = "DESPERTAR - Control de Transito ALFA"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       SONIDO LIQUIDO V5 - MOTOR DE ARRANQUE" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. GIT SYNC
$gitPrompt = Read-Host "¿Desea ejecutar GIT PULL para sincronizar rama (S/N)?"
if ($gitPrompt -match "^[sS]") {
    Write-Host "[*] Sincronizando con el Vault (Github)..." -ForegroundColor Yellow
    try {
        git pull
        # Run python script
        python scripts\\manager_status.py set 4
    } catch {
        Write-Host "[ERROR] Falló el Git Pull. Verifique conexión o conflictos." -ForegroundColor Red
        Read-Host "Presione Enter para continuar"
    }
} else {
    Write-Host "[!] Saltando sincronización manual." -ForegroundColor DarkGray
}

Write-Host ""

# 2. Consultar estado del Genoma
$bitCritico = $false
$desincro = $false
$statusL = "DESCONOCIDO"

$output = & python scripts\\manager_status.py read
foreach ($line in $output) {
    if ($line -match "^STATUS_STR:(.*)") {
        $statusL = $matches[1].Trim()
    }
    if ($line -match "^ALERT:DESINCRO_DETECTADA") {
        $desincro = $true
    }
}

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "          REPORTE METEOROLOGICO (BIT 3)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if ($statusL -match "CRÍTICO" -or $statusL -match "CRITICO") {
    $bitCritico = $true
}

if ($bitCritico) {
    Write-Host " [ALERTA ROJA] Hay líos en el gallinero (Bit 3: CRÍTICO activado)" -ForegroundColor Red
    Write-Host " Estado actual: $statusL" -ForegroundColor Red
} else {
    Write-Host " [OK] Última sesión terminó con cielo despejado (GOLD)." -ForegroundColor Green
    Write-Host " Estado actual: $statusL" -ForegroundColor Green
}

if ($desincro) {
    Write-Host " [ATENCION] Posible desincronización de origen." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "SELECCION DE PROTOCOLO:" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "[L] ALFA-LITE : Vía rápida (Ajustes UI, Fixes locales). Sin burocracia."
Write-Host "[C] CANARIO   : Auditoría profunda (Cambios estructurales o resolucion)."
Write-Host "[X] SALIR     : No copiar nada."
Write-Host ""

$opcion = Read-Host "Seleccione opción [L / C / X]"

if ($opcion -match "^[lL]") {
    Write-Host "[*] Preparando directiva ALFA-LITE..." -ForegroundColor Yellow
    Set-Clipboard -Value "Gy, arrancamos bajo ALFA-LITE (Vía rápida). El entorno está despejado. Tarea a resolver: "
    Write-Host "Instrucción LITE copiada al portapapeles." -ForegroundColor Green
} elseif ($opcion -match "^[cC]") {
    Write-Host "[*] Preparando directiva CANARIO..." -ForegroundColor Yellow
    Set-Clipboard -Value "Gy, inicia ALFA COMPLETO. Ejecutá el Canario V2.0, revisá integridad general y aguardá mi instrucción."
    Write-Host "Instrucción CANARIO copiada al portapapeles." -ForegroundColor Green
} else {
    Write-Host "[!] Operación abortada." -ForegroundColor DarkGray
    exit
}

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "Operación completada. Pegue el comando en la interfaz de Gy." -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Read-Host "Presione Enter para cerrar"
"""

content_bat = """@echo off
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0DESPERTAR.ps1"
"""

with open('DESPERTAR.ps1', 'w', encoding='utf-8-sig') as f:
    f.write(content_ps1)

with open('DESPERTAR.bat', 'w', encoding='utf-8') as f:
    f.write(content_bat)
