# Informe de Sesión 796: Parser Y-Axis Fix + D↔P Sync (CA)

**Fecha:** 2026-05-05
**Locación:** CA
**Entorno:** D + P (Tom) + canario_v2.py
**Estado:** NOMINAL — OMEGA ejecutado
**Commits:** 7b5794d (Tom null-checks), 534178b (PedidoCanvas sync), 8c658f63 (bitácora OF addendum)
**Archivo:** INFORMES_HISTORICOS/2026-05-05_INGESTA_PARSER_FIX_MODAL_SYNC_CA.md

---

## 1. Objetivo

Resolver causa raíz de `items[]` vacío en flujo PDF → modal PedidoCanvas tras diagnóstico incompleto de sesión OF.  
Caso real: Factura L EPI S.R.L. — Alcohol 70% bidón x 5 Lts — cantidad: 4,00 — precio unit: $13.500,00.

---

## 2. Intervenciones

### Hito 1: Fix Y-Axis Tolerance — pdf_parser.py (CRÍTICO)
- **Archivo:** `backend/remitos/pdf_parser.py`, línea 137
- **Causa:** Tolerancia `/4` (±2pts) insuficiente para PDFs AFIP donde `qty` y `u_medida` difieren hasta 5pts verticalmente.
  - qty y0 = 285.8 → `/4` → y_key **284**
  - u_medida y0 = 286.2 → `/4` → y_key **288**
  - Condición `has_data_anchor AND cantidad is not None` fallaba: cada campo en fila distinta.
- **Fix:** `round(y0 / 4) * 4` → `round(y0 / 6) * 6`
  - Ambas coordenadas → y_key **288** ✅ Items agrupados correctamente.
- **Validación:** Extracción real de coordenadas PDF con fitz; caso L EPI confirmado.
- **Alcance:** D + P (Tom)

### Hito 2: Fix Typo Producto — pilot_v5x.db
- **Tabla:** `productos` | ID 150 | SKU 10211
- **Antes:** "Acohol 70 % bidon x 5 Lts" → sin match en búsqueda modal
- **Después:** "Alcohol 70 % bidon x 5 Lts" → match OK
- `UPDATE productos SET nombre = 'Alcohol 70 % bidon x 5 Lts' WHERE id = 150`

### Hito 3: Verificación Bug #3 — Field Alignment (descartado)
- Hipótesis inicial: desalineación `precio_unitario` vs `precio_unitario_neto`
- Parser línea 193: `"precio_unitario": row_data["precio"] or 0.0` ✅
- PedidoCanvas línea 1570: `precio: Number(item.precio_unitario) || 0` ✅
- Pull de mañana ya traía alineación. Bug #3 = FALSE POSITIVE.

### Hito 4: Null-checks remitos/router.py — Tom (commit 7b5794d)
- Endpoint `/ingresar-factura` sin validación de items vacíos → 500 silencioso.
- Null-checks agregados: respuesta controlada cuando `parsed_data['items']` vacío.

### Hito 5: PedidoCanvas.vue D→P sync verificado (commit 534178b)
- Alineación de campo confirmada. Sin cambios requeridos en este tramo.

### Hito 6: Bitácora OF addendum (commit 8c658f63)
- Entrada sesión 795 OF agregada con diagnóstico en curso y bugs A/B/C relevados.

### Hito 7: Canario v2.py — Actualización TARGET_FLAGS (D + Tom)
- **Causa:** Canario tenía `TARGET_FLAGS = 8205` (pre-saneamiento 2026-05-02).
- DB tiene `flags = 13` (post-saneamiento, bit 8192 eliminado) → canario reportaba DESVÍO CRÍTICO.
- **Fix:** `TARGET_FLAGS = 8205` → `TARGET_FLAGS = 13` en D y Tom.
- Resultado: INTEGRITY NOMINAL GOLD ✅ en ambos entornos.

---

## 3. Métricas

| Indicador | Valor |
|-----------|-------|
| Bugs identificados (sesión completa OF+CA) | 3 |
| Bugs CRÍTICOS resueltos | 1 (Y-axis /4→/6) |
| Bugs MENORES resueltos | 1 (typo DB) |
| Bugs FALSE POSITIVE | 1 (field alignment) |
| Canario fix adicional | 1 (TARGET_FLAGS 8205→13) |
| Entornos sincronizados | D + Tom |
| Commits de sesión | 3 (7b5794d, 534178b, 8c658f63) |
| Caso real validado | L EPI — Alcohol 70% — qty=4,00 precio=$13.500,00 |

---

## 4. Bugs Backlog (pendientes para próxima sesión)

| ID | Descripción | Prioridad |
|----|-------------|-----------|
| Bug A | Campo búsqueda en modal pisa referencia PDF original al tipear | Media |
| Bug B | ESC en modal 409 no restaura estado anterior — limbo visual | Media |
| Bug C | Flujo pedido→factura→remito incompleto: vínculo no cierra ciclo logístico | Alta |
| Clientes azules | Multi-entidad CUIT compartido: modal muestra cliente incorrecto | Alta |
| Build P (OF) | `npm run build` + volcar `dist/` → `static/` pendiente mañana OF | Bloqueante |

---

**Estado:** NOMINAL GOLD — OMEGA 796 ejecutado. PIN 1974 autorizado por Carlos.
