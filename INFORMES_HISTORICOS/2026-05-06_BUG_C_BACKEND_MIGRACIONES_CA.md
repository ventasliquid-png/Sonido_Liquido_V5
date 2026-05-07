# Informe de Sesión 797-CA: Bug C Backend + Sistema de Migraciones

**Fecha:** 2026-05-06
**Locación:** CA
**Entorno:** D
**Estado:** NOMINAL GOLD (ítem 13 PedidoCanvas diferido)
**Arquitecto:** Sonnet
**Ejecutor:** Claude Code (Sonnet 4.6)
**Hash:** 529aa2be
**Archivo:** INFORMES_HISTORICOS/2026-05-06_BUG_C_BACKEND_MIGRACIONES_CA.md

---

## 1. Objetivo

Resolver Bug C — flujo pedido→factura→remito incompleto. El backend tenía 7 bugs identificados
(B-1 a B-7) que dejaban el endpoint de puente completamente inoperativo y violaban la doctrina
de numeración 0016-XXXX-YYYYYYYY. Adicionalmente se implementó el modelo N:M `FacturaRemito`
y el sistema de control de versiones de migraciones.

---

## 2. Intervenciones

### Hito 1: Auditoría forense (Sonnet)
Lectura completa de `facturacion/models.py`, `facturacion/service.py`, `remitos/router.py`,
`remitos/service.py`, `PedidoCanvas.vue` y `pedidos.js`. Identificación de 7 bugs críticos y
diseño del plan de corrección completo incluyendo la decisión arquitectural N:M.

### Hito 2: Migración 026 — tabla `facturas_remitos` (Ítem 1)
- `DROP TABLE IF EXISTS facturas_remitos` (eliminó la versión con PK compuesta sin id propio)
- `CREATE TABLE facturas_remitos` con `id CHAR(32) PRIMARY KEY`, `fecha_vinculo`, `flags_estado BIGINT`
- Índices por `factura_id` y `remito_id`
- Script: `scripts/migrate_026_factura_remitos.py`

### Hito 3: Modelo ORM `FacturaRemito` (Ítem 2-4)
- `backend/facturacion/models.py`: `Table` simple → clase `FacturaRemito` completa con GUID,
  `fecha_vinculo`, `flags_estado`, relaciones bidireccionales con strings (anti-deadlock CLAUDE.md)
- `Factura.remitos` → `Factura.vinculos_remitos` (cascade `all, delete-orphan`)
- `backend/remitos/models.py`: `Remito.vinculos_facturas` agregado (string ref)

### Hito 4: Fix B-1 — `factura_id: int` → `str` (Ítems 4-5)
- `backend/remitos/router.py:261`: parámetro `int` → `str`
- `backend/remitos/service.py:586`: firma + cast `_uuid.UUID(factura_id)` en query
- **Impacto:** el endpoint era completamente inoperativo — FastAPI rechazaba el UUID antes de llegar al service

### Hito 5: Fix B-2 — `fecha_vto_cae` → `cae_vencimiento` (Ítem 6)
- `backend/remitos/service.py:606,634`: campo inexistente `fecha_vto_cae` → campo real `cae_vencimiento`
- **Impacto:** crash `AttributeError` en runtime en ambas ramas del método

### Hito 6: Fix B-3 — `numero_legal` con número ARCA real (Ítem 7)
- `backend/remitos/service.py:610,635`: helper `_numero_legal_arca(factura, fallback_id)`
- Con CAE: `f"0016-{punto_venta.zfill(4)}-{numero_comprobante.zfill(8)}"` (doctrina punto 4)
- Sin CAE (borrador): `f"0015-{str(fallback_id).zfill(8)}"` (serie manual, doctrina Nike)
- **Impacto:** antes usaba `pedido.id` o UUID del remito — violación directa de doctrina

### Hito 7: Fix B-7 — `total_bruto` → `factura.total` (Ítem 8)
- `backend/remitos/service.py:637`: campo inexistente `total_bruto` → `factura.total`
- **Impacto:** `valor_declarado` siempre era 0.0 silenciosamente

### Hito 8: Integración N:M en `create_puente_factura` (Ítem 9)
- Inserción de `FacturaRemito` en ambas ramas (remito existente + nuevo)
- Guard de idempotencia: verifica existencia antes de insertar
- Helper `_vincular_factura_remito(db, factura, remito)` extraído para claridad

### Hito 9: Fix B-6 — `cuit_comprador` en borrador (Ítem 10)
- `backend/facturacion/service.py`: asignación `factura.cuit_comprador = pedido.cliente.cuit`
  después del `db.flush()` en `create_draft_from_pedido`
- **Impacto:** sello histórico faltante — el campo existía en el modelo pero nunca se populaba

### Hito 10: Comentario arquitectural N:M (Ítem 11)
- `backend/facturacion/service.py`: nota inline explicando que el vínculo en `facturas_remitos`
  se crea en `RemitosService.create_puente_factura()`, no en el borrador

### Hito 11: Bug B también resuelto en esta sesión (pre-797)
- `frontend/src/stores/pedidos.js`: `pending409Context` + `set409Context`/`clear409Context`
- `IngestaFacturaView.vue`: `goToNewPedido()` persiste contexto; `onMounted()` lo restaura
- Hash: `9df14bdf`

### Hito 12: Sistema de control de migraciones (post-797)
- `scripts/migrate_000_control_migraciones.py`: crea tabla `_migraciones_aplicadas` con
  `id VARCHAR PRIMARY KEY`, `nro_sesion INTEGER`, `aplicada_en DATETIME`
- Patrón idempotente documentado al tope del script 000 para guiar futuros scripts
- `migrate_026_factura_remitos.py` refactorizado: verifica `_migraciones_aplicadas` antes
  de ejecutar → SKIP si ya aplicada
- Hash: `529aa2be`

---

## 3. Métricas

| Indicador | Valor |
|-----------|-------|
| Bugs backend resueltos | 6 (B-1 a B-3, B-6, B-7 + endpoint inoperativo) |
| Bugs frontend resueltos | 1 (Bug B — modal 409) |
| Archivos modificados | 6 backend + 3 frontend + 2 scripts |
| Tabla nueva | `facturas_remitos` (id, fecha_vinculo, flags_estado) |
| Tabla nueva | `_migraciones_aplicadas` (sistema de control) |
| Modelo ORM nuevo | `FacturaRemito` (N:M soberano) |
| Commits de sesión | 3 (9df14bdf, 0cf51130, 529aa2be) |
| Canario D post-sesión | NOMINAL GOLD — flags=13 ✅ |

---

## 4. Pendientes

| ID | Descripción | Prioridad |
|----|-------------|-----------|
| Bug C ítem 13 | D-7: `savePedido()` en PedidoCanvas no invoca cadena factura→remito post-save | ALTA |
| Bug C (completo) | resuelto=0 en DB hasta que ítem 13 esté ejecutado | — |
| Build P | Frontend de Producción sin compilar | MEDIA |
| Clientes azules | Multi-entidad CUIT compartido | MEDIA |
| Vínculos invisibles | Ficha cliente | MEDIA |

**Sello de cierre:** PIN 1974 — Sesión 797-CA — 2026-05-06 — NOMINAL GOLD
