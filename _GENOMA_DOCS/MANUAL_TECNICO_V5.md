# MANUAL TECNICO V5: "INDEPENDENCIA"
**Version:** 2.8 Release (S837 CA — ES_NO_COMERCIAL Bit 11 implementado + race condition fix + 3 fixes UI)
**Fecha:** 2026-06-28

### 📢 Actualización Sesión 837 CA (2026-06-27/28) — ES_NO_COMERCIAL implementado + race condition

**Commit:** `cdf70d4e` · B:`5794a62` (cherry-pick S838)

**Implementación ES_NO_COMERCIAL (Bit 11):**
- `toggle_no_comercial` endpoint en `backend/pedidos/router.py`: guard precio $0 (HTTP 400 con detalle del producto), enciende Bit11+Bit33 en ON, reinicia Bit23 + nota forense inmutable en OFF
- `backend/remitos/service.py`: Bit 23 (FULL_INVOICED) se enciende automáticamente cuando pedido ES_NO_COMERCIAL alcanza FULL_DELIVERED (Bit 21). Una muestra completamente despachada = ciclo fiscal cerrado automáticamente.
- `backend/pedidos/schemas.py`: `NoComercialRequest` con campo `usuario` para la nota forense
- ES_FIRME (Bit 33) ortogonal a ES_NO_COMERCIAL: un pedido no-comercial activo DEBE tener Bit 33 para aparecer en el selector de remito manual

**Race condition (flush-antes-de-toggle):**
- Bug: watcher `isNoComercial` llamaba `/no-comercial` antes de persistir precios editados → DB veía $0 aunque UI mostraba precio nuevo
- Fix: flush explícito (`PATCH /pedidos/{id}` con `buildPayload()`) antes del toggle cuando `val=false`
- Catch block muestra `detail` del backend en lugar de mensaje genérico

**ManualRemitoView — Preselección por query params:**
- `onMounted` lee `?cliente_id=X&pedido_id=Y` y precarga el formulario de remito manual automáticamente
- Navegación desde inspector: botón "Remito" en Total Footer → `router.push({ name: 'ManualRemito', query: {...} })`

**Tres fixes UI (segunda iteración — primera falló por corte de sesión):**
- **Notas en PedidoCanvas:** `fixed left-6` quedaba detrás del sidebar `w-64` → panel INLINE en footer (`flex flex-col gap-3`), sin overlay ni posicionamiento absoluto
- **Cámara/texto en header inspector:** `ml-2 gap-1` insuficiente → `flex-1 min-w-0` en texto + `shrink-0` en botones
- **Botón Remito:** en zona scrolleable, invisible al abrir → movido al Total Footer del inspector (junto a CLONAR, siempre visible)

**Migrate_036 en CA:**
- `flags_estado INTEGER DEFAULT 0` en tabla `remitos` — aplicada en CA (faltaba desde S836 que solo la aplicó en OF)

### 📢 Actualización Sesión 836 OF (2026-06-26) — Arquitectura genoma sin cambios de código funcional

**Sin cambios en APIs ni comportamiento observable.** Esta sesión fue de canonización doctrinal pura.

**Nuevos bits en PedidoFlags (`backend/pedidos/constants.py`):**
- `HAS_PARTIAL_INVOICE = 1 << 22` — Facturas parciales en curso. Se enciende cuando hay al menos una factura R16 que no cubre el 100% del pedido.
- `FULL_INVOICED = 1 << 23` — Facturación completa (COMMERCIALLY_CLEARED). Rosa: confirmado por operador. Blanco: confirmado por Sabueso ARCA.
- `ES_NO_COMERCIAL = 1 << 11` — Bypass comercial: muestras, uso interno. Parte de la Banda de Excepciones (Bits 11/12). Reversible con nota forense obligatoria.

**Doctrina canonizada:**
- Dos ejes ortogonales independientes: **físico** (Bits 20/21 HAS_PARTIAL_DELIVERY/FULL_DELIVERED) vs **fiscal** (Bits 22/23 HAS_PARTIAL_INVOICE/FULL_INVOICED).
- Pedidos soberano: no existe remito sin pedido padre. La exploración de Ghost/nullable fue descartada por Nike.
- Banda de Excepciones Bits 11/12: `ES_NO_COMERCIAL` opera junto a `NO_FISCAL_FORCE` como circuito de bypass.

**Nuevos bits en RemitoFlags (`backend/remitos/constants.py`):**
- `flags_estado INTEGER DEFAULT 0` agregado a tabla `remitos` vía migrate_036.
- Genoma canonizado: EXISTENCE(0), HAS_ACTIVITY(1), ES_LIBRE(4 — reservado), V15_STRUCT(10), VINCULAR_PARCIAL(11), PROHIBIDO(13).

## 38. REGLA DE ALCANCE LOCAL EN PYTHON: import DENTRO DE FUNCIÓN (Sesion 835 OF, 2026-06-25)

### 38.1 El problema (UnboundLocalError)

Si se hace `from x import y` en *cualquier punto* dentro del cuerpo de una función, Python convierte `y` en variable local para **toda** la función — incluso para las líneas anteriores al import. Resultado: `UnboundLocalError: local variable 'y' referenced before assignment` en la primera referencia a `y`, aunque exista un import global del mismo nombre en la cabecera del módulo.

### 38.2 El patrón en service.py (S835)

```python
# BUGGY: import local convierte domicilios_clientes en local en toda la función
def update_domicilio(...):
    domicilios_clientes.update(...)  # ← UnboundLocalError aquí
    ...
    from backend.clientes import domicilios_clientes  # ← causa del bug
```

### 38.3 La solución

Eliminar todo import dentro del cuerpo de la función. Los imports globales al módulo son suficientes. Nunca duplicar imports dentro de funciones como workaround de circularidad — resolver la circularidad en los módulos correctamente.

### 38.4 Regla de diagnóstico

Ante cualquier `UnboundLocalError` en Python, buscar `import` o `=` del mismo nombre **en cualquier lugar de la función**, sin importar cuán tarde aparezcan.

---

## 38B. TALONARIO DOS CAPAS: service + engine (Sesion 835 OF, 2026-06-25)

El número de serie de un remito puede ser sobreescrito en dos puntos independientes:
1. **service.py `create_manual()`**: genera el `numero_legal` con la serie correcta (0015).
2. **remito_engine.py `generar_remito_pdf()`**: podía forzar un prefijo diferente al imprimir en PDF.

Si solo se corrige la capa 1, la DB tiene `0015-` pero el PDF imprime `0016-`. Siempre verificar ambas capas ante bugs de talonario.

**Fix S835**: remito_engine.py ahora preserva el prefijo del `numero_remito` entrante. Detecta `0015`, `0016`, `0001` del input y lo mantiene.

---

## 37. PATRON DICT BYPASS PARA @property EN ENDPOINT CON JOIN (Sesion 832 OF, 2026-06-22)

### 37.1 El problema

`Persona.nombre_completo` es un `@property` Python — no es columna SQLAlchemy. Al hacer un join Vinculo+Persona y retornar objetos ORM, Pydantic con `from_attributes=True` intenta `getattr(vinculo_orm, 'nombre_completo')` pero el atributo pertenece a `persona_orm`, no a `vinculo_orm`.

### 37.2 El patron canonico

```python
# En el endpoint, retornar list[dict] en lugar de list[ORM]:
return [
    {
        "id": v.id,
        "persona_id": v.persona_id,
        "nombre_completo": p.nombre_completo,  # @property evaluado explicitamente
        "rol": v.rol,
        "roles": v.roles or [],
        "flags_estado": v.flags_estado,
        "activo": v.activo,
    }
    for v, p in query.all()
]
```

Pydantic valida los dicts sin intentar introspeccion ORM. El `@property` se evalua sobre el objeto correcto.

### 37.3 Cuando aplicar

Usar este patron en cualquier endpoint que serialice propiedades calculadas de un objeto relacionado en un join multi-tabla.

---

## 36. DOCTRINA STATE_MASK — PATRÓN OBLIGATORIO EN TRANSICIONES DE PEDIDO (Sesión 825 CA, 2026-06-14)

### 36.1 El problema: OR sin máscara

El campo `pedidos.flags_estado` usa bits 32-35 como estados mutuamente excluyentes del ciclo de vida:

| Bit | Valor | Nombre |
|-----|-------|--------|
| 32 | 1<<32 | `ES_PRESUPUESTO` |
| 33 | 1<<33 | `ES_FIRME` |
| 34 | 1<<34 | `ES_CUMPLIDO` |
| 35 | 1<<35 | `ES_ANULADO` |

Un `|=` sin limpiar la máscara primero deja múltiples bits activos simultáneamente:

```python
# INCORRECTO — puede dejar ES_FIRME|ES_ANULADO activos al mismo tiempo
pedido.flags_estado = (pedido.flags_estado or 0) | PF.ES_ANULADO.value
```

Esto hace que el pedido aparezca en filtros de **ambos** estados.

### 36.2 El patrón canónico

Toda transición de estado de ciclo de vida **DEBE** limpiar `STATE_MASK` antes de aplicar el nuevo estado:

```python
# CORRECTO — limpia los 4 bits de ciclo de vida, luego activa el nuevo
pedido.flags_estado = ((pedido.flags_estado or 0) & ~STATE_MASK.value) | PF.ES_NUEVO_ESTADO.value
```

**Importación requerida:**
```python
from backend.pedidos.constants import PedidoFlags as PF, STATE_MASK
```

`STATE_MASK` es una constante a nivel módulo en `constants.py` — **no** es miembro de la clase `PedidoFlags`. Acceder vía `PF.STATE_MASK` lanza `AttributeError`.

### 36.3 Caso de aplicación — Fix Card #51 (router.py:266)

La migración quirúrgica (path cuando Ingesta detecta discrepancia con pedido existente del mismo día) tenía este bug latente. Al momento del fix no había instancias activas en DB (`SELECT COUNT(*) WHERE (flags & ES_FIRME) > 0 AND (flags & ES_ANULADO) > 0` → 0 filas). El fix fue preventivo.

**Archivo:** `backend/pedidos/router.py` línea 266.

### 36.4 Regla de búsqueda para auditoría

Para detectar pedidos con estados simultáneos inválidos:
```sql
SELECT id, flags_estado FROM pedidos
WHERE (flags_estado & (1<<32)) > 0 AND (flags_estado & (1<<33)) > 0  -- ES_PRESUPUESTO|ES_FIRME
   OR (flags_estado & (1<<33)) > 0 AND (flags_estado & (1<<35)) > 0  -- ES_FIRME|ES_ANULADO
   OR (flags_estado & (1<<32)) > 0 AND (flags_estado & (1<<34)) > 0; -- etc.
```

**Resultado esperado:** 0 filas. Si hay resultados, corregir con:
```python
flags_limpio = (flags_actual & ~STATE_MASK.value) | ESTADO_CORRECTO.value
```

## 35. DOCTRINA TELEPORT + v-show — HOTFIX 822.1 OF (2026-06-05)

### 35.1 Bug: Pantalla negra al navegar a PedidoCanvas

**Síntoma:** Al clickear "Nuevo Pedido", pantalla negra sin errores en consola (solo warnings).

**Causa raíz:** `HaweLayout.vue` usaba `v-if` en `GlobalStatsBar`:
```html
<GlobalStatsBar v-if="route.name !== 'PedidoCanvas'" />
```
Cuando Vue Router inicia la navegación a `PedidoCanvas`, `route.name` cambia **inmediatamente** (reactivo), antes de que los componentes se monten/desmonten. Con `mode="out-in"` en la transition, el componente saliente (HaweView, PedidoList) sigue montado durante su animación de salida. Si ese componente tiene un `<Teleport to="#global-header-center">` activo, y el target ya fue destruido por el `v-if`, Vue lanza un warning silencioso y la transición falla → pantalla negra.

