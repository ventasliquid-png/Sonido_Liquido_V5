# Script de Reparación de Acceso Remoto (Firewall + Usuario) - Simplificado

Write-Host "--- 1. CONFIGURANDO FIREWALL (Puerto 8000) ---" -ForegroundColor Cyan
# Intentar abrir puerto. Si falla (por falta de permisos), avisar.
# Primero borramos regla anterior si existe para asegurar limpieza (opcional, pero mejor crear nueva si no existe)
# New-NetFirewallRule es idempotente casi, pero vamos a intentar crearlo directametne.
New-NetFirewallRule -DisplayName "HAWE V5 Backend" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue

if ($?) {
    Write-Host "✅ Intento de configuracion de Firewall realizado." -ForegroundColor Green
} else {
    Write-Host "⚠️ No se pudo configurar Firewall automaticamente (Requiere Admin)." -ForegroundColor Yellow
    Write-Host "   Si falla la conexion, abre el puerto 8000 manualmente." -ForegroundColor Gray
}

# 2. Crear Usuario Operador
Write-Host "`n--- 2. CREANDO USUARIO 'operador' ---" -ForegroundColor Cyan
python scripts/create_operator_user.py

# 3. Mostrar Datos de Conexion
$ip = (Test-Connection -ComputerName (hostname) -Count 1).IPV4Address.IPAddressToString
Write-Host "`n--- DATOS DE ACCESO PARA LA OTRA PC ---" -ForegroundColor Green
Write-Host "URL:      http://$ip:5173" -ForegroundColor Yellow
Write-Host "Usuario:  operador" -ForegroundColor Yellow
Write-Host "Clave:    operador123" -ForegroundColor Yellow

Read-Host "`nPresiona Enter para finalizar..."
