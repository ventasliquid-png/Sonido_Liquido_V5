# INFORME TÉCNICO V5.9 — SESIÓN 2026-04-18
**Asunto**: Indicadores de Huérfandad + Alta de Rubro en Caliente (F4) + Protocolo de Adopción.  
**Estado**: **NOMINAL GOLD**.  
**Protocolo**: Omega Closure (PIN 1974).  
**Agente**: Claude Code (Sonnet 4.6)  
**Entorno**: OF  

---

## 1. RESUMEN EJECUTIVO

Sesión de tres bloques consecutivos. Punto de partida: los productos cuyo rubro fue dado de baja (Bit 3 = EXPATRIADO) no tenían ningún indicador visual en el frontend. El operador no podía distinguirlos ni reasignarlos eficientemente. Se implementó el sistema completo de gestión de huérfanos: indicadores visuales, filtro dedicado, alta de rubro en caliente desde el inspector, y protocolo de adopción con confirmación especial para el rubro General.

---

## 2. HITOS ALCANZADOS

### A. INDICADORES DE HUÉRFANDAD (Bit 3)

- **Dot neon en tarjetas**: Punto verde (`#24e70f`) con glow y `outline: 2.5px solid #0a0f1a` para que pop contra fondos claros. Posición absoluta top-left, `animate-pulse`.
- **Dot en listado por renglones**: Mismo indicador sobre el ícono del producto en la vista lista.
- **Borde en inspector**: Cuando el producto abierto es huérfano, el inspector reemplaza `hud-border-red` por borde verde neon con box-shadow difuso.
- **Filtro "Huérfanos"**: Botón adicional en el grupo Todos/Activos/Inactivos. Filtra client-side por `flags_estado & 8`.

**Fix crítico previo**: `flags_estado` no estaba expuesto en el schema `ProductoRead`. El frontend recibía `undefined` y `undefined & 8 = 0` → nunca mostraba dot. Fix: agregar `flags_estado: int = 0` a `ProductoRead` en `schemas.py`.

**Fix DB**: SKU 80016 tenía `flags_estado=0` a pesar de ser un producto expatriado real. Corregido vía SQL directo (PIN 1974) en ambas DBs.

---

### B. ALTA DE RUBRO EN CALIENTE (F4)

Flujo completo: el operador está en el selector de Rubro del inspector, escribe un nombre que no existe, presiona **F4** (o hace clic en "Crear...") → se abre un modal ámbar `z-[200]` con campos:
- **Nombre** (obligatorio)
- **Código** (auto-generado por backend, editable opcionalmente, máx 3 chars)
- **Margen Propuesto** (%)

Campo **Padre eliminado** por política V2 — los rubros se crean siempre en el nivel raíz.

**Backend**: `_auto_codigo()` en `service.py` genera código de 3 chars ASCII del nombre, con sufijo numérico en colisión. `codigo` en `RubroCreate` pasó de `str` requerido a `Optional[str] = None`.

**Teclado**: F4 en `SelectorCreatable` emite `create` siempre (con o sin resultados). El botón "Crear..." con hint `(F4)` siempre visible al fondo cuando hay texto.

---

### C. PROTOCOLO DE ADOPCIÓN V5.9

**Adopción silenciosa**: Cuando el operador cambia el rubro de un huérfano a cualquier rubro que no sea General → el backend limpia el Bit 3 automáticamente en `update_producto` (`flags_estado & ~8`). Sin confirmación, sin fricción.

**Adopción en General** (confirmación especial): Si el huérfano va a quedar en General, el sistema intercepta antes de guardar y muestra un modal amarillo `z-[210]`:
> "¿Confirmar que queda en General y se lo da por adoptado?"

Con opción de cancelar y elegir otro rubro. Al confirmar → `_executeSave` con el payload original.

---

### D. CORRECCIÓN DEL CICLO REACTIVO (bug en alta de rubro)

**Problema**: Al crear el rubro en el modal y hacer `fetchRubros()`, el watch `deep: true` sobre `props.producto` (que apunta a `currentProducto` del store) disparaba `full-sync` con `ID change: true`, borrando el formulario del inspector. Causa real identificada: F10 sin guard disparaba `save()` del producto mientras el modal estaba abierto → `updateProducto` → `currentProducto.value = response.data` → watch con objeto diferente → full-sync.