### 35.2 Fix aplicado

**Archivo:** `frontend/src/layouts/HaweLayout.vue` — 1 línea

```html
<!-- ANTES (bug) -->
<GlobalStatsBar v-if="route.name !== 'PedidoCanvas' && route.query.mode !== 'satellite'" />

<!-- DESPUÉS (fix) -->
<GlobalStatsBar v-show="route.name !== 'PedidoCanvas' && route.query.mode !== 'satellite'" />
```

**Por qué funciona:** `v-show` aplica `display: none` — el elemento DOM persiste. El Teleport puede encontrar `#global-header-center` aunque esté oculto. La transición de salida completa normalmente. PedidoCanvas renderiza.

### 35.3 Doctrina Teleport (sellado 822.1)

> **REGLA:** Un elemento que sirve como target de `<Teleport>` NUNCA debe estar bajo `v-if`.
> Usar `v-show` para preservar el DOM element durante transiciones de ruta.

| Approach | Efecto en DOM | Seguro para Teleport |
|---|---|---|
| `v-if=false` | Elemento destruido | ❌ NO — target desaparece |
| `v-show=false` | `display:none` | ✅ SÍ — target permanece |

**Afecta a:** cualquier componente que use `<Teleport to="#global-header-center">` → HaweView.vue, PedidoList.vue, y cualquier vista futura que use el portal del GlobalStatsBar.

## 34. EXCEL ESPEJO DE PEDIDOS — SESIÓN 822 OF (2026-06-04)

### 34.1 Script `scripts/exportar_pedidos_excel.py`

Genera `Q:\Mi unidad\V5_Silo_Claude\PEDIDOS_ESPEJO.xlsx` — un bloque por pedido, apilados verticalmente. No requiere FastAPI ni Vue — abre su propia conexión SQLite.

**Estructura de cada bloque:**
```
[Pedido Nº | nro RED | Cliente PURPURA]  [OC si existe]
[Fecha     | CUIT    | valor           ]
[PRODUCTO  | CANTIDAD | PV | SUBTOTAL | | COSTO UNIT | COSTO TOTAL]
 item 1...
[NOTAS | texto mergeado B→H (italic si tiene contenido)]
[      |  | Sub Total | $xxx | | $costo_sub]
[      |  | IVA       | $xxx | | $costo_iva]  ← solo si discrimina IVA
[      |  | TOTAL     | $xxx | | $costo_tot]
(separador)
```

**Colores STATE_MASK (bits 32-35 de `pedidos.flags_estado`):**
| Estado | Bit | bg_header | bg_item_impar |
|---|---|---|---|
| Firme/Pendiente | 33 | `#C4D79B` verde | `#EBF1DD` |
| Cumplido | 34 | `#FFD966` amarillo | `#FFF2CC` |
| Anulado | 35 | `#FF9999` rojo | `#FFD5D5` |
| Presupuesto | 32 | `#C9B1E8` lila | `#EDE0FF` |
| Entregado | 44 | `#D9D9D9` gris | `#F2F2F2` |

**Costos:** solo si el producto está en `productos_costos`. 16/65 ítems cubiertos en pilot_v5x.db.

**Fallback PermissionError:** si `PEDIDOS_ESPEJO.xlsx` está abierto (Drive o Excel), genera `PEDIDOS_ESPEJO_HHMMSS.xlsx` sin fallar.

### 34.2 Lógica IVA — Motor Bipolar en script

Replica exactamente `_aplica_iva()` de `backend/pedidos/router.py`:

```python
NO_FISCAL_FORCE = 4096               # Bit 12 pedido
DISCRIMINA_IVA  = 1 << 40            # Bit 40 cliente
RI_UUID         = '966fdb33d6a64e499c81197790567dcb'

def _calcula_discrimina_iva(pedido_flags, cliente_flags, condicion_iva_id):
    if (pedido_flags or 0) & NO_FISCAL_FORCE:
        return False                 # Circuito Negro soberano
    if ((cliente_flags or 0) & DISCRIMINA_IVA) or (condicion_iva_id == RI_UUID):
        return True                  # Circuito Blanco — RI
    return False                     # CF / Mono / Exento / informal
```

**Nota:** bit 40 no está migrado en todos los clientes RI (solo BULACIO y JOFRE en pilot). Se usa `condicion_iva_id = RI_UUID` como proxy confiable hasta migración completa.

### 34.3 Endpoint `GET /pedidos/exportar-espejo`

**Archivo:** `backend/pedidos/router.py`

```python
@router.get("/exportar-espejo")
def exportar_espejo_excel():
    ...
    result = subprocess.run([sys.executable, script],
                            capture_output=True, text=True,
                            cwd=project_root, timeout=60)
    ...
```

**REGLA CRÍTICA DE ROUTE ORDERING:** Este endpoint DEBE declararse **ANTES** de `@router.get("/{pedido_id}", ...)`. Si va después, FastAPI captura el segmento "exportar-espejo" como un pedido_id de tipo int → 422 Unprocessable Entity. Comentario en código: "IMPORTANTE: debe estar ANTES de /{pedido_id}".

### 34.4 Frontend — Teleport al GlobalStatsBar

**Patrón:** `<Teleport to="#global-header-center">` desde `PedidoList.vue`.

`GlobalStatsBar.vue` ya tiene `<div id="global-header-center" class="flex-1 flex items-center justify-center ..."></div>` — portal previsto exactamente para este uso.

Los botones se montan/desmontan con el componente → visibles SOLO en el Tablero de Pedidos. El mismo patrón ya se usaba en el componente para tooltips y context menu (`<Teleport to="body">`).

```html
<Teleport to="#global-header-center">
  <div class="flex items-center gap-3">
    <button @click="router.push({ name: 'PedidoCanvas' })">+ Nuevo</button>
    <button @click="exportarEspejo" :disabled="exportandoEspejo">📊 Exportar Excel</button>
  </div>
</Teleport>
```

## 33. SISTEMA DE INGESTA Y FACTURACIÓN — ESTADO ACTUAL — SESIÓN 820 CA (2026-05-30)

### 33.1 Arquitectura de Documentos (Implementada)

| Documento | Estado | Ubicación código |
|---|---|---|
| Factura BORRADOR | ✅ Implementada | `facturacion/service.py:create_draft_from_pedido()` |
| Ingesta PDF ARCA | ✅ Implementada | `IngestaFacturaView.vue` + `ingesta/conserje.py` |
| Remito 0016 Fiscal | ✅ Implementado | `remitos/service.py:create_puente_factura()` |
| Anti-duplicación | ✅ Implementada (3 guardas) | `remitos/service.py:28-85` |
| Visor ARCA vs BORRADOR | ✅ Existe (visual-only) | `AfipComparisonOverlay.vue` |

### 33.2 GAPs Críticos (Pendientes)

