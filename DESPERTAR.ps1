param(
    [string]$Pull      = "",   # S/N para Git Pull (vacio = preguntar)
    [string]$Restaurar = "",   # S/N para restaurar DB (vacio = preguntar)
    [string]$Mode      = ""    # L=AlfaLite, C=Canario (vacio = preguntar)
)

# Extracción dinámica de Sesión desde CAJA_NEGRA.md
$cajaNegraPath = "$PSScriptRoot\_GY\_MD\CAJA_NEGRA.md"
$SESION_NUM = "000" # Fallback
if (Test-Path $cajaNegraPath) {
    $firstLines = Get-Content $cajaNegraPath -TotalCount 10
    foreach ($line in $firstLines) {
        if ($line -match "Sesión actual:\s*(\d+)") {
            $SESION_NUM = $matches[1]
            break
        }
    }
}
$LOCACION = switch ($env:COMPUTERNAME) {
    "MEDIO"   { "OF" }
    default   { "DESCONOCIDO" }
}
$FECHA = Get-Date -Format "yyyy-MM-dd"

$ErrorActionPreference = "SilentlyContinue"
[console]::Title = "DESPERTAR - Aduana Inteligente (Protocolo Nike)"
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "       SONIDO LIQUIDO V5 - ADUANA DE IMPORTACION" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " [SESION] $SESION_NUM $LOCACION $FECHA" -ForegroundColor Magenta
Write-Host ""

# --- CHEQUEO DE SALUD ANTIGRAVITY (PREVENSION DE BLOQUEO) ---
if (Test-Path "$PSScriptRoot\scripts\check_health.ps1") {
    & powershell.exe -ExecutionPolicy Bypass -File "$PSScriptRoot\scripts\check_health.ps1"
}
# -----------------------------------------------------------

# 0. FETCH PREVENTIVO (MIRADA SATELITAL)
Write-Host "[*] Contactando a la Torre de Control (Git Fetch)..." -ForegroundColor DarkGray
git fetch origin HEAD > $null 2>&1

$remotePasaporte = $null
try {
    # Detectar rama actual dinamicamente
    $branch = git branch --show-current
    if (-not $branch) { $branch = "main" }

    $remotePasaporteStr = git show "origin/$branch":.pasaporte_v5.json 2>$null
    if ($remotePasaporteStr) { $remotePasaporte = $remotePasaporteStr | ConvertFrom-Json }
} catch {}

if ($remotePasaporte) {
    Write-Host "========================================================" -ForegroundColor Cyan
    Write-Host "[PKG] PASAPORTE REMOTO DETECTADO" -ForegroundColor Yellow
    $rOrigen = $remotePasaporte.origen
    $rFecha  = $remotePasaporte.fecha_cierre_real
    $rEstado = $remotePasaporte.estado_salud

    $color = "Green"
    if ($rEstado -match "CRITICO") { $color = "Red" }

    Write-Host " - Origen del vuelo    : $rOrigen"
    Write-Host " - Sello de Tiempo (P) : $rFecha"
    Write-Host " - Estado de Salud     : $rEstado" -ForegroundColor $color
    Write-Host "========================================================" -ForegroundColor Cyan
}

Write-Host ""

# 1. GIT PULL Y CONTROL DE CONFLICTOS
if ($Pull -ne "") {
    $gitPrompt = $Pull
    Write-Host "[AUTO] Git Pull: $Pull" -ForegroundColor DarkGray
} else {
    $gitPrompt = Read-Host "Desea bajar cambios de la otra oficina (Git Pull)? (S/N)"
}
if ($gitPrompt -match "^[sS]") {

    # Paracaidas automatico antes de tocar nada si es critico
    if ($remotePasaporte -and $remotePasaporte.estado_salud -match "CRITICO") {
        Write-Host "[!] ALERTA: La carga es CRITICA. Se recomienda rama salvavidas." -ForegroundColor Red
        $doBranch = Read-Host "Crear rama de seguridad local ahora? (S/N)"
        if ($doBranch -match "^[sS]") {
            $bName = "salvavidas-$(Get-Date -Format 'yyyyMMdd-HHmm')"
            git branch $bName
            Write-Host "[OK] Rama $bName creada." -ForegroundColor Green
        }
    }

    Write-Host "[*] Ejecutando Pull..." -ForegroundColor Yellow
    git pull origin HEAD

    # Chequeo de Conflictos Binarios (Protocolo Nike)
    $conflicts = git ls-files -u
    if ($conflicts) {
        Write-Host ""
        Write-Host "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" -ForegroundColor Red
        Write-Host "!!! ERROR CRITICO: CONFLICTO BINARIO DETECTADO       !!!" -ForegroundColor Red
        Write-Host "!!! La base de datos o el polizon estan en conflicto !!!" -ForegroundColor Red
        Write-Host "!!! Intervencion humana manual requerida en Git.     !!!" -ForegroundColor Red
        Write-Host "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" -ForegroundColor Red
        Read-Host "Presione Enter para ABORTAR"
        exit
    }
}

