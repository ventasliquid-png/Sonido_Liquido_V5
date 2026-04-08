content_cierre_ps1 = """$ErrorActionPreference = "SilentlyContinue"
[console]::Title = "OMEGA - Cierre de Sesion y Aduana"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       AEROPUERTO V5 - SELLADO DE PASAPORTE OMEGA" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[*] Escaneando biometria de la maquina..." -ForegroundColor DarkGray

$machine = $env:COMPUTERNAME
$date = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host ""
Write-Host "¿Cual es el estado del sistema V5 al cerrar la jornada?" -ForegroundColor Yellow
Write-Host "[G] GOLD    (Cielo despejado, Nominal, Funciona)"
Write-Host "[C] CRITICO (Alertas, bugs pendientes, a medias)"
Write-Host ""
$statusInput = Read-Host "Elija G o C"

if ($statusInput -match "^[gG]") {
    $status = "GOLD"
} else {
    $status = "CRITICO"
}

# Crear json manualmente para evitar BOM o encodings raros de PS
$jsonString = '{\n  "origen": "' + $machine + '",\n  "fecha": "' + $date + '",\n  "estado": "' + $status + '"\n}'

$path = ".pasaporte_v5.json"
Set-Content -Path $path -Value $jsonString -Encoding UTF8

Write-Host "--------------------------------------------------------"
Write-Host "Pasaporte sellado: $status desde $machine" -ForegroundColor Green
Write-Host "--------------------------------------------------------"

$msg = Read-Host "Mensaje breve para la Bitacora Git (Ej: Fix UI Canvas)"
if ([string]::IsNullOrWhiteSpace($msg)) { $msg = "Omega: Cierre automatico" }
$fullMsg = "Omega: $msg [$status]"

Write-Host "[*] Subiendo contenedor al Vault satelital (GitHub)..." -ForegroundColor Yellow

git add .
git commit -m $fullMsg
git push origin HEAD

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "Carga enviada al Vault remoto exitosamente." -ForegroundColor Green
    Write-Host "========================================================" -ForegroundColor Cyan
} else {
    Write-Host "[ERROR] Hubo un problema empujando el camión al servidor." -ForegroundColor Red
}

Read-Host "Presione Enter para salir"
"""

content_cierre_bat = """@echo off
powershell.exe -ExecutionPolicy Bypass -NoProfile -File "%~dp0CIERRE.ps1"
"""

content_despertar_ps1 = """$ErrorActionPreference = "SilentlyContinue"

[console]::Title = "DESPERTAR - Control de Transito ALFA"

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       SONIDO LIQUIDO V5 - MOTOR DE ARRANQUE" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 0. ADUANA SATELITAL (FETCH)
Write-Host "[*] Contactando a la Torre de Control (Aduana)..." -ForegroundColor DarkGray
# Hacemos fetch silencioso para actualizar referencias locales
git fetch origin HEAD > $null 2>&1

$remotePasaporte = $null
try {
    # Leer el archivo remotamente si existe
    $remotePasaporteStr = git show origin/HEAD:.pasaporte_v5.json 2>$null
    if ($remotePasaporteStr) {
        $remotePasaporte = $remotePasaporteStr | ConvertFrom-Json
    }
} catch {
    # Ignorar
}

Write-Host "========================================================" -ForegroundColor Cyan
if ($remotePasaporte) {
    Write-Host "📦 CARGA ENTRANTE DETECTADA (PASAPORTE OMEGA)" -ForegroundColor Yellow
    $rOrigen = $remotePasaporte.origen
    $rFecha = $remotePasaporte.fecha
    $rEstado = $remotePasaporte.estado

    $color = "Green"
    if ($rEstado -match "CRITICO") { $color = "Red" }
    
    Write-Host " - Viene desde         : $rOrigen"
    Write-Host " - Fecha de sellado    : $rFecha"
    Write-Host " - Salud del paquete   : $rEstado" -ForegroundColor $color
} else {
    Write-Host "📦 No se detectó pasaporte satelital remoto." -ForegroundColor DarkGray
}
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. GIT SYNC
$gitPrompt = Read-Host "¿Desea VOLCAR esta carga remota sobre su entorno local (Git Pull)? (S/N)"
if ($gitPrompt -match "^[sS]") {
    # Paracaidas condicional
    if ($remotePasaporte -and $remotePasaporte.estado -match "CRITICO") {
        Write-Host ""
        Write-Host "[!] ADVERTENCIA: La carga entrante viene marcada como CRÍTICO." -ForegroundColor Red
        $parachute = Read-Host "¿Deseas crear una rama SECRETA para asegurar tu estado local actual antes de descargar? (S/N)"
        if ($parachute -match "^[sS]") {
            $stamp = Get-Date -Format "yyyyMMdd-HHmm"
            $branch = "salvavidas-$($env:COMPUTERNAME)-$stamp"
            Write-Host "[*] Creando ancla salvavidas: $branch ..." -ForegroundColor Yellow
            git branch $branch
            Write-Host "[OK] Codigo local protegido en tiempo y espacio." -ForegroundColor Green
        }
    }

    Write-Host "[*] Volcando carga (Sincronizando)..." -ForegroundColor Yellow
    try {
        git pull origin HEAD
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
Write-Host "          REPORTE METEOROLOGICO LOCAL (BIT 3)" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if ($statusL -match "CRÍTICO" -or $statusL -match "CRITICO") {
    $bitCritico = $true
}

if ($bitCritico) {
    Write-Host " [ALERTA ROJA] Hay líos en el gallinero (Bit 3: CRÍTICO activado localmente)" -ForegroundColor Red
    Write-Host " Estado actual: $statusL" -ForegroundColor Red
} else {
    Write-Host " [OK] Última sesión terminó con cielo despejado (GOLD)." -ForegroundColor Green
    Write-Host " Estado actual: $statusL" -ForegroundColor Green
}

if ($desincro) {
    Write-Host " [ATENCION] Posible desincronización de origen (Local vs Drive)." -ForegroundColor Yellow
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

with open('CIERRE.ps1', 'w', encoding='utf-8-sig') as f:
    f.write(content_cierre_ps1)

with open('CIERRE.bat', 'w', encoding='utf-8') as f:
    f.write(content_cierre_bat)

with open('DESPERTAR.ps1', 'w', encoding='utf-8-sig') as f:
    f.write(content_despertar_ps1)
