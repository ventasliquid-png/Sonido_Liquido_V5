# Hardening Ingesta — 3 Fixes Quirúrgicos (Sesión 818 sub-CA)

**Fecha:** 2026-05-28
**Locación:** CA
**Agente:** Claude Code (Haiku 4.5)
**Hash de cierre:** 2938c77a
**Estado:** NOMINAL GOLD — PIN 1974

## Contexto

Dos auditorías independientes (CC Opus 4.8 + Gy High) sobre el módulo de ingesta
identificaron hallazgos. Antes de fixear, cada uno fue **validado contra el código real**.

## FIX 1 — URLs con prefijo `/api` inexistente

**Hallazgo (Gy):** Los iframes y links en `IngestaFacturaView.vue` usaban
`/api/ingesta/...` y `/api/remitos/...`, pero el backend monta los routers sin
prefijo `/api` y Vite no tiene proxy para `/api` → 404 en todos los iframes del
panel de duplicados.

**Validación:**
- `IngestaFacturaView.vue`: 3 ocurrencias (líneas 393, 407, 451).
- `vite.config.js`: proxea `/ingesta` y `/remitos`, NO `/api`.
- `main.py:420`: `app.include_router(ingesta_router)` sin prefijo.
- El resto del `.vue` ya usaba rutas sin `/api` (ej. línea 745).

**Fix aplicado:**
- Línea 393: `/api/ingesta/raw/.../pdf` → `/ingesta/raw/.../pdf`
- Línea 407: `/api/ingesta/raw/.../pdf` → `/ingesta/raw/.../pdf`
- Línea 451: `/api/remitos/.../pdf` → `/remitos/.../pdf`

## FIX 2 — `PedidoFlags.STATE_MASK` → AttributeError

**Hallazgo (CC):** `router.py:231` usaba `PedidoFlags.STATE_MASK`, pero `STATE_MASK`
está definido a nivel módulo en `constants.py`, no como miembro de la clase
`PedidoFlags` → `AttributeError` → 500 al anular un pedido con `ORIGEN_FACTURA`.

**Validación:**
- `constants.py:37`: `STATE_MASK` definido a nivel módulo (fuera de la clase).
- `router.py:226`: el import solo traía `PedidoFlags`.

**Fix aplicado:**
- Línea 226: `from backend.pedidos.constants import PedidoFlags, STATE_MASK`
- Línea 231: `~PedidoFlags.STATE_MASK` → `~STATE_MASK`

## FIX 3 — `flags_estado &= ~2048` sin guard

**Hallazgo (ambos):** En `anular_y_reingestar`, línea 243, `raw_nuevo.flags_estado &= ~2048`
lanza `TypeError` si `flags_estado` es None. La línea 218 sí tenía el guard `or 0`.

**Validación:** confirmado en `router.py` — asimetría entre línea 218 (con guard) y 243 (sin guard).

**Fix aplicado:**
- Línea 243: `raw_nuevo.flags_estado = (raw_nuevo.flags_estado or 0) & ~2048`

## Anexo — Corrección documental OMEGA.md FASE 1

El snippet inline de salud del OMEGA exigía `flags_estado = 13` exacto, desactualizado
respecto a la migración a máscara de bits de `canario_v2.py`. LAVIMAR tiene
`flags_estado = 1099511627789` (bits acumulados), y `1099511627789 & 13 == 13`.
Snippet migrado a `(flags_estado & 13) == 13`.

## Verificación

- Canario `canario_v2.py`: **NOMINAL GOLD** (`(flags & 13) == 13`, 0.008s).
- Commit: `2938c77a` — push a `origin/main` verificado (órbita OK, hashes coinciden).
- Diff: 2 archivos, 6 inserciones / 6 borrados.

## Deuda detectada

- `audit_v5.py` (FASE 4 del OMEGA) ausente del árbol — recuperar o re-apuntar el protocolo.