**Solución aplicada (patrón Clientes)**:
1. `saveRubroFromModal` ya no llama `fetchRubros()`. Hace `productosStore.rubros.push(newRubro)` directamente → el selector lo ve sin reemplazo reactivo.
2. Asignación directa: `localProducto.value.rubro_id = newRubro.id` → no toca `currentProducto`.
3. `handleKeydown` rutea F10: si `showRubroModal` está abierto → llama `saveRubroFromModal`; si no → `save()` del producto.
4. Los watches usan `if (showRubroModal.value) return` como guard.
5. `showRubroModal` declarado **antes** de los watches (fix de Temporal Dead Zone — JS no permite acceder a `const` antes de su declaración).

---

### E. FIX handleSave (doble llamada)

`ProductosView.handleSave` llamaba nuevamente a `updateProducto` cuando el inspector ya lo había llamado. Simplificado: `handleSave` solo actualiza el item en la lista local con el resultado recibido del inspector.

---

## 3. ARCHIVOS MODIFICADOS

| Archivo | Entorno | Cambio |
|---|---|---|
| `backend/productos/schemas.py` | D y P | `flags_estado: int = 0` en `ProductoRead`; `codigo: Optional[str]` en `RubroBase`; validador en `RubroCreate` |
| `backend/productos/service.py` | D y P | `_auto_codigo()`, adopción limpia Bit 3 en `update_producto`, Papelera en `hard_delete_producto` |
| `frontend/.../ProductoInspector.vue` | D y P | Modal Alta Rubro, Adopción General, guard watches, F10 routing, borde huérfano |
| `frontend/.../ProductosView.vue` | D y P | Filtro Huérfanos, dot en listado, fix `handleSave` |
| `frontend/.../ProductoCard.vue` | D y P | Dot huérfano con outline |
| `frontend/src/components/common/SelectorCreatable.vue` | D y P | F4 + "Crear..." siempre visible |

---

## 4. MÉTRICAS

| Métrica | Valor |
|---|---|
| Bugs críticos resueltos | 5 (flags_estado invisible, ciclo reactivo, F10 routing, TDZ, doble save) |
| Iteraciones de debug del ciclo reactivo | 4 (flag _rubroCreating × 2, freeze/restore, solución final push directo) |
| Archivos backend modificados | 2 |
| Archivos frontend modificados | 4 |
| Builds ejecutados en P | 6 (uno por cada iteración de fix) |
| Entornos sincronizados | D y P — paridad confirmada byte a byte |
| SKUs corregidos manualmente en DB | 1 (SKU 80016, PIN 1974) |
| Rubros de prueba creados en pilot_v5x.db | 1 ("Papeles", id=30, PAP) |

---

## 5. DEUDAS TÉCNICAS ACTIVAS

| ID | Descripción | Prioridad |
|---|---|---|
| DT-HUERFANOS-01 | Script de consolidación de duplicados: unificar SKUs duplicados, asignar bit VIRGINITY, borrado físico | ALTA — próxima sesión |
| DT-HUERFANOS-02 | Reasignar los ~9 productos huérfanos restantes a sus rubros definitivos (lo hace el operador desde UI) | MEDIA |
| DT-01 | BIT_ORIGEN_FACTURA / BIT_ORIGEN_REMITO en pedidos | ALTA |

---

## 6. ESTADO DE CIERRE

- **Sistema D**: NOMINAL GOLD. Vite dev server activo.
- **Sistema P**: NOMINAL GOLD. Frontend buildeado (`ProductoInspector-DtwBVYZC.js`) y deployado a `static/`. Backend con `schemas.py` y `service.py` sincronizados.
- **DB D** (`pilot_v5x.db`): contiene rubro "Papeles" (id=30) de pruebas de la sesión.
- **DB P** (`V5_LS_MASTER.db`): intacta, sin los rubros de prueba.
- **Paridad D↔P**: confirmada (`diff` byte a byte en todos los archivos modificados).

---

*Claude Code (Sonnet 4.6) — Protocolo Omega — 2026-04-18*
