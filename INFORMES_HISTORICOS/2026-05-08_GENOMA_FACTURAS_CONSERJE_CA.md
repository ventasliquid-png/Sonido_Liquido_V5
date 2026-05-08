# Informe de Sesión 799-CA: Genoma Facturas + Conserje Duplicados

**Fecha:** 2026-05-08
**Locación:** CA
**Agente:** Claude Code Sonnet 4.6
**Estado de cierre:** NOMINAL GOLD
**Hash técnico:** 93a9a3d4

---

## Resumen Ejecutivo

Sesión CA enfocada en tres ejes: (1) implementación del Genoma de facturas — `FacturaFlags` como clase de constantes con mapa completo de bits 0-21 sellado por Nike Arq 5.5; (2) extensión del modelo `Factura` con campo `notas_auditoria`; (3) conserje de facturas duplicadas en el endpoint de ingesta de PDF — detección temprana por `punto_venta + numero_comprobante` con respuesta HTTP 409 `FACTURA_DUPLICADA`. También en esta sesión: Bug G (pedidos duplicados con advertencia modal, hash `58404b1b`).

---

## Hito 1: `FacturaFlags` — Genoma de flags_estado (Hash: 93a9a3d4)

**Archivo nuevo:** `backend/facturacion/constants.py`

Clase de constantes que define el mapa completo de bits del campo `flags_estado` en la tabla `facturas`. Sellado Nike Arq 5.5.

| Bit | Valor | Nombre | Semántica |
|-----|-------|--------|-----------|
| 0 | 1 | `EXISTENCE` | El registro existe |
| 1 | 2 | `HAS_ACTIVITY` | 1=virgen (nunca tocado), 0=tocado |
| 2 | 4 | `HAS_REMITO` | Tiene al menos un remito vinculado |
| 3 | 8 | `ACTIVE` | No anulada |
| 10 | 1024 | `V15_STRUCT` | Reservado global (estructura V15) |
| 15 | 32768 | `PASADO_A_PEDIDO` | Factura ya usada para generar pedido |
| 16 | 65536 | `EN_CUARENTENA` | Bajo revisión manual |
| 17 | 131072 | `TIENE_NC` | Tiene nota de crédito asociada |
| 18 | 262144 | `TIENE_ND` | Tiene nota de débito asociada |
| 19 | 524288 | `ES_NC` | Este comprobante ES una nota de crédito |
| 20 | 1048576 | `ES_ND` | Este comprobante ES una nota de débito |
| 21 | 2097152 | `AUDITADA` | Revisada y certificada por operador |
| 22-29 | — | Reservado | Módulo Contabilidad (retenciones) |
| 30+ | — | Ultra-reservado | Futuras extensiones |

**Estado inicial de factura nueva:** `EXISTENCE | HAS_ACTIVITY | ACTIVE` = `1 | 2 | 8` = **11**

---

## Hito 2: Campo `notas_auditoria` en modelo Factura

**Archivo modificado:** `backend/facturacion/models.py`

```python
notas_auditoria = Column(String, nullable=True)
```

Campo de texto libre destinado a registrar observaciones del operador durante la auditoría manual. Complementa el bit `AUDITADA` (bit 21): el bit señala que fue revisada, el campo preserva el detalle de qué se observó.

---

## Hito 3: Migración 029 — `facturas.notas_auditoria`

**Archivo nuevo:** `scripts/migrate_029_facturas_notas_auditoria.py`

```sql
ALTER TABLE facturas ADD COLUMN notas_auditoria VARCHAR;
```

Migración idempotente siguiendo el patrón `_migraciones_aplicadas` (sesión 797). ID de registro: `"029_facturas_notas_auditoria"`. Ejecutada y confirmada en `pilot_v5x.db`.

---

## Hito 4: Conserje `FACTURA_DUPLICADA` en ingesta-pdf

**Archivo modificado:** `backend/remitos/router.py` — endpoint `POST /remitos/ingesta-pdf`

**Lógica insertada antes de procesar el PDF:**

1. Extrae `punto_venta` y `numero_comprobante` del payload parseado.
2. Consulta `facturas` WHERE `punto_venta = X AND numero_comprobante = Y`.
3. Si existe registro: retorna **HTTP 409** con body:
   ```json
   {
     "codigo": "FACTURA_DUPLICADA",
     "mensaje": "La factura ya existe en el sistema.",
     "factura_id": "<uuid>"
   }
   ```
4. Si no existe: flujo continúa normalmente.

**Impacto:** El frontend (IngestaFacturaView) puede distinguir el 409 `FACTURA_DUPLICADA` de otros errores y mostrar al operador el mensaje específico con opción de navegación al registro existente.

---

## Hito 5: Bug G — Pedidos duplicados con advertencia modal (Hash: 58404b1b)

Implementación de guardia en el flujo de creación de pedidos: cuando el sistema detecta un posible duplicado (mismo cliente, misma fecha, ítems similares), muestra un modal de advertencia con opción de continuar o cancelar en lugar de bloquear silenciosamente.

---

## Métricas

| Indicador | Valor |
|-----------|-------|
| Archivos nuevos | 2 (`constants.py`, `migrate_029_...py`) |
| Archivos modificados | 2 (`models.py`, `router.py`) |
| Bits de Genoma documentados | 22 (bits 0-21) |
| Migración ejecutada en pilot_v5x.db | 029 |
| Canario D post-sesión | NOMINAL GOLD — flags=13 |

---

## Hashes Git

| Hash | Descripción |
|------|-------------|
| `93a9a3d4` | feat(facturas): FacturaFlags + notas_auditoria + conserje duplicados + migración 029 |
| `58404b1b` | fix(bug-G): pedidos duplicados con advertencia modal |

---

**Sello de cierre:** PIN 1974 — Sesión 799-CA — 2026-05-08 — NOMINAL GOLD