# 2. ADUANA DE POLIZON (TRASPLANTE)
if (-not (Test-Path "POLIZON_MAESTRO.bak")) {
    Write-Host ""
    Write-Host "[!] No hay POLIZON_MAESTRO.bak disponible." -ForegroundColor Yellow
    Write-Host "    (No estas conectado, Git no disponible, o cerraste en este mismo puesto.)" -ForegroundColor DarkGray
    Write-Host "    Continuando sin sincronizacion de base de datos." -ForegroundColor DarkGray
} else {
    Write-Host ""
    Write-Host "[*] Analizando carga del Polizon..." -ForegroundColor Cyan

    # Identificar base local
    $localDb = ""
    if (Test-Path "V5_LS_MASTER.db") { $localDb = "V5_LS_MASTER.db" }
    elseif (Test-Path "pilot_v5x.db") { $localDb = "pilot_v5x.db" }

    if ($localDb -ne "" -and $remotePasaporte) {
        # Obtener fechas (ParseExact puede lanzar excepcion terminante si el formato no coincide)
        $pFechaObj = $null
        try {
            $pFechaObj = [datetime]::ParseExact($remotePasaporte.fecha_cierre_real, "yyyy-MM-dd HH:mm:ss", $null)
        } catch {
            Write-Host " [!] No se pudo leer la fecha del Polizon: $($_.Exception.Message)" -ForegroundColor DarkGray
        }
        $lFechaObj = (Get-Item $localDb).LastWriteTime

        Write-Host " - Polizon (Remoto): $($remotePasaporte.fecha_cierre_real)"
        Write-Host " - Base Local      : $($lFechaObj.ToString('yyyy-MM-dd HH:mm:ss'))"

        if ($pFechaObj -and $pFechaObj -gt $lFechaObj) {
            Write-Host " >>> RECOMENDACION: EL POLIZON ES MAS RECIENTE. RESTAURAR." -ForegroundColor Green
        } else {
            Write-Host " >>> ADVERTENCIA: EL POLIZON ES MAS VIEJO QUE TU BASE LOCAL." -ForegroundColor Red
            Write-Host " >>> Restaurar podria causar perdida de datos (Enchastre)." -ForegroundColor Red
        }

        Write-Host ""
        if ($Restaurar -ne "") {
            Write-Host "[AUTO] Restaurar DB: $Restaurar" -ForegroundColor DarkGray
        } else {
            $Restaurar = Read-Host "Deseas RESTAURAR la base local desde el Polizon? (S/N)"
        }
        if ($Restaurar -match "^[sS]") {
            Write-Host "[*] Asegurando base local antigua (respaldo_pre_trasplante.db.bak)..." -ForegroundColor Yellow
            Copy-Item $localDb "$localDb.pre_trasplante.bak" -Force

            Write-Host "[*] Ejecutando Trasplante Fisico..." -ForegroundColor Green
            Copy-Item "POLIZON_MAESTRO.bak" $localDb -Force
            Write-Host "[OK] Base de datos sincronizada." -ForegroundColor Green
        } else {
            Write-Host "[!] Polizon ignorado. Se mantiene la base local actual." -ForegroundColor Yellow
        }
    }
}

Write-Host ""
# 3. SEMAFORO ALFA (LITE / CANARIO)
$statusL = "LIMPIO"
$output = & python scripts\manager_status.py read
foreach ($line in $output) {
    if ($line -match "^STATUS_STR:(.*)") { $statusL = $matches[1].Trim() }
}

Write-Host "========================================================" -ForegroundColor Cyan
if ($statusL -match "CRITICO") {
    Write-Host " [ALERTA] Estado actual: $statusL" -ForegroundColor Red
} else {
    Write-Host " [OK] Estado actual: $statusL" -ForegroundColor Green
}
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "[L] ALFA-LITE | [C] CANARIO | [X] SALIR"
if ($Mode -ne "") {
    $opc = $Mode
    Write-Host "[AUTO] Modo: $Mode" -ForegroundColor DarkGray
} else {
    $opc = Read-Host "Seleccione"
}

if ($opc -match "^[lL]") {
    Set-Clipboard -Value "Gy, arrancamos bajo ALFA-LITE (Via rapida). El entorno esta despejado. Sesion $SESION_NUM. Tarea: "
    Write-Host "Instruccion ALFA-LITE copiada (sesion $SESION_NUM)." -ForegroundColor Green
} elseif ($opc -match "^[cC]") {
    Set-Clipboard -Value "Gy, inicia ALFA COMPLETO (sesion $SESION_NUM). Ejecuta el Canario y valida integridad."
    Write-Host "Instruccion CANARIO copiada (sesion $SESION_NUM)." -ForegroundColor Green
}

Read-Host "Enter para cerrar"