**GAP 1: Resolución de discrepancia (Card #43)**
- `AfipComparisonOverlay.vue` muestra el diff pero no tiene acciones
- Faltan: botón "ARCA GANA", botón "PEDIDO GANA"
- Falta: endpoint `POST /remitos/resolver-discrepancia`
- Falta: Bit `PENDIENTE_AJUSTE_DOCUMENTAL` en `pedidos/constants.py` (dictaminado Bit 46)

**GAP 2: Split-Brain TIENE_NC/TIENE_ND (Bandera Roja #1, Card #44)**
```python
# ingesta/constants.py (IngestaFlags)
TIENE_NC = 1 << 2   # Bit 2 = valor 4
TIENE_ND = 1 << 3   # Bit 3 = valor 8

# facturacion/constants.py (FacturaFlags)
TIENE_NC = 1 << 17  # Bit 17 = valor 131072
TIENE_ND = 1 << 18  # Bit 18 = valor 262144
```
Mismo significado semántico, valores diferentes. Riesgo de bugs en comparaciones cruzadas.
Resolución pendiente script rescate lunes OF — afecta V5_LS_MASTER.db.

**GAP 3: Flujo NC/ND (Sin implementar)**
- No existe detección de NC/ND en OCR (ConserjeV2 no diferencia tipo de comprobante)
- No existe lógica de acumulación (Factura + NC + ND → comparar vs BORRADOR)
- No existe timeout para `PENDIENTE_AJUSTE_DOCUMENTAL`

### 33.3 Bits Fantasma Detectados — Clientes con flags_estado=65581

**Clientes afectados (pilot_v5x.db y V5_LS_MASTER.db):**
- Lácteos de Poblet SA (CUIT 33660726859)
- CENTRO PET ARGENTINA S.R.L. (CUIT 30715138707)

**Decodificación de 65581:**
- Bit 0 (1): EXISTENCE ✅
- Bit 2 (4): GOLD_ARCA ✅
- Bit 3 (8): V14_STRUCT ✅
- Bit 5 (32): MULTI_CUIT ✅
- **Bit 16 (65536): NO DOCUMENTADO ❓** — posible fantasma heredado

**Acción requerida (lunes OF, PIN 1974):**
Script de rescate en V5_LS_MASTER.db para limpiar Bit 16 (si es fantasma) y revisar Bit 5.
Investigar si Bit 16 tiene significado semántico en algún módulo legacy.

### 33.4 Preguntas Abiertas Respondidas (Auditoría 820-CA)

| # | Pregunta | Respuesta |
|---|---|---|
| 1 | ¿Múltiples BORRADOR por pedido? | DB soporta N:M, UI no lo gestiona |
| 2 | ¿0015→0016 automático? | Código OK (línea 812-822), UX falta |
| 3 | ¿facturas_remitos N:M? | ✅ SÍ implementado |
| 4 | ¿Ingesta acepta NC/ND? | ❌ NO, solo facturas |
| 5 | ¿PENDIENTE_AJUSTE bloquea? | ❌ Bit no existe aún (Bit 46 dictaminado) |
| 6 | ¿Timeout? | ❌ Sin mecanismo |
| 7 | ¿Visor reutilizable? | ✅ SÍ, AfipComparisonOverlay |

---

## 32. IDENTIDAD VISUAL ENTORNO P + GENOMA PEDIDOS V6 — SESIÓN 819 OF (2026-05-29)

### 32.1 Frontend Entorno P — Título y Favicon
**Archivos:** `static/index.html`, `static/favicon.svg`, `public/favicon.svg`

Cambios de identidad visual para distinguir entorno Mando (P) de desarrollo:
- **Título HTML** (línea 8 index.html): Cambio de "Sonido Líquido V5 [DESARROLLO] - D" a "Sonido Líquido V5 - Mando" para identificación clara en pestaña del navegador.
- **Favicon:** Reemplazo del diseño 4 cuadrantes neón (verde/amarillo/cyan/magenta) por fondo sólido púrpura (#6B21A8) + "SL" blanco. Proporciona identidad corporativa consistente y diferenciación instantánea de entorno.

Técnica: Uso de `<clipPath>` con `rx="20"` para esquinas redondeadas. SVG recortado y centrado con `text-anchor="middle"`.

**Impacto:** Operarios identifican visualmente si están en entorno de mando (producción) o desarrollo. Reducción de errores operacionales.

### 32.2 Genoma Pedidos V6.0 — Modelado Estados Logísticos vs Contables
**Diseño en BACKLOG** — Cards 29-30 del BOARD_V5.xlsx.

Problema resuelto: Confusión entre "entregado" (logístico) y "cobrado" (contable). Estos son eventos independientes:
- **ES_ENTREGADO** (Card 29): Nuevo estado que marca cuando la mercadería fue despachada/entregada, INDEPENDIENTEMENTE del cobro.
- **Bit COBRADO** (Card 30): Disparador contable que marca cuando el pago fue efectivamente cobrado. Dispara ciclo contable (facturación, actualización de cuenta corriente del cliente).

Doctrina: `Cobrado ⊂ Cumplido` (cobrado es un subconjunto de cumplido, no equivalente). Requiere definición de posición y transición de estados a cargo de Nike.

**Impacto:** Claridad contable. Permite reportes separados de "pedidos entregados sin cobro" (cuentas por cobrar) vs "pedidos cobrados pero no entregados" (casos especiales).

### 32.3 Excel Snapshot de Pedidos — Feature V5.9
**Card 31 en BACKLOG.**

Especificación técnica:
- Script Python que genera Excel solo lectura en Q:\Mi unidad\ sin necesidad de abrir el ERP.
- Formato: Un bloque por pedido con detalle de items (producto, cantidad, precio venta unitario, subtotal, costo unitario, costo total).
- Pie del bloque: subtotal, IVA (21%), total.
- Referencia histórica: Excel reports de V4 Legacy.

Caso de uso: Exportación rápida de pedidos para operaciones logísticas sin requerimiento de conexión a FastAPI.

---

## 31. HARDENING INGESTA — 3 FIXES QUIRÚRGICOS — SESIÓN 818 CA (2026-05-28)

### 31.1 Ruteo frontend ingesta/remitos — SIN prefijo `/api`
Las URLs de iframe y PDF del módulo de ingesta deben usar rutas relativas SIN prefijo `/api` (`/ingesta/...`, `/remitos/...`). `vite.config.js` proxea cada módulo por nombre (`/ingesta`, `/remitos`, etc.); **no existe proxy `/api`** y los routers en `main.py` se montan sin prefijo. Usar `/api/...` produce 404 (el panel comparativo de duplicados quedaba con iframes rotos).

### 31.2 `STATE_MASK` — constante de módulo, no miembro de clase
`STATE_MASK` está definido a nivel módulo en `backend/pedidos/constants.py`, NO como miembro de `PedidoFlags`. Acceder vía `PedidoFlags.STATE_MASK` lanza `AttributeError` → 500. Importar explícitamente: `from backend.pedidos.constants import PedidoFlags, STATE_MASK`. Afectaba la anulación en cascada de pedidos con `ORIGEN_FACTURA`.

### 31.3 Guard de `flags_estado` None
Toda mutación bitwise sobre `flags_estado` debe usar guard: `(flags_estado or 0) & ~BIT`. Si la columna es None, `&=` lanza `TypeError`. Aplicado en `anular-y-reingestar` (router.py:243) por paridad con el guard ya presente en la línea 218.

---

## 30. FIXES IVA ROSA + VIRGINIDAD FRONTEND + NAVEGACIÓN — SESIÓN 810 (2026-05-18)

### 30.1 ClientCanvas — `has4Pillars` bifurcado (FIX C4)
La validación de domicilio para alcanzar SOBERANÍA usa lógica diferenciada por color:
- **Rosa** (`flags & 16`): valida `es_entrega && calle.length > 2`. No requiere fiscal.
- **Gold/Blanco**: valida `es_fiscal && calle.length > 2`.

La línea `currentFlags &= ~2` fue **eliminada** de `ClientCanvas.vue`. IS_VIRGIN (Bit 1) es INTOCABLE desde el frontend — solo el backend lo apaga en CUMPLIDO o CAE real.

### 30.2 `_audit_sovereignty()` — Gap documentado
La inferencia automática de Bit 4 (Rosa) **requiere `segmento_id IS NOT NULL`** (línea 346, `backend/clientes/service.py`). Clientes creados sin segmento asignado no reciben el sello automático. Corrección: UPDATE manual con PIN 1974 + `flags_estado |= 16`. Deuda técnica pendiente: agregar rama alternativa.

### 30.3 PedidoCanvas — Stripping IVA Lista 5 para Rosa
La cascada de precios devuelve `Lista 5 = Lista_4 × 1.21` para clientes MINORISTA. El frontend corrige en `selectProduct`:
```javascript
if (isSinIVA.value && res.origen === 'LISTA_5') {
    precioFinal = precioFinal / 1.21;
}
```
El bloque IVA en el template usa `v-if="!isSinIVA"` — invisible para clientes informales.

### 30.4 Navegación — Named Routes obligatorias
Las vistas de pedidos usan **named routes** para navegación interna. Rutas literales como `/hawe/tactico` están **deprecadas y rotas** (sin entrada en el router).

| Destino | Named route |
|---|---|
| Canvas nuevo pedido | `{ name: 'PedidoCanvas' }` |
| Editar pedido existente | `{ name: 'PedidoEditar', params: { id } }` |

---

## 29. MOTOR BIPOLAR + IS_VIRGIN + ROSETI 1482 — DOCTRINA 809 (2026-05-18)

### 29.1 Motor Bipolar — Bit 12 Soberano para IVA
Canonizado sesión 809. El circuito IVA es controlado exclusivamente por el **Bit 12 (NO_FISCAL_FORCE = 4096) del PEDIDO**.
- `isSinIVA = !!(pedido.flags_estado & 4096)` → soberano para cálculo de totalFinal y documentos fiscales.
- `isClientRosa` (Bit 4 del cliente) → exclusivo para restricciones operativas (sin factura borrador, sin remito puente).
- Rosa SIEMPRE tiene Bit 12=1, pero el motor mira el pedido, no el cliente.

### 29.2 IS_VIRGIN — Bit 1 (Semántica Corregida)
- `IS_VIRGIN = 2` (Bit 1): **1 = Virgen** (borrado físico permitido) / **0 = Tocado** (bloqueado).
- Guard en `hard_delete_cliente`: `if not (current_flags & ClientFlags.IS_VIRGIN)` → bloquea tocados.
- Se apaga (→0) solo en: CUMPLIDO en `pedidos/router.py` o CAE en `facturacion/service.py`.
- Constante renombrada de `HAS_ACTIVITY → IS_VIRGIN` en 15 archivos (sesión 809).

### 29.3 Roseti 1482 — Domicilio Plantilla Rosa
- ID canónico: `59b01b5a-e81a-4e2a-b496-9d65fef9262b`
- Constante: `DOMICILIO_ROSETI_ID` en `backend/clientes/constants.py`.
- Lógica: `ClienteService._ensure_domicilio_rosa()` — si cliente Rosa sin domicilios → vincula automáticamente vía `domicilios_clientes`.
- Arquitectura: domicilios usa N:M (`domicilios_clientes`). Campo `cliente_id` en `Domicilio` es DEPRECATED.

## 28. NORMALIZACIÓN DE INFRAESTRUCTURA — SOBERANÍA TOMY (2026-05-11)

A partir de mayo de 2026, el entorno de Producción (Tomy) ha sido normalizado para eliminar ambigüedades con instalaciones legacy.

### 28.1 Ruta Canónica
- **Raíz de Producción**: `C:\dev\v5-ls-Tom`
- **ADN**: Se han purgado todas las referencias internas a `C:\dev\V5-LS` en scripts `.bat`, logs y archivos de configuración.

### 28.2 Gestión de Entornos en Producción
La estructura `v5-ls-Tom` mantiene la jerarquía de soberanía:
- `current/`: Instancia activa (Puerto 8090).
- `staging/`: Instancia de pruebas y pre-despliegue (Puerto 8091).
- `data/`: Bases de datos maestras (`V5_LS_MASTER.db`).

### 28.3 Protocolo de Actualización
Se utiliza el script `ACTUALIZAR_V5.bat` en la raíz. El proceso realiza un `git pull` desde el repositorio unificado de GitHub. El repositorio de Tomy (`v5-ls-Tom`) está saneado de archivos binarios (`.db`, `.pyc`), garantizando actualizaciones rápidas y ligeras.

## 15. ORÍGENES DE PEDIDO — DOCTRINA DE TRAZABILIDAD (Diseño v5.9, implementación pendiente)

Un Pedido puede nacer de tres orígenes distintos. El origen queda registrado en el campo `origen` y en bits de `flags_estado`:

| Origen | `origen` field | Bit `flags_estado` | Descripción |
|---|---|---|---|
| Operador | `DIRECTO` | — | Flujo normal. El operador crea el pedido. |
| Forzado por Remito | `FORZADO_REMITO` | `BIT_ORIGEN_REMITO` | El movimiento físico llegó sin pedido previo. Sin respaldo contable. Pendiente de facturar. |
| Forzado por Factura | `FORZADO_FACTURA` | `BIT_ORIGEN_FACTURA` | Se ingresó una factura AFIP sin pedido previo. **Tiene respaldo contable — no anular livianamente.** |

**Regla crítica:** El Remito siempre tiene `pedido_id NOT NULL`. Si no existe un pedido real, el sistema crea uno "forzado" con los datos de la factura/remito. No existe tabla separada de huérfanos.

**Flujo de ingesta de facturas (pendiente de implementación):**
1. Sistema pregunta: ¿A qué pedido corresponde esta factura?
2. Operador selecciona uno existente → vinculación directa.
3. Operador indica "ninguno" → sistema crea Pedido con datos reales (cliente, items, totales) + `flags_estado |= BIT_ORIGEN_FACTURA`.

## 16. ARQUITECTURA DE DOMICILIOS — JUNCTION TABLE N:M

El sistema tiene dos rutas de relación Cliente↔Domicilio:

- **Legacy (1:N):** `domicilios.cliente_id` FK directa. Usada por `create_domicilio` para guardar el registro.
- **Activa (N:M):** `domicilios_clientes` junction table. Usada por `GET /clientes/{id}` via `joinedload(Cliente.domicilios)`.

**Invariante crítico:** Todo domicilio creado para un cliente DEBE insertarse en `domicilios_clientes` además de en `domicilios`. Si solo se inserta en `domicilios`, el domicilio es invisible para todos los endpoints de lectura.

## 17. CLIENTES ROSA — DOCTRINA ARLEQUÍN V2 (Sesión 806, 2026-05-13)

### 17.1 Jerarquía de estados (flags_estado)

| Estado | Identificación por bits | Descripción |
|---|---|---|
| **Amarillo** | `!(flags & 4)` y `!(flags & 16)` | Sin Gold, sin sello Rosa. Camino a Blanco. |
| **Rosa** | `flags & 16` (`OPERATOR_OK` — Bit 4) | Sello informal. Validación manual del operador. |
| **Blanco/Gold** | `flags & 4` (`GOLD_ARCA` — Bit 2) | Datos homologados ARCA. Máxima jerarquía. |
| **Azul** | `flags & 32` (`MULTI_CUIT` — Bit 5) | CUIT compartido / Sucursales. |
| **Rosa Fucsia** | `flags & 64` (`TRUSTED_MANUAL` — Bit 6) | Corporativo informal (ej: Luvianka). |

**Referencia canónica completa:** `docs/GENOMA_UNIVERSAL.md` — sellado Nike Arq 5.5 sesión 806.

### 17.2 Inferencia automática de Rosa (`_audit_sovereignty`)

El método `_audit_sovereignty()` en `backend/clientes/service.py` infiere el sello Rosa automáticamente:
- Si el cliente **no tiene GOLD_ARCA** (Bit 2 apagado)
- Y **tiene segmento asignado**
- Y **no tiene CUIT real** (menos de 10 dígitos)

→ Enciende `OPERATOR_OK` (Bit 4). La transición Amarillo→Rosa es irreversible mientras no tenga CUIT. La transición Rosa→Blanco requiere acción explícita del operador.

### 17.3 Comportamiento en Pedidos

- **Rosa**: No requiere CUIT, domicilio fiscal ni condición IVA. El motor enciende `NO_FISCAL_FORCE` (Bit 12 = 4096) automáticamente al crear el pedido.
- **Gold/Blanco**: Pasa directo a verde en `clientValidation` sin evaluar otros campos.
- La validación en `PedidoCanvas.vue` usa bits directamente — no depende de `(flags & 15) in [...]`.

### 17.4 Consumidor Final / MOSTRADOR (CUIT 00000000000)

- `_audit_sovereignty()` fuerza `GOLD_ARCA` (Bit 2) si detecta CUIT = `00000000000`.
- El CUIT `00000000000` es **exclusivo del MOSTRADOR/GENÉRICO**: el sistema bloquea HTTP 400 si un segundo cliente intenta usarlo.
- Consumidor Final nace **Blanco Virgen** (flags = 15) — nunca infiere Rosa.

## 18. ARQUITECTURA N:M FACTURAS↔REMITOS + SISTEMA DE MIGRACIONES (Sesión 797-CA, 2026-05-06)

### 18.1 Tabla `facturas_remitos` — Relación N:M soberana

Una Factura puede estar asociada a múltiples Remitos y viceversa. La tabla de unión es soberana: tiene identidad propia y estado propio.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | `CHAR(32) PK` | GUID propio — no PK compuesta |
| `factura_id` | `CHAR(32) FK` | Referencia a `facturas.id` |
| `remito_id` | `CHAR(32) FK` | Referencia a `remitos.id` |
| `fecha_vinculo` | `DATETIME` | Timestamp de creación del vínculo |
| `flags_estado` | `BIGINT` | Estado del vínculo (1 = activo) |

**UNIQUE constraint:** `(factura_id, remito_id)` — un vínculo no se duplica.

### 18.2 Modelo ORM `FacturaRemito`

Ubicación: `backend/facturacion/models.py`. Clase completa con relaciones bidireccionales usando strings (regla anti-deadlock de CLAUDE.md):

- `Factura.vinculos_remitos` → `relationship("FacturaRemito", cascade="all, delete-orphan")`
- `Remito.vinculos_facturas` → `relationship("FacturaRemito")`
- `FacturaRemito.factura` / `FacturaRemito.remito` → back_populates respectivos

**Invariante de creación:** El vínculo se materializa ÚNICAMENTE en `RemitosService.create_puente_factura()`. El borrador de factura (`create_draft_from_pedido`) NO crea el vínculo — la factura en BORRADOR aún no tiene remito.

### 18.3 Doctrina de numeración ARCA (helper `_numero_legal_arca`)

```
Con CAE (ARCA):    0016-{punto_venta:04d}-{numero_comprobante:08d}
Sin CAE (manual):  0015-{fallback_id:08d}
```

- Prefijo `0016` = origen ARCA / oficial.
- Prefijo `0015` = serie manual / Rosa (doctrina Nike). Nunca `0001`.

### 18.4 Sistema de control de migraciones (`_migraciones_aplicadas`)

Tabla creada por `scripts/migrate_000_control_migraciones.py`. Evita doble ejecución de scripts.

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | `VARCHAR PK` | Identificador único del script (ej: `"026_factura_remitos"`) |
| `nro_sesion` | `INTEGER` | Número de sesión que lo aplicó |
| `aplicada_en` | `DATETIME` | Timestamp de aplicación |

**Patrón estándar para todo script de migración:**
1. Verificar existencia en `_migraciones_aplicadas` → SKIP si ya existe.
2. Ejecutar DDL.
3. Registrar en `_migraciones_aplicadas` con MIGRATION_ID + NRO_SESION.
4. Commit + close.

Referencia canónica: `scripts/migrate_000_control_migraciones.py`.

## 19. GENOMA `facturas.flags_estado` — `FacturaFlags` (Sesión 799-CA, 2026-05-08)

### 19.1 Clase de constantes `FacturaFlags`

**Archivo:** `backend/facturacion/constants.py`  
**Sellado:** Nike Arq 5.5

Define el mapa completo de bits del campo `flags_estado` en la tabla `facturas`. No mezclar con el `flags_estado` de otras tablas — cada tabla tiene su propio Genoma.

| Bit | Valor | Nombre | Semántica |
|-----|-------|--------|-----------|
| 0 | 1 | `EXISTENCE` | El registro existe y es válido |
| 1 | 2 | `HAS_ACTIVITY` | 1=virgen (nunca tocado), 0=tocado |
| 2 | 4 | `HAS_REMITO` | Tiene al menos un remito vinculado |
| 3 | 8 | `ACTIVE` | No anulada |
| 4–9 | — | Reservado | Libre para extensión en módulo facturación |
| 10 | 1024 | `V15_STRUCT` | Reservado global (marca de estructura V15) |
| 11–14 | — | Reservado | Libre |
| 15 | 32768 | `PASADO_A_PEDIDO` | Esta factura ya fue usada para crear/vincular un pedido |
| 16 | 65536 | `EN_CUARENTENA` | Bajo revisión manual — no operar |
| 17 | 131072 | `TIENE_NC` | Tiene nota de crédito asociada |
| 18 | 262144 | `TIENE_ND` | Tiene nota de débito asociada |
| 19 | 524288 | `ES_NC` | Este comprobante ES una nota de crédito |
| 20 | 1048576 | `ES_ND` | Este comprobante ES una nota de débito |
| 21 | 2097152 | `AUDITADA` | Revisada y certificada por operador |
| 22–29 | — | Reservado Contabilidad | Retenciones, percepciones (módulo futuro) |
| 30+ | — | Ultra-reservado | Extensiones de largo plazo |

**Estado inicial estándar de factura nueva:** `EXISTENCE | HAS_ACTIVITY | ACTIVE` = `1 | 2 | 8` = **11**

**Regla de lectura `HAS_ACTIVITY`:** La semántica es inversa a la intuitiva. Bit encendido (valor 2) significa **virgen** — el comprobante ingresó al sistema pero ningún operador lo procesó todavía. Bit apagado (valor 0) significa **tocado** — ya fue vinculado, auditado o procesado. Esta inversión es intencional (hereda doctrina Bit 1 del Arleq V2).

### 19.2 Campo `notas_auditoria`

**Modelo:** `backend/facturacion/models.py` → clase `Factura`  
**DDL:** `notas_auditoria VARCHAR` (nullable)

Campo de texto libre. Destinado a registrar observaciones del operador al certificar la factura. Trabaja en conjunto con el bit `AUDITADA` (bit 21):

- El bit señala **que** fue auditada (boolean).
- El campo preserva **qué** se observó (texto libre, auditaría detallada).

No tiene longitud máxima impuesta — el contenido es operativo, no estructural.

**Migración:** `scripts/migrate_029_facturas_notas_auditoria.py` — ejecutada en `pilot_v5x.db` sesión 799-CA.

### 19.3 Conserje `FACTURA_DUPLICADA` — endpoint `POST /remitos/ingesta-pdf`

**Archivo:** `backend/remitos/router.py`

Guard insertado **antes** del procesamiento del PDF. Lógica:

1. El payload parseado contiene `punto_venta` y `numero_comprobante`.
2. Se consulta `SELECT id FROM facturas WHERE punto_venta = :pv AND numero_comprobante = :nc LIMIT 1`.
3. Si existe registro → **HTTP 409** con body:
   ```json
   {
     "codigo": "FACTURA_DUPLICADA",
     "mensaje": "La factura ya existe en el sistema.",
     "factura_id": "<uuid-del-registro-existente>"
   }
   ```
4. Si no existe → flujo continúa normalmente.

**Contrato con el frontend:** El código `FACTURA_DUPLICADA` es discriminador — el frontend (`IngestaFacturaView`) puede distinguirlo de otros 409 (ej: `PEDIDO_DUPLICADO`) y ofrecer al operador navegación directa al comprobante existente.

**Invariante de integridad:** El par `(punto_venta, numero_comprobante)` identifica unívocamente una factura AFIP. No puede existir dos registros con la misma combinación.

---

## 1. DOCTRINA DE PRECIOS: "LA ROCA Y LA MÁSCARA"
El sistema V5 implementa una estrategia psicológica de precios:
* **La Roca (Precio Objetivo):** Es el valor real de rentabilidad que la empresa necesita cobrar (Backend). Es inamovible.
* **La Máscara (Precio de Lista):** Es el valor público ("inflado") sobre el cual se aplican bonificaciones.
* **Objetivo:** El sistema permite llegar a "La Roca" aplicando descuentos sobre "La Máscara", generando en el cliente la satisfacción de "ganar" una bonificación, mientras la empresa asegura su margen.

## 2. ARQUITECTURA DE CLIENTES (V5.4) - "UNA PLANTA = UN CLIENTE" [LEGACY]
* **Nota de Evolución:** Este modelo 1:1 ha sido superado por la **Bóveda Universal V5**. Aunque la base de datos permite duplicar CUITs para representar plantas, la arquitectura recomendada ahora es usar **Vínculos Geográficos** sobre un único maestro de CUIT.

## 14. BÓVEDA UNIVERSAL DE DOMICILIOS (VANGUARD VAULT V5)
Implementada en Marzo 2026, esta arquitectura desacopla los domicilios físicos de las entidades comerciales.
* **Modelo N:M**: Una entidad (`CLIENTE`, `PERSONA`, `TRANSPORTE`) puede tener N domicilios, y un domicilio puede pertenecer a N entidades.
* **Genoma de Relación**: La tabla `vinculos_geograficos` almacena el rol de la dirección mediante una máscara de bits:
    - **Bit 0 (1):** Fiscal.
    - **Bit 1 (2):** Principal / Entrega.
    - **Bit 3 (8):** Temporal / Excepcional.
* **Resolución de Domicilio**: El `RemitosService` ahora consulta la Bóveda para determinar el destino legal y físico del envío, eliminando la dependencia de columnas fijas en la tabla `pedidos`.

## 4. DESPLIEGUE DE TERMINALES REMOTAS (V5-LS SATÉLITE)
Implementado en Marzo 2026 para el operador Tomy. Esta configuración permite la independencia total de la terminal de producción.
* **Configuración de Red**:
    - **Host**: 192.168.0.34
    - **Puerto API**: 8090 (Backend Uvicorn/FastAPI)
    - **Puerto WEB**: 5174 (Frontend Python Server)
* **Punteros de Base de Datos**:
    - El sistema utiliza `V5_LS_MASTER.db` como identidad legítima (Malla de Oro).
    - Los ruteos internos han sido sintonizados para ignorar la base de desarrollo `pilot_v5x.db`.
* **Lanzador Maestro**: Se utiliza `LANZAR_V5_SOBERANA.bat` para el arranque dual armonizado.
* **Firewall Awareness**: Las llamadas de Axios han sido inyectadas con rutas absolutas al puerto 8090 para evitar bloqueos por políticas de seguridad del navegador.

## 5. SOPORTE TÉCNICO Y GEM
El soporte de Nivel 1 es realizado por el Agente IA "Ayuda HAWE".
* **Fuente de Verdad:** El Agente lee este manual directamente desde Google Drive.
* **Instrucción al Usuario:** Ante cualquier error (pantalla blanca, error 500), el usuario debe copiar el mensaje y pegarlo en el chat de Ayuda.

## 5. RUTAS Y VARIABLES (.ENV)
* `DATABASE_URL`: Apunta a la base local (SQLite).
* `PATH_DRIVE_BACKUP`: Ruta absoluta a la carpeta de Google Drive Desktop del usuario. Es vital para la Regla 4/6 (Backup automático cada 4 sesiones).

## 6. ARQUITECTURA DE CONTACTOS (V5.6)
* **Modelo Unificado:** La entidad `Contacto` actúa como nexo entre una persona física y una organización (Cliente o Transporte).
* **Gestión de Estado (Frontend):** Se utiliza `storeToRefs` (Pinia) obligatoriamente para garantizar reactividad en selects dinámicos (Cliente/Transporte).
* **Prevención de Fallos (Backend):** Las propiedades computadas como `contacto_principal_nombre` deben implementar bloques `try/except` para aislar fallos de integridad en registros individuales y evitar caídas en listados masivos (Error 500).

## 7. LOGÍSTICA TÁCTICA V7 (SPLIT ORDERS)
* **Concepto:** Un `Pedido` es una intención comercial (Reserva de Stock). Un `Remito` es una ejecución física (Movimiento de Mercadería).
* **Cardinalidad:** Un Pedido puede tener N Remitos (Entregas Parciales).
* **Gatekeeper Financiero:**
    * El sistema impide generar remitos oficiales si el Pedido no tiene el flag `liberado_despacho`.
    * Excepción: Usuarios con permisos pueden forzar el desbloqueo bajo su responsabilidad (Audit Log).
* **Safety Net:** La exportación a Excel detecta automáticamente si un pedido tiene logística simple (1 destino) o múltiple, adaptando la columna "Logística" para evitar errores de interpretación.

## 8. HUB LOGÍSTICO V5.7 (SPLIT VIEW)
* **Arquitectura Híbrida:** Se separa la dirección en dos entidades conceptuales:
    * **Fiscal (Panel Izquierdo):** Datos legales validados. Solo editable con Flag Fiscal.
    * **Logística (Panel Derecho):** Datos operativos del punto de entrega.
* **Mapeo de Datos:**
    * Para evitar inconsistencias, si un domicilio NO es fiscal, el sistema **copia automáticamente** los datos del panel logístico (Calle Entrega, Número Entrega) a los campos nucleares de la base de datos (`calle`, `numero`).
    * **Razón:** El backend espera la dirección física en `calle`. Si solo se llenaba `calle_entrega`, el registro quedaba "vacío" a nivel lógico.

    *   **Razón:** El backend espera la dirección física en `calle`. Si solo se llenaba `calle_entrega`, el registro quedaba "vacío" a nivel lógico.

## 9. PROTOCOLO PUENTE RAR-V5 (ARCA)
Incorporado en V6.3, este módulo conecta V5 con el legacy RAR V1 para validación fiscal.
*   **Arquitectura:** `AfipBridgeService` carga dinámicamente el módulo `Conexion_Blindada.py` de RAR.
*   **Resolución de OpenSSL (desde V5 02/04/2026):** El ejecutable se resuelve en orden:
    1. Variable de entorno `OPENSSL_PATH` (configurable en `.env`).
    2. Búsqueda automática en `PATH` del sistema via `shutil.which("openssl")`.
    3. Fallback: lista de rutas conocidas Windows (Git for Windows / System32).
    Ver `.env.example` para documentación de la variable.
*   **Puente Multi-Identidad (CUIT 20/30):** Debido a discrepancias en permisos fiscales, el puente conmuta automáticamente entre certificados:
    *   **Identidad Personal (20132967572):** Utilizada para servicios de Consulta de Padrón A13.
    *   **Identidad Empresa (30715603973):** Utilizada para servicios de Emisión (MTXCA/WSFE).
*   **Dependencias Críticas:** Requiere las librerías `zeep` y `lxml` en el entorno virtual (`venv`) del backend.
*   **Manejo de Errores:**
    *   Si RAR falla (timeout, sin internet), el backend captura la excepción y retorna un JSON con `error`, evitando caídas 500.
    *   **Archivos Temporales:** Se usan UUIDs para los XML de firma (`temp_auth_*.xml`) para evitar colisiones en entornos concurrentes.

## 10. ARQUITECTURA DE CLIENTES HÍBRIDOS (INFORMAL VS FORMAL)
Implementado en V6.3, el sistema permite la convivencia de dos tipos de clientes:
*   **Formal (Verde/Amarillo):** Tiene CUIT válido (11 dígitos). Requiere Domicilio Fiscal estricto. Validado contra ARCA.
*   **Informal (Rosa Chicle):** Sin CUIT o CUIT genérico. No requiere Domicilio Fiscal estricto (puede ser solo Entrega).
    *   **UX Pink Mode:** Se identifica visualmente con texto Fucsia y brillo neón en listados y fichas.
    *   **Transición:** Si un cliente Informal carga un CUIT, el sistema activa automáticamente el puente ARCA para completar sus datos fiscales y formalizarlo.
*   **Infiltración Vanguard (Verification Firewall):** La interfaz `AfipComparisonOverlay.vue` actúa como un cortafuegos visual:
    *   **Detección de Cambios:** Compara campo por campo (Razón Social, IVA, Dirección) y resalta inconsistencias en amarrillo neón.
    *   **Confirmación Requerida:** Los datos de AFIP solo se inyectan en el formulario local si el usuario presiona "Infiltrar Datos".
    *   **Domicilios Split:** El formulario de alta permite llenar solo la sección "Logística" (Derecha) y el sistema auto-completa la sección "Fiscal" (Izquierda) para evitar bloqueos de validación.

## 11. PERSISTENCIA INTELIGENTE (ARCA SYNC)
* **Problema:** El sistema protege los domicilios en actualizaciones (`UPDATE`) para evitar sobrescrituras accidentales.
* **Solución (Biotenk Fix):** En `ClienteInspector.vue`, se implementó una actualización explícita manual del domicilio fiscal dentro de la función `save()`. Si el formulario detecta cambios (vía infiltración ARCA), se dispara un `updateDomicilio` independiente antes de persistir los cambios generales del cliente.
* **Excepción:** Cuando se ejecuta una validación ARCA exitosa, el frontend activa una bandera `forceAddressSync`.
* **Comportamiento:** Al guardar, si esta bandera está activa, `saveCliente` incluye explícitamente el objeto `domicilios` en el payload, forzando al backend a actualizar la dirección fiscal con la "Verdad Oficial" de AFIP.

## 12. MÓDULO DE INGESTA AUTOMÁTICA (PDF ENGINE V6.5)
Incorporado en V6.4 (2026-02-19) y consolidado en V6.5 (2026-02-28).
*   **Motor:** `pypdf` + `fpdf2` + Regex Heurística (Backend Python).
*   **Estrategia de Parseo:**
    *   **Encabezados Compactos:** Soporta formatos donde CUIT y Razón Social comparten línea (ej: Lavimar).
    *   **Ítems por Anclaje:** Utiliza palabras clave como "unidades" o "litros" para extraer descripciones y cantidades, ignorando saltos de línea rotos en tablas complejas.
*   **Lógica "Confianza Ciega" (Trust Protocol):**
    *   El sistema asume que la Factura es la verdad.
    *   **Get-or-Create:** Si el CUIT detectado no existe en la base, se crea un Cliente nuevo automáticamente con los datos del PDF.
    *   **Dirección:** Se asigna una dirección fiscal genérica para cumplir con el modelo de datos, permitiendo al operador corregirla post-ingesta.
*   **Manejo de Errores:**
    *   El backend captura trazas completas de error y las envía al frontend para que el usuario sepa exactamente por qué falló un PDF (ej: "Archivo vacío", "No es PDF de texto").
    *   **Actualización V6.5 (Upsert Inteligente):** El sistema ahora verifica existencia por CUIT. Si el cliente existe con status bajo (<13), se actualiza a **Flag 13** (Gold Candidate) y se elimina el flag 'Virgin'. Si es nuevo, se inserta directamente en Flag 13 con estado 'PENDIENTE_AUDITORIA'.
    *   **Corrección Regex:** Se modificó el motor para escanear el texto crudo (`raw_text`) antes de limpiar, solucionando fallos en facturas compactas (LAVIMAR).
    *   **Workflow Frontend Asistido:** Implementado en `IngestaFacturaView.vue`, el componente cruza la "Infiltración Vanguard". Cualquier cliente derivado del PDF cuya validación AFIP falte (Nivel < 13) fuerza la apertura perentoria de `ClienteInspector.vue`.
    *   **Doctrina de Evolución (4-Bytes):** A nivel backend (`service.py`), los clientes insertados on-the-fly (`estado_arca='PENDIENTE_AUDITORIA'`, Flag=15 Virgen) pierden la bandera Virginity (`& ~ClientFlags.VIRGINITY`) mutando al nivel 13 Gold al momento exacto de formular/confirmar la carga en remitos.


## 13. PROTOCOLO GENOMA V14 (BITMASK DE IDENTIDAD)
Implementado en V14.5 y saneado en V14.8 (Marzo 2026), el sistema gestiona la identidad comercial mediante una máscara de bits (Bitmask) simplificada:
- **Bit 0 (1):** `EXISTENCE` (Activo en DB).
- **Bit 1 (2):** `VIRGINITY` (1=Sin movimientos / 0=Operado).
- **Bit 2 (4):** `GOLD_ARCA` (Validado contra satélite RAR).
- **Bit 3 (8):** `V14_STRUCT` (Protocolo Apolo activo).
- **Bit 4 (16):** `SABUESO_ALERT` (Alerta de riesgo o deuda).

### Lógica de Dominancia Visual:
1. **Rosa (9 o 11):** Pao de Tandil / Informal (Bits 0+3 + Virginity opcional).
2. **Blanco Gold (13 o 15):** Validado por ARCA (Bits 0+2+3 + Virginity opcional).
3. **Amarillo:** Estado base (Pendiente de validación ARCA).
- **Bit 5 (32):** `MULTI_Sede` (Sello Azul / Compartición Legal). Se activa automáticamente si el cliente tiene más de un domicilio habilitado.
- **Bit 6 (64):** `CONSOLIDATED` (Sello de Purga V14). Indica que el registro ha pasado por el proceso de unificación de CUITs.

### Lógica de Dominancia:
El color visual de la ficha se determina por la jerarquía de bits:
1.  **Azul (32):** Multicliente (Máxima prioridad de alerta).
2.  **Blanco Gold (4):** Validado por ARCA.
3.  **Rosa (16):** Operador OK / CUIT Genérico.
4.  **Amarillo (8):** Estado Base (Pendiente).

### Consolidación de Base de Datos (Marzo 2026):
Se implementó la política de **1 CUIT = 1 Registro Maestro**. 
- El script `consolidate_clients_v64.py` se encarga de unificar duplicados, transfiriendo pedidos e historial al registro principal.
- Los domicilios secundarios se mantienen como "Sedes" vinculadas al mismo CUIT bajo el bit `MULTI_Sede`.

### Seguridad de Datos (Escudo de Virginidad):
Durante la validación de AFIP, el sistema preserva el estado del Bit 1. Un cliente que ya ha operado comercialmente (Bit 1 = 0) nunca volverá a recibir el estado "Virgen" por una inyección de datos externos.

## 15. SISTEMA DE PAPELERA GLOBAL & PROTECCIÓN HISTÓRICA (GENOMA 14.8.1)
Implementada para prevenir la pérdida irreversible de datos comerciales por errores humanos en "Utilidades Maestras".
* **Papelera de Registro**: La tabla `papelera_registros` actúa como un búfer de seguridad. Antes de cualquier `DELETE` físico en el backend, el objeto es serializado recursivamente a JSON (limpiando tipos `Decimal`, `UUID` y `datetime`) y persistido en esta tabla.
* **Blindaje de Historial**: El sistema identifica registros históricos mediante el Bit 1 de `flags_estado` (0 = Histórico). 
    - **Prohibición**: El backend rechaza (403 Forbidden) cualquier solicitud de eliminación física para estos registros.
    - **Visualización**: En la interfaz de Utilidades Maestras, estos registros aparecen "grisados" (opacidad 60%) y con el botón de borrado deshabilitado.
* **Mecanismo de Rescate**: Aunque el borrado está bloqueado, la funcionalidad de reactivación ("Rescate") permanece disponible, permitiendo devolver registros históricos de la baja lógica sin comprometer la integridad de la base de datos principal.

## 16. SOBERANIA OPERATIVA V14.8.4 (PIN 1974)
Implementada el 18-03-2026. El criterio humano de carga prevalece sobre ARCA/AFIP.

### Promocion Automatica 15->13 (Veterano de Facto)
Si un cliente posee los 4 Pilares de Integridad de Carga al guardar, el sistema lo promueve automaticamente:
- **Bit 1 OFF** (`IS_VIRGIN = 2`): Quita el estado Virgen. El cliente pasa de Nivel 15 a Nivel 13 (Veterano Operado).
- **Bit 20 OFF** (`PENDIENTE_REVISION = 1048576`): Limpia el estado Amarillo.

**Los 4 Pilares:** razon_social + lista_precios_id + segmento_id + domicilio_fiscal.calle (>2 chars).

### Escudo Doble
- **Frontend** (`ClientCanvas.vue`): Opera antes de `payload.flags_estado = currentFlags` en `saveCliente`.
- **Backend** (`service.py`): Verifica 4 Pilares post-setattr en `update_cliente` y fuerza la mutacion.

### Color Independiente de AFIP
`getClientColorMode` ya no depende de `estado_arca`. Color blanco = `!(flags & 1048576)`. La lupa AFIP ya no es el unico camino al blanco.

### Lupa No Destructiva
`consultarAfip` muestra confirm() antes de sobreescribir una direccion fiscal manual con dato de ARCA. Si cancela, conserva la correccion manual.

## 17. REMITO MANUAL (SERIE 0015-)
Implementado el 19-03-2026 para permitir logística sin facturación previa (Clientes Rosa/Informales).

### Arquitectura de Creación:
*   **Ghost Pedidos**: El sistema genera un `Pedido` interno con `origen='MANUAL'` para mantener la integridad de la base de datos.
*   **Numeración**: Los remitos manuales utilizan la serie `0015-`, iniciando en `00003001` (Criterio de Continuidad Carlos).
*   **Resolución de Clientes**: Soporta clientes existentes o creación "al vuelo" mediante el modal `ClientCanvas`.
*   **Endpoints**:
    *   `POST /remitos/manual`: Recibe `ManualRemitoPayload`.
    *   `GET /remitos/{id}/pdf`: Genera el PDF oficial sobre la serie 0015.

## 18. EDICIÓN TÁCTICA DE INGESTA (EDITABLE GRID)
Mejora al motor OCR para permitir corrección humana de errores de lectura.
*   **Frontend**: `IngestaFacturaView.vue` utiliza una tabla de inputs reactivos conectada al `parsedData.items`.
## 19. SEGURIDAD DE SINCRONIZACIÓN: PROTOCOLO OMEGA V5.2 (BLINDADO)
Implementado el 19-03-2026 para evitar desincronías entre los entornos de la Oficina y Casa.
*   **Ojo de Halcón (`audit_v5.py`)**: Herramienta de auditoría física que rastrea cambios en disco en las últimas 12 horas.
*   **Rotación de Backups en Cascada (Fase 1B.2)**: Script automatizado (`backup_db.py`) que realiza backups de la base transaccional (`pilot_v5x.db` / `V5_LS_MASTER.db`) hacia el Silo en esquema Grandfather-Father-Son (slots de 3, 14 y 35 días) protegiendo el historial ante desastres.
*   **Bloqueo de PIN 1974**: El sistema tiene prohibido solicitar el PIN de cierre si existen discrepancias entre el estado de Git y los cambios físicos detectados en el disco.
*   **Certificación de Salida**: Es obligatorio ejecutar `git show --name-only HEAD` tras cada push para validar la inyección física de los commits.

## 20. MEMORIA DE SESIÓN (PROTOCOLO ALFA)
*   **Staging Early Check**: Al iniciar, el agente debe declarar la lista `ARCHIVOS_SESION` basándose en el `git status -s` inicial.
*   **Protección de Rama**: El sistema valida estrictamente la permanencia en `atenea-v5-vault-final`. Cualquier derivación no autorizada activa una ALERTA ROJA.

## 21. EDICIÓN DE REMITOS ADMITIDOS (RESTORE V5.2)
Implementado el 20-03-2026 para permitir correcciones en remitos ya generados (especialmente de ingesta).
*   **Backend**: 
    *   `PATCH /remitos/{id}`: Soporta actualización de cabecera (`numero_legal`, `cae`, `vto_cae`, `transporte_id`, `domicilio_entrega_id`).
    *   **Restricción**: Solo permitido para remitos en estado `BORRADOR`.
*   **Frontend**:
    *   `RemitoListView.vue`: Captura `@dblclick` sobre la fila del remito.
    *   **Modal de Edición**: Carga dinámicamente los domicilios del cliente asociado al pedido del remito.
*   **Parche Incompleto (Deuda Técnica)**: 
    *   Falta edición de bultos y valor declarado.
    *   Falta edición de ítems (cuerpo) post-generación.
    *   SISTEMA EN ESTADO CRÍTICO (BIT 3) por deuda de integridad en logística.

## 22. SOBERANÍA DEL ADDRESS HUB (V5.2 GOLD)
Implementada el 23-03-2026 para consolidar la independencia de los domicilios.
*   **Seeding Protocol**: Uso de `seed_hub.py` para migración masiva.
*   **Deduplicación Semántica**: El sistema agrupa direcciones idénticas bajo un único ID del Hub, incrementando el `usage_count`.
*   **Vínculos (Bit 21)**: Los domicilios migrados se marcan con el Bit 21 en `domicilios_clientes` para indicar que son espejos de datos legacy.
*   **Evolución GOLD**:
    - **is_maps_manual (Boolean)**: Nuevo campo en `Domicilio` para trackear si el link fue verificado por un humano o autogenerado.
    - **Auto-Maps Engine**: `ClienteService` autogenera links de búsqueda si el campo está vacío.
    - **N:M Relationship Manager**: Implementación de una interfaz dedicada para vincular/desvincular múltiples entidades a una misma fila física sin duplicidad de datos.

## 23. SOBERANÍA TOTAL DE REMITOS (V15.2.2)
Implementada el 25-03-2026 para otorgar control absoluto al operador sobre la ingesta y edición.
* **Modelo Editable E2E**: El flujo de ingesta (`process_pdf_ingestion` -> `create_from_ingestion`) ahora permite el override total de datos extraídos (Razón Social, CUIT, Ítems) antes de la persistencia.
* **Blindaje de Mapeo SQLAlchemy**: Se corrigió el error `InvalidRequestError` causado por rutas de módulos circulares en las relaciones. Se estandarizó el uso de nombres de clase simples (`"Pedido"`, `"Cliente"`) en lugar de rutas completas (`backend.pedidos.models...`).
* **Propiedades Dinámicas**: Se implementaron `@property` en el modelo para `razon_social` y `descripcion_display`, permitiendo visibilidad de datos sin necesidad de almacenamiento redundante en la tabla de remitos.

## 24. ARQUITECTURA DE 64-BITS (GY GENOMA V5.8)
Implementada para erradicar la deuda técnica de columnas booleanas legacy (`activo`, `direccion`, etc.).
* **Unificación de Genoma**: Todas las entidades nucleares (`Cliente`, `Domicilio`, `EmpresaTransporte`) utilizan ahora `flags_estado` (BigInteger) como fuente de verdad operativa.
* **Mapeo de Bits V5.8**:
    - **Bit 6 (64)**: `OC_REQUIRED` (Clientes). Dispara el mandato de OC Obligatoria en el Pedido.
    - **Bit 7 (128)**: `IS_OFFICE` (Domicilios). Identifica puntos de despacho internos (Roseti) y activa el **Poka-Yoke de Retiro**.
    - **Bit 3 (8)**: `RECOMMENDED` (Transportes). Identifica transportistas preferenciales ("Albertos").
* **Herencia de Transporte**: El `Cliente` posee ahora un puntero `transporte_habitual_id` que automatiza la selección logística en nuevos pedidos.
* **Puente Pinia (Frontend)**: Los stores (`clientes.js`, `logistica.js`) actúan como traductores dinámicos de bits a flags booleanos, garantizando retrocompatibilidad total de la UI.

## 25. ESCUDO DE IDENTIDAD NIKE V16.2 (BAG OF WORDS)
Implementado el 08-04-2026 para erradicar las colisiones por variaciones cosméticas en la Razón Social.
* **Lógica Bag of Words (BOW)**: El sistema ya no compara strings lineales. Descompone el nombre en "bolsas de palabras".
* **Algoritmo de Canonización**:
    1. **Normalización Unicode**: Eliminación de acentos y caracteres especiales.
    2. **Limpieza de Siglas**: "S.R.L." se convierte en "SRL" mediante remoción de puntos.
    3. **Tokenización**: División por espacios en blanco.
    4. **Filtro de Ruido**: Eliminación de tokens irrelevantes (longitud < 2 caracteres).
    5. **Ordenamiento Alfabético**: Los tokens se ordenan (Ej: `['SRL', 'INAPYR']` -> `['INAPYR', 'SRL']`).
    6. **Sellado Único**: Unión de tokens ordenados sin espacios en la columna `razon_social_canon`.
* **Sensor de Colisión (Frontend)**: `ClientCanvas.vue` invoca `/check-similarity` on-type. Si el score es 1.0 (Colisión de Identidad), el sistema dispara un bloqueo visual perentorio.
* **Homologación D-P**: Esta lógica está sincronizada tanto en el repo de desarrollo como en el satélite de producción (`V5-LS`).

## 15. PROTOCOLO DE IMPORTACIÓN DESDE CANTERA (V5.9 — 14/04/2026)
El módulo Cantera (`/bridge/productos/{id}/import`) es el camino estándar para incorporar productos del sistema legado al ERP activo.

### Auto-SKU (Rango Cantera)
* Cuando el producto del mirror JSON no tiene SKU (caso habitual en migración desde sistema anterior), el endpoint asigna automáticamente `MAX(sku) + 1` con un **piso de 9001**.
* Los SKUs de cantera quedan en el rango **9001–9999**, diferenciados de los manuales (10000+).
* El mirror puede serializar SKUs como floats (`"123.0"`). El parser usa `int(float(sku_raw))` para normalizar.

### flags_estado en Creación
* Todo producto importado desde cantera nace con `flags_estado = 3` (Bit 0 ACTIVE + Bit 1 VIRGIN).
* Esto lo hace elegible para la **Ley de Virginidad** (hard delete habilitado).
* Antes de este fix, los productos llegaban con `flags_estado = 0`, bloqueando el hard delete y causando confusión operativa.

### Endpoint `/health`
* La ruta raíz `/` fue renombrada a `/health` en D y P para liberar el catch-all `/{full_path:path}` que sirve el SPA.
* Sin este cambio, acceder a `http://host:puerto/` devolvía JSON en lugar de `index.html`, causando pantalla en blanco en el satélite de Tomy.

### 26. GESTIÓN DE RUBROS — GENOMA 64-BIT (V5.9)
La tabla `rubros` ahora implementa la arquitectura de **Genoma (64-bit)** mediante la columna `flags_estado` (BigInteger).

- **Bit 2 (4):** `BANNED`. Indica que el rubro ha sido dado de baja lógica (Purgatorio). No se muestra en los selectores del frontend, pero se preserva por integridad de los productos asociados.
- **Bit 3 (8):** `EXPATRIADO` (En Productos). Cuando un rubro es eliminado, sus productos migran al rubro "General" y activan este bit para auditoría de orfandad.

**Regla de Sincronización P (Aviso 21/04/2026):** Es crítico que el modelo SQLAlchemy en `current/backend` coincida con la base de datos Maestra. La ausencia de la columna en el modelo causa fallos de instanciación (Error 500) incluso si la columna existe físicamente en SQLite.

## 26. SISTEMA DE GESTIÓN DE RUBROS V5.9 (18/04/2026)

### Tabla `rubros` — flags_estado
La tabla `rubros` opera con `flags_estado` (BigInteger):
- **Bit 2 (4):** `BANNED` — rubro dado de baja lógica (Purgatorio). No se muestra en listados por defecto.

### Auto-Código de Rubro
El backend genera automáticamente el `codigo` (3 chars) si no se provee:
1. Toma los primeros 3 chars ASCII del nombre (normalizado, sin acentos, mayúsculas).
2. En caso de colisión: `base[:2] + str(suffix)` (sufijo numérico incremental).
3. `codigo` es `Optional[str]` en `RubroCreate` — nunca obligatorio desde el frontend.

### Protocolo de Exilio (Bit 3 en Productos)
Cuando un rubro es dado de baja, sus productos son migrados automáticamente al rubro "General":
- Se activa **Bit 3 (8) = EXPATRIADO** en `productos.flags_estado`.
- El producto queda funcional pero marcado como "huérfano" para trazabilidad.

### Protocolo de Adopción
- **Reasignación a cualquier rubro:** El backend limpia Bit 3 silenciosamente en `update_producto` (`flags_estado & ~8`). Sin fricción.
- **Reasignación a General desde huérfano:** El frontend intercepta antes de guardar y exige confirmación explícita del operador ("¿Queda en General no Huérfano?").

### Alta de Rubro en Caliente (F4)
Desde el inspector de Producto, el operador puede crear un rubro sin salir del formulario:
- **F4** en el selector de Rubro → abre modal ámbar (z-200).
- Campos: Nombre (obligatorio), Código (auto, editable, máx 3 chars), Margen Propuesto.
- Sin campo Padre (política V2 — rubros siempre en nivel raíz desde este flujo).
- Al confirmar: `productosStore.rubros.push(newRubro)` directo (sin re-fetch) + asignación `localProducto.rubro_id`.
- **F10** con el modal abierto → confirma el alta del rubro (no guarda el producto).

### Indicadores Visuales de Huérfandad (Frontend)
- **Tarjetas:** Dot neon `#24e70f` con glow y outline oscuro. Posición absoluta top-left, `animate-pulse`.
- **Listado por renglones:** Mismo dot sobre el ícono del producto.
- **Inspector abierto:** Borde verde neon reemplaza `hud-border-red`.
- **Filtro "Huérfanos":** Botón en el grupo Todos/Activos/Inactivos. Filtra client-side por `flags_estado & 8`.

### flags_estado en ProductoRead (fix crítico)
`flags_estado` debe estar explícitamente declarado en el schema `ProductoRead` (`flags_estado: int = 0`). Sin esto, el campo no viaja en la respuesta JSON y el frontend recibe `undefined` — todos los cálculos de bits devuelven 0 y los indicadores nunca se muestran.

## 27. Códice Arlequín V2 — Productos (2026-05-04)

### Bit 1 — HAS_ACTIVITY (valor 2)
Semántica unificada para CLIENTES y PRODUCTOS.
- Bit 1 = 1 → virgen/sin actividad → borrado físico habilitado (nace encendido)
- Bit 1 = 0 → tocado/con historial → borrado físico bloqueado (se apaga con primera operación)
Constante renombrada: IS_VIRGIN → HAS_ACTIVITY. Semántica idéntica en ambos módulos.
flags_estado default=2 en productos/models.py — todo producto nace virgen.

### nombre_canon — Deduplicación BOW
Campo agregado a tabla productos (VARCHAR 300, nullable, indexed).
Algoritmo: NFKD → ASCII → UPPER → tokenizar → filtro len>=2 → sort → concat.
Activo en create_producto() vía check_duplicate_name().
Tokens de 1 char excluidos por ambigüedad semántica (L, S, M, X).
El freno humano es la barrera correcta para variantes de talle/presentación.

### Doctrina Ingesta — Solo Lectura
create_from_ingestion() es READ-ONLY para productos y pedidos.
Un producto desconocido en PDF → alta desde módulo Productos → reintentar ingesta.
Una factura sin pedido vinculado → HTTP 409 PEDIDO_REQUERIDO.
Auto-creation deshabilitado permanentemente.

### Features Diferidas V6
- F1: Conciliación factura/pedido con discrepancias
- F2: Entregas parciales — bit ENTREGA_PARCIAL
- F3: Facturas huérfanas — cola de revisión supervisor
- Linaje de Productos: bifurcación SKUs con padre_id y bit RENOMBRADO

## 19. COMPONENTE IngestaItemModal — Extracción y Fix H (Sesión 798-OF, 2026-05-07)

### 19.1 Extracción del componente

El modal de resolución de ítems de factura fue extraído de `PedidoCanvas.vue` a su propio componente:
`frontend/src/views/Ventas/components/IngestaItemModal.vue`

**Props:** `items: Array` — ítems crudos con formato `{codigo, descripcion, cantidad, precio_unitario}`
**Emits:** `resolved(resolvedItems)` — ítems con `producto_id` asignado / `cancel` — operador canceló

PedidoCanvas.vue actúa como orquestador: maneja `showIngestaModal` y `ingestaItemsForModal`, delega toda la UI y lógica de resolución al componente.

### 19.2 Fix H — F4 dentro del modal

F4 en el buscador del modal abre la ventana satélite de alta de producto (`ProductosView` en `mode=satellite`) con el término de búsqueda actual. Implementado en `handleOverlayKeydown` del componente — el evento se detiene (`stopPropagation`) antes de llegar al handler global de PedidoCanvas. Guard adicional `if (showIngestaModal.value) return` en `handleGlobalKeys`.

### 19.3 Botón copy descripción

El campo de descripción de referencia (zona read-only) tiene un botón `fa-copy` que al clickear copia la descripción de la factura al campo buscador. El buscador inicia vacío — el operador tipea libremente o usa el botón copy.

### 19.4 Bugs D/E/F — F4 satélite PedidoCanvas

- **Fix D:** Nombre de ventana único `AltaProducto_${Date.now()}` — evita reutilizar tab bloqueado por browser.
- **Fix E:** `v-if="route.query.mode !== 'satellite' || showInspector"` en `<main>` de `ProductosView.vue` — suprime F4 handler hasta que inspector esté listo.
- **Fix F:** `fetchRubros()` defensivo en `ProductoInspector.vue` `onMounted` — en modo satellite el store de rubros no se precarga por App.vue.

## 29. GENOMA_UNIVERSAL — DOCUMENTO CANÓNICO DE BITS (Sesión 806, 2026-05-13)

### 29.1 Referencia
**Archivo:** `docs/GENOMA_UNIVERSAL.md`
**Sellado:** Nike Arq 5.5 — NOMINAL GOLD — PIN 1974

El GENOMA_UNIVERSAL es la fuente de verdad única para todos los mapas de bits del ecosistema V5.
Ningún `constants.py` puede divergir de sus tablas. Ante cualquier duda sobre un bit, consultar ahí primero.

### 29.2 Bits globales inmutables (todas las entidades)

| Bit | Valor | Nombre | Estado |
|---|---|---|---|
| 0 | 1 | `EXISTENCE` | ACTIVO |
| 1 | 2 | `HAS_ACTIVITY` | ACTIVO — 1=Virgen, 0=Operado |
| 10 | 1024 | `V15_STRUCT` | INTOCABLE |
| 13 | 8192 | `PROHIBIDO` | PROHIBIDO — Colisión LAVIMAR |

### 29.3 NO_FISCAL_FORCE — corrección canónica

`NO_FISCAL_FORCE` reside en **Bit 12 (valor 4096)**. El valor anterior 1024 era herejía: colisionaba con `V15_STRUCT` (Bit 10), marca de agua arquitectónica intocable.

- `backend/pedidos/constants.py`: `NO_FISCAL_FORCE = 4096`
- `frontend/src/views/Pedidos/PedidoList.vue`: todas las referencias usan `4096`

### 29.4 Protocolo de Emergencia MT

**Archivo:** `docs/protocolos/PROTOCOLO_EMERGENCIA_MT.md`

Ante un bug en producción (MT), el flujo obligatorio es:
1. Reproducir en D con copia de `V5_LS_MASTER.db`
2. Solucionar en D — commit
3. Cherry-pick D→P en MC — verificar
4. `git pull` en MT — aplicar migraciones si las hay

**Prohibido:** editar código directamente en P ni en MT. Excepciones de datos quirúrgicos requieren PIN 1974.

---

## Sección 30 — Doctrina de Virginidad (Bit 1 / HAS_ACTIVITY)
*Sellado: Sesión 808 — 2026-05-15*

### Semántica
`HAS_ACTIVITY` (Bit 1 = 2) en `clientes.flags_estado` indica que el cliente **nunca tuvo una operación comercial real registrada**. Cuando es 1 (activo), el cliente es "virgen" — no hay pedido cumplido ni factura AFIP a su nombre.

### Triggers canónicos para apagar Bit 1 (irreversible)
Solo dos eventos legítimos apagan Bit 1:

1. **Pedido llega a estado CUMPLIDO** — `PATCH /pedidos/{id}` con `estado: CUMPLIDO`. Hook en `pedidos/router.py`.
2. **Factura sellada con CAE real de AFIP** — `sellar_factura()` con `update_data.cae`. Hook en `facturacion/service.py`.

### Triggers que NO apagan Bit 1
- Promoción a cliente Gold (4 pilares): solo limpia Bit 20, no implica operación real.
- Creación de remito de ingesta (Vanguard Canon): es un documento de entrada, no originado en el sistema.
- Creación de remito manual: el pedido fantasma nace PENDIENTE — el operador lo marca CUMPLIDO conscientemente.

### Pedido fantasma de remito manual
El flujo de remito manual (`create_manual()`) crea un pedido fantasma con `estado="PENDIENTE"`. El operador lo marca CUMPLIDO desde la UI, activando el hook de virginidad en ese momento.

---

## Sección 31 — Atomicidad del flujo de Ingesta
*Sellado: Sesión 808 — 2026-05-15*

### Problema original
`IngestaService.approve()` tenía dos commits separados:
1. `RemitosService.create_from_ingestion()` → `db.commit()` interno
2. `IngestaService.approve()` → segundo `db.commit()` para raw + FacturasProcesada

Si el servidor crasheaba entre ambos commits, el raw quedaba en `RECIBIDO` con los registros downstream ya persistidos. Al reintentar: 409 por duplicado (Guard 1 detecta remito existente).

### Solución implementada (808)
- `create_from_ingestion()` ahora usa `db.flush()` — no commit. El caller es dueño del commit.
- `IngestaService.approve()` es el único punto de commit del flujo completo.
- Checkpoint: raw pasa a `PROCESANDO` antes de llamar a `create_from_ingestion()`.
- En caso de excepción: raw pasa a `ERROR` (estado visible, no silencioso).
- Endpoint deprecated `POST /ingesta-process` (usado por `IngestaFacturaView.vue`) recibió su propio `db.commit()` explícito.

### Estados de audit_status
| Estado | Significado |
|---|---|
| `RECIBIDO` | PDF subido, sin procesar |
| `PROCESANDO` | En vuelo — si persiste, indica crash del servidor |
| `PROCESADO` | Flujo exitoso completo |
| `ERROR` | Falló después del checkpoint — revisar downstream |
| `CUARENTENA` | Bloqueado manualmente por operador |

---

## Sección 32 — Hard Delete de Fósiles Pre-Genoma (Sesión 811, 2026-05-19)

### Problema
Clientes con `flags_estado=0` eran bloqueados por el guard IS_VIRGIN.
`not (flags & IS_VIRGIN)` interpreta `flags=0` como "tocado" — borrado imposible desde la UI.

### Fix backend (service.py)
```python
# Antes
if not (current_flags & ClientFlags.IS_VIRGIN):
    raise HTTPException(403, ...)
# Después
if current_flags != 0 and not (current_flags & ClientFlags.IS_VIRGIN):
    raise HTTPException(403, ...)
```
`flags=0` es fósil pre-genoma. El guard solo aplica a registros con `flags_estado > 0`.

### Fix frontend (HardDeleteManager.vue)
- Borde amber (`border-amber-500/30`) en lugar de gris
- Label `⚠️ CLIENTE IMPOSIBLE` + mensaje `flags=0 — fósil pre-genoma`
- Botón habilitado; integrity check devuelve `safe: true`

---

## Sección 33 — Flujo DEOU / Alta Rápida F4 (Sesión 811, 2026-05-19)

### Contexto
F4 desde PedidoCanvas → `altaClienteContext()` → `ClientCanvas` (modal) → `create_cliente`.

### Bugs corregidos
1. **Cliente nacía inactivo**: nibble=0 → `activo=bool(0&1)=False`. Fix: `currentFlags |= 3`
   (EXISTENCE + IS_VIRGIN) cuando no hay CUIT real y nibble=0 en `ClientCanvas.saveCliente()`.
2. **CUIT vacío en DB**: `cuit: ''` → `cuit: null` en `altaClienteContext()` y handler F4.
3. **Sin Rosa inference**: `_audit_sovereignty()` no se llamaba en `create_cliente()`.

### Orden correcto en create_cliente (post-fix)
```
_apply_cf_cuit_fallback → _audit_sovereignty → activo sync → _ensure_domicilio_rosa → db.commit()
```

---

## Sección 34 — CF CUIT Fallback Backend (Sesión 811, 2026-05-19)

### Doctrina
Cliente con condición IVA "Consumidor Final" sin CUIT recibe `'00000000000'` automáticamente.
Se llama ANTES de `_audit_sovereignty` para que el audit active `GOLD_ARCA` correctamente.

### Método
```python
@staticmethod
def _apply_cf_cuit_fallback(db_cliente):
    if db_cliente.cuit and db_cliente.cuit.strip():
        return
    is_cf = (
        db_cliente.condicion_iva is not None
        and db_cliente.condicion_iva.nombre is not None
        and "CONSUMIDOR FINAL" in db_cliente.condicion_iva.nombre.upper()
    )
    if is_cf:
        db_cliente.cuit = '00000000000'
```

### Invariantes
- Solo actúa si `cuit` es null o vacío (nunca sobreescribe un CUIT real).
- El guard de exclusividad `00000000000` no se dispara (opera sobre ORM, no el payload de entrada).
- Comportamiento AFIP estándar: múltiples CF pueden compartir `00000000000`.

## 31. BIT 40 — DISCRIMINA_IVA (Sesión 812 OF, 2026-05-20)

**Versión:** 2.1 (Bit 40 DISCRIMINA_IVA — sesión 812)

### 31.1 Definición
`ClientFlags.DISCRIMINA_IVA = 1 << 40` en `backend/clientes/constants.py`.
- **1 (encendido):** cliente Responsable Inscripto — discrimina IVA, recibe Factura A, el precio de campo es neto (precio de lista / 1.21).
- **0 (apagado):** CF / Monotributo / Exento / Rosa — no discrimina IVA, recibe Factura B, el precio de campo es final (IVA ya incluido).

### 31.2 Puntos de escritura del bit

| Nodo | Archivo | Trigger |
|---|---|---|
| Definición canónica | `backend/clientes/constants.py` | — |
| Auto-detección AFIP | `backend/clientes/services/afip_bridge.py` | RAR devuelve condicion_iva RI |
| Toggle permanente | `backend/clientes/service.py` → `_audit_sovereignty` REGLA 3 | Cada create/update cliente |

### 31.3 Regla 3 en `_audit_sovereignty`
```python
if db_cliente.condicion_iva and "RESPONSABLE INSCRIPTO" in db_cliente.condicion_iva.nombre.upper():
    db_cliente.flags_estado |= ClientFlags.DISCRIMINA_IVA
else:
    db_cliente.flags_estado &= ~ClientFlags.DISCRIMINA_IVA
```

### 31.4 Interacción con Motor Bipolar (Bit 12)
El Motor Bipolar (Bit 12 del pedido) sigue siendo soberano para el circuito fiscal. El Bit 40 del cliente complementa la presentación de precios:
- Bit 12 = 1 (negra) → precio neto siempre, sin importar Bit 40.
- Bit 12 = 0 + Bit 40 = 1 (blanca + RI) → precio neto en campo, IVA discriminado al pie.
- Bit 12 = 0 + Bit 40 = 0 (blanca + CF/otros) → precio final con IVA incluido.

### 31.5 Frontend (Sesión 813)
`isClienteRI = !!(BigInt(cliente.flags_estado) & (BigInt(1) << BigInt(40)))` — requiere BigInt por overflow JavaScript en bits > 31.
Implementación del `selectProduct` condicional pendiente en sesión 813.

---

## Sección 35 — Refactorización de PedidoCanvas y Poka-Yoke de Cierre (Sesión 817 OF, 2026-05-27)

### 35.1 Captura Reactiva de Estado en Frontend
Para corregir el bug donde `savePedido()` sobreescribía el estado a `"PENDIENTE"`, se introdujo la variable reactiva `estadoPedido = ref('PENDIENTE')`.
- En `loadPedido(id)`: se extrae del objeto deserializado el estado persistido `estadoPedido.value = p.estado || 'PENDIENTE'`.
- En `resetPedido()`: se restablece a su valor inicial `'PENDIENTE'`.
- En el payload de envío de `savePedido()`: se reemplaza el literal `"PENDIENTE"` por `estadoPedido.value`.

### 35.2 Lógica de Bloqueo de Pedidos Cerrados (Poka-Yoke)
- **Computed Property:** Se definió `isClosedOrder` para determinar si el pedido no es editable:
  ```javascript
  const isClosedOrder = computed(() => ['CUMPLIDO', 'ANULADO'].includes(estadoPedido.value));
  ```
- **Intercepción de Teclado:** En `handleGlobalKeys`, la pulsación de la tecla `F10` queda protegida para evitar la activación accidental del guardado:
  ```javascript
  if (!isSaving.value && items.value.length > 0 && clienteSeleccionado.value && !isClosedOrder.value) {
      savePedido();
  }
  ```
- **Guard en Guardado:** La función `savePedido()` aborta inmediatamente en caso de un pedido bloqueado, arrojando una notificación visual de error:
  ```javascript
  if (isClosedOrder.value) {
      return notificationStore.add('No se puede guardar un pedido CUMPLIDO o ANULADO.', 'error');
  }
  ```

### 35.3 Redefinición CSS de Viewport a Fluid Height
El desborde en el pie de página de `PedidoCanvas.vue` en sistemas Windows se debía al uso de clases CSS de Tailwind que definen altura absoluta del viewport (`h-screen`, `min-h-screen`). Dado que el componente padre define paddings y márgenes flexibles, el canvas excedía la zona visible.
- El div contenedor principal ahora declara `min-h-full w-full`.
- La tarjeta interna de edición declara `h-full flex-col`.
- Con esta configuración, el flexbox padre contiene al canvas de forma reactiva y el pie (TOTAL FINAL) permanece siempre visible por encima de la barra de tareas de Windows.

---

## 36. DOCTRINA ROSA/BLANCO + TABLERO AMBOS — SESIÓN 829 OF (2026-06-18)

### 36.1 Flujo de Activación PENDIENTE — Decisión Bifurcada Rosa vs Blanco (PedidoInspector, línea 570)

**Archivo:** `frontend/src/views/Pedidos/PedidoInspector.vue` línea 570

Cuando el operador cambia el estado de un presupuesto a **PENDIENTE**, el sistema ejecuta `handleStatusChange('PENDIENTE')` que toma una decisión bifurcada según la condición del cliente:

**Código:**
```javascript
if (newStatus === 'PENDIENTE') {
    const OPERATOR_OK = 16  // Bit 4 = cliente Rosa
    const esRosa = (props.modelValue.cliente?.flags_estado || 0) & OPERATOR_OK
    let newType
    if (esRosa) {
        newType = 'X'  // Rosa → SIN documentos, silencioso
    } else {
        const confirmComp = confirm(
            "¿Cómo continúa este presupuesto?\n\n" +
            "[ACEPTAR] = Lista 1 (con factura)\n" +
            "[CANCELAR] = Lista 2 (sin factura)"
        )
        newType = confirmComp ? 'FISCAL' : 'X'  // Blanco → pregunta al operador
    }
    await store.updatePedido(props.modelValue.id, { 
        estado: 'PENDIENTE', 
        tipo_facturacion: newType 
    })
}
```

**Lógica:**
1. Si cliente Rosa (Bit 4 encendido): asigna `tipo_facturacion = 'X'` automáticamente. Sin preguntar. Sin avisos. Operación silenciosa.
2. Si cliente Blanco (Bit 4 apagado): abre un `confirm()` dialog:
   - **[ACEPTAR]** → `FISCAL` (Lista 1, con factura, IVA 21%)
   - **[CANCELAR]** → `X` (Lista 2, sin factura, sin IVA)

**Impacto operacional:** El motor de precios y documentación posteriores respetan `tipo_facturacion`. Rosa nunca genera borrador fiscal, remito puente, ni factura. Blanco genera documentos según `FISCAL` vs `X`.

### 36.2 ClienteSummary.flags_estado — Enabling Frontend Validation

**Archivo:** `backend/pedidos/schemas.py` línea ~87

El campo `flags_estado` fue agregado a la respuesta `ClienteSummary` para permitir que el frontend valide la condición Rosa/Blanco ANTES de ejecutar `handleStatusChange`:

```python
class ClienteSummary(BaseModel):
    id: str
    razon_social: str
    cuit: Optional[str]
    domicilio_fiscal_resumen: Optional[str]
    condicion_iva: Optional[str]
    segmento_id: Optional[str]
    flags_estado: int  # ← NUEVO en sesión 829
```

**Uso en frontend:**
```javascript
const esRosa = (modelValue.cliente?.flags_estado || 0) & 16
```

Este campo es crítico para que PedidoInspector ejecute la lógica bifurcada sin solicitudes adicionales al backend.

### 36.3 Tablero Pedidos — Botón "Ambos" + Fucsia List 2

**Archivo:** `frontend/src/views/Pedidos/PedidoList.vue`

Tres cambios visuales coordinados:

1. **Botón "Ambos" (DEFAULT):**
   - Nueva opción: "Ambos" → muestra todos los pedidos (Oficial + Interno)
   - Gradiente: `bg-gradient-to-r from-emerald-600 to-pink-600`
   - Estado activo por defecto

2. **Renombramiento botón Interno:**
   - ANTES: "Circuito Interno" con `bg-gray-700`
   - AHORA: "Circuito Interno" con `bg-pink-600` (fucsia)
   - Semántica: Pink = List 2 = sin IVA = Rosa-compatible

3. **Filas Rosa — Styling condicional:**
   ```vue
   :class="(p.flags_estado & 4096) ? 'bg-pink-950/30 border-l-2 border-pink-500/40' : ''"
   ```
   - Si Bit 12 encendido (NO_FISCAL_FORCE): fila con fondo oscuro fucsia + borde pink
   - Ayuda visual rápida para identificar pedidos sin IVA

**Impacto operacional:** El operador ve "Ambos" por defecto → cobertura completa sin filtros accidentales. Al clickear "Circuito Interno", los pedidos Rosa aparecen destacados en fucsia.

### 36.4 Validación Rosa Flexible — segmento.id Anidado

**Archivo:** `frontend/src/views/Pedidos/PedidoInspector.vue` línea ~1298

**ANTES:**
```javascript
if (!c.segmento_id) throw new Error('Segmento requerido');
```

**DESPUÉS:**
```javascript
if (!c.segmento_id && !c.segmento?.id) {
    throw new Error('Segmento requerido');
}
```

**Motivo:** El backend puede devolver `segmento` como objeto anidado `{id, nombre}` en lugar de solo `segmento_id`. La validación acepta ambas formas para máxima flexibilidad.

