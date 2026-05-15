# INFORME HISTÓRICO — Sesión 808
**Fecha:** 2026-05-15
**Entorno:** OF — D (C:\dev\Sonido_Liquido_V5)
**Agente:** Claude Code (Sonnet 4.6)
**Tema:** Doctrina de Virginidad + Atomicidad Ingesta + Fix UX + Sync D↔P

---

## 1. Contexto

Sesión de continuación de 807. Trabajo en D, cherry-pick a P al cierre. El canario reportó NOMINAL GOLD al inicio (FLAGS: 13).

---

## 2. FIX UX — PedidoCanvas

**Problema:** El botón "Guardar e Imprimir" aparecía en el flujo manual (sin ingestaData). El canvas siempre redirigía a PedidoList post-guardado, incluso en flujo manual donde el operador quiere continuar cargando pedidos.

**Solución:**
- `v-if="pedidosStore.ingestaData"` en el botón — desaparece en flujo manual.
- Variable `wasIngesta` capturada antes de `clearIngestaData()` — evita bug de evaluación tardía.
- Post-guardado manual: reset de campos del canvas + notificación "listo para siguiente operación".
- Post-guardado ingesta: redirección a PedidoList (comportamiento anterior).

---

## 3. FIX Rosa — OPERATOR_OK bypass AFIP

**Problema:** Al guardar un pedido para cliente Rosa (Bit 4 activo, sin CUIT), el sistema igualmente llamaba a la API de creación de borrador de factura y remito puente.

**Solución:** Flag `esOperatorOk` evaluado antes del bloque fiscal. Si activo, salta todo el circuito AFIP y muestra warning al operador.

---

## 4. Doctrina de Virginidad — Implementación canónica

**Contexto:** Bit 1 (HAS_ACTIVITY) representa "cliente sin operación real". Debe apagarse una sola vez, irreversiblemente, cuando ocurre la primera operación real.

**Auditoría previa:** Se identificaron 2 triggers incorrectos activos (promoción 4 pilares, Vanguard Canon) y 2 triggers canónicos faltantes (CUMPLIDO, CAE).

**Cambios:**
| Archivo | Cambio |
|---|---|
| `clientes/service.py` | Removida línea `~HAS_ACTIVITY` de bloque 4 pilares |
| `remitos/service.py` | Vanguard Canon preserva Bit 1 (solo setea base) |
| `remitos/service.py` | Ghost pedido nace PENDIENTE (era CUMPLIDO) |
| `pedidos/router.py` | Hook en PATCH: CUMPLIDO → apagar Bit 1 |
| `facturacion/service.py` | Hook en sellar: CAE → apagar Bit 1 |

**Commit D:** `8e703914`

---

## 5. Diagnóstico 409 ingesta — Raw stuck en RECIBIDO

**Problema:** Raw `80af6b8b` (Labme, factura 0001-00002535) devolvía 409 al intentar aprobar. El frontend no podía proceder.

**Diagnóstico:**
- El raw tenía `audit_status='RECIBIDO'` y `processed_at=None`
- Pero existían: Pedido #39 (CUMPLIDO), Remito `0016-00002535` (con CAE real), Factura espejo (AUTORIZADA_AFIP)
- Guard 1 de `create_from_ingestion` detectaba el remito existente → 409
- Causa raíz: commit parcial anterior — `create_from_ingestion` comiteó el downstream, pero el segundo commit de `IngestaService.approve()` nunca se ejecutó

**Fix inmediato:** Reconciliación manual del raw → `audit_status='PROCESADO'`, `processed_at` seteado (PIN 1974).

---

## 6. Atomicidad IngestaService.approve()

**Auditoría completa del flujo:** dos commits no atómicos con ventana de inconsistencia entre ellos.

**Solución implementada:**
- `create_from_ingestion()`: `db.commit()` → `db.flush()` (flush-only)
- `IngestaService.approve()`: único commit al final del flujo exitoso
- Checkpoint `PROCESANDO` visible antes del vuelo
- Estado `ERROR` en fallo (antes el raw quedaba silenciosamente en RECIBIDO)
- Endpoint deprecated `POST /ingesta-process` recibió `db.commit()` explícito

**Commit D:** `513796bf`

---

## 7. Sync D↔P

Cherry-picks aplicados a P en orden:
1. `0b34f1f9` → `add3fbf` (OK limpio)
2. `bb723cf6` → `a08dd2d` (conflicto burocracia `_GY/_MD/` → destagiado)
3. `8e703914` → `3690673` (conflicto `clientes/service.py` → resuelto versión D)
4. `513796bf` → `5865616` (OK limpio)

P push: `d3173b2..5865616`

---

## 8. Estado final

- D: `513796bf` 🟢
- P: `5865616` 🟢
- MT: 🟡 necesita `git pull`
- Canario: NOMINAL GOLD FLAGS: 13
- Deuda técnica activa: 3 ítems UX PedidoCanvas (DT-01, DT-02, DT-03)
