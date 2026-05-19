# Informe Sesión 811 — HONNEY + DEOU F4 + CF CUIT Fallback
**Fecha:** 2026-05-19 | **Locación:** OF | **Agente:** Claude Code Sonnet 4.6

## Resumen
Sesión de corrección de tres bugs en el subsistema de clientes: borrado de fósiles pre-genoma,
alta rápida DEOU F4, y fallback de CUIT para Consumidor Final.

## Hito 1 — HONNEY fix (flags=0 hard delete)
**Problema:** `hard_delete_cliente()` bloqueaba registros con `flags_estado=0` (fósiles pre-genoma)
porque `not (0 & IS_VIRGIN) = True` — interpretaba el flags neutro como "tocado/bloqueado".

**Fix backend:** Guard extendido con condición `current_flags != 0`.
**Fix frontend:** HardDeleteManager.vue — amber styling, "CLIENTE IMPOSIBLE", botón habilitado.
**Commits:** D `1e5d4327` / P `85a48b8`

## Hito 2 — DEOU F4 (alta rápida cliente)
**Problema:** Cliente creado via F4 nacía con tres defectos:
- Inactivo: nibble=0 → `activo=bool(0)=False`
- CUIT vacío string en DB: payload enviaba `cuit: ''`
- Sin inferencia Rosa: `_audit_sovereignty` ausente en `create_cliente`

**Fix:**
- `ClientCanvas.saveCliente()`: `currentFlags |= 3` cuando nibble=0 y sin CUIT real.
- `PedidoCanvas.altaClienteContext()` + F4 handler: `cuit: null`.
- `create_cliente()`: orden `_apply_cf_cuit_fallback → _audit_sovereignty → activo sync → Roseti → commit`.

**Commits:** D `0286f0df` / P `0b31fe2`

## Hito 3 — CF CUIT Fallback backend
**Problema:** Clientes CF sin CUIT llegaban al backend con `cuit=null`.
El backend no lo completaba, dejando el campo vacío.

**Fix:** Nuevo método `_apply_cf_cuit_fallback()` — detecta condicion_iva CONSUMIDOR FINAL
via `condicion_iva.nombre`, asigna `'00000000000'` si cuit es null. Se llama antes de
`_audit_sovereignty` para que el audit vea el CUIT correcto y active `GOLD_ARCA`.

**Commits:** D `208d6a46` / P `937d5be`

## Deuda técnica registrada
- **INBOX.md:** unificación detección Rosa — 3 estrategias divergentes en frontend
  (Bit4 / nibble [9,11] / Bit19 = 524288). Solución pendiente: `useClienteColor.js`.

## Estado final
- Canario D: NOMINAL GOLD (flags=13)
- WAL checkpoint: OK
- D: main @ 208d6a46
- P: main @ 937d5be — pendiente push
