# Reporte de Auditoría: Sistema IVA_V1 (Bug Multi-Alícuota)
**Fecha**: 2026-04-09 (Turno Noche)
**Estado del Sistema**: Funcional con Riesgo de Cálculo
**Ubicación**: `C:\dev\IVA_V1`

## ⚠️ Hallazgo Crítico: Fallo en Saldo Técnico
Durante la auditoría del satélite **IVA_V1**, se detectó un error estructural en el cálculo de impuestos que afecta la toma de decisiones fiscales.

### El Problema
Los módulos de reporte y el generador de saldos (`src/reports.py`) **solo están sumando el IVA al 21%**. El sistema ignora completamente el crédito y débito fiscal proveniente de otras alícuotas que ya están en la base de datos:
- IVA 10.5% (Alimentos/Maquinaria)
- IVA 27% (Servicios/Energía)
- IVA 5% / 2.5%

### Impacto
Si el usuario genera un reporte de un período con alícuotas mixtas, el **Saldo Técnico (IVA a Pagar/Favor)** será incorrecto, subestimando tanto el crédito como el débito fiscal.

## 🛠️ Acción Requerida (Pendiente para Mañana - OF)
Se debe realizar un refactor en `src/reports.py` (líneas 214 en adelante) para implementar una suma omni-direccional de las columnas:
- `importe_iva` (21%)
- `iva_105`
- `iva_27`
- `iva_5`
- `iva_25`

Asimismo, el `bridge.py` debe ser actualizado para exportar estos desgloses hacia el sistema central V5.

---
**Firmado**: Gy (Antigravity) | **Estado**: Auditado / Pendiente de Fix
