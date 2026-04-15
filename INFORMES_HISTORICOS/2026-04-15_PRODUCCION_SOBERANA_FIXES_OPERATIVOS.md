# Informe de Sesión: Producción Soberana — Fixes Operativos + Diseño Doctrinal

**Fecha**: 2026-04-15  
**ID de Sesión**: Omega-20260415  
**Agente**: Claude Code (Sonnet 4.6)  
**Estado del Sistema**: **NOMINAL GOLD**  
**Entorno**: OF  
**Operadores**: Carlos (arquitecto) + Tomy (operador en producción, V5-LS)

---

## 1. Punto de Partida

Primera sesión con el sistema en modo producción real: Tomy operando en V5-LS (Soberana) mientras Carlos supervisaba desde P (Sonido_Liquido_V5). La sesión fue íntegramente reactiva — los bugs aparecieron en tiempo real mientras Tomy intentaba trabajar.

**Contexto previo:** El sistema de domicilios había sido corregido en backend en sesión anterior pero el frontend tenía un bug de Pinia que destruía el store. El frontend no había sido buildeado con ese fix.

**Aclaración de terminología establecida en esta sesión:**
- **D** = "Distribuida" = `C:\dev\V5-LS` (lo que usa Tomy — producción)
- **P** = "Propia" = `C:\dev\Sonido_Liquido_V5` (entorno local de Carlos)
- Regla de sync: todo fix en D se replica en P.

---

## 2. Intervenciones

### 2.1 Fix Domicilios — Triple Causa del 500

El error 500 al guardar domicilios (Sanatorio Materno, ARCA) tenía tres causas encadenadas:

**Causa A — Backend: `is_maps_manual` duplicate kwarg**  
`create_domicilio` en `service.py` hacía `model_dump()` sin excluir `is_maps_manual`, y luego lo pasaba también explícitamente al constructor de `Domicilio()`. Python lanzaba `TypeError: got multiple values for keyword argument`.  
Fix: `model_dump(exclude={..., 'is_maps_manual'})`.

**Causa B — Backend: junction table `domicilios_clientes` no insertada**  
`create_domicilio` guardaba el domicilio en la tabla `domicilios` (con FK legacy `cliente_id`) pero nunca insertaba en la junction table N:M `domicilios_clientes`. `GET /clientes/{id}` usa `joinedload(Cliente.domicilios)` que traversa la junction → el domicilio recién creado era invisible.  
Fix: `db.execute(domicilios_clientes.insert().values(...))` post-flush.

**Causa C — Frontend: Pinia store corruption**  
`createDomicilio` en `clientes.js` hacía `this.clientes.splice(index, 1, response.data)` donde `response.data` es un objeto `Domicilio`, no un `Cliente`. Reemplazaba el cliente entero en el store con el domicilio → corrupción de store → loop de navegación en HaweView.  
Fix: `client.domicilios.push(response.data)`.

**Archivos afectados (D y P):**
- `backend/clientes/service.py`
- `frontend/src/stores/clientes.js`

---

### 2.2 Clientes Rosa — Fix `clienteEsVerde`

`PedidoTacticoView.vue` evaluaba a todos los clientes con los mismos tres criterios: CUIT ≥ 11 dígitos, domicilio fiscal activo, condición IVA. Los clientes Rosa (sin CUIT, gestión informal) fallaban los tres → badge rojo pulsante + confirm dialog en cada pedido.

La arquitectura de `flags_estado` ya identificaba a los clientes Rosa: `(flags_estado & 15) in [9, 11]`. El backend los trataba correctamente (no les exigía domicilio para la medalla). El frontend no lo sabía.

Fix: detección de `isRosa` en el computed y retorno inmediato `true` para ellos.

**Archivos afectados (D y P):**
- `frontend/src/views/Pedidos/PedidoTacticoView.vue`

---

### 2.3 Migración GENERAL → General (ambas DBs)

El Explorador de Rubros mostraba "General" (id=26) y "GENERAL" (id=28) duplicados.

- D: 4 productos migrados de id=28 a id=26. GENERAL dado de baja (`activo=0`).
- P: 7 productos migrados. Igual resultado.

El rubro "GENERAL" queda inactivo pero presente en el padrón para auditoría.

---

### 2.4 Fix Crítico: PedidoCanvas Edit Mode

**Bug:** Cada vez que Tomy abría un pedido existente para modificarlo, el sistema creaba un pedido NUEVO en lugar de actualizar el original. Causa: `savePedido()` en `PedidoCanvas.vue` siempre llamaba `POST /pedidos/tactico` sin importar si había `route.params.id`.

El backend tenía el endpoint `PATCH /pedidos/{id}` correctamente implementado (incluyendo reemplazo de items y recálculo de totales) — nunca se usaba.

Fix: detección de modo edición con `route.params.id` y uso condicional de PATCH vs POST.

**Impacto operacional:** Antes del fix, Tomy generó los siguientes duplicados en producción:
- DeLuca: #16 (original ANULADO) → #17 (nuevo, correcto) → luego #17 anulado → nuevo #16
- Lácteos: #9 (ingesta, ANULADO) → #18 creado
- LABME: #8 (ingesta, ANULADO) → #19 creado
- MYM: #15 (original) → #18, #19 creados en dos intentos de corrección

**Limpieza DB ejecutada:**
- Primera pasada: borrados #17, #18, #19 (items + pedidos). Próximo: #17.
- Segunda pasada (aparecieron nuevos duplicados porque el fix no estaba deployado): borrados #17, #18 nuevamente. Estado final: próximo pedido = #20.

**Archivos afectados (D y P):**
- `frontend/src/views/Ventas/PedidoCanvas.vue`

---

### 2.5 Fix: Botón "Editar Nota" Invisible en PedidoInspector

El lápiz ✏ de edición de nota en el inspector de pedidos tenía `opacity-0` con `group-hover` — invisible hasta que el usuario pasaba el mouse exactamente encima. Tomy no podía anotar el motivo de anulación.

Fix: `opacity-0 group-hover/nota:opacity-100` → `text-yellow-500/50` (siempre visible).

**Archivos afectados (D y P):**
- `frontend/src/views/Pedidos/PedidoInspector.vue`

---

### 2.6 Diseño Doctrinal: Orígenes de Pedido (Sin código — acordado para próxima sesión)

**Problema identificado:** La ingesta de facturas creaba pedidos en $0 silenciosamente (para satisfacer el `NOT NULL` de `pedido_id` en `remitos`). Estos pedidos "fantasma" ensuciaban el stock y confundían al operador.

**Diseño acordado:**

No se crea un archivo separado de "huérfanos". El Pedido es siempre un Pedido. La distinción se hace mediante bits libres de `flags_estado`:

```
BIT_ORIGEN_REMITO    = 2^X  → Pedido creado porque entró un remito sin padre
                               Sin respaldo contable. Pendiente de facturar.
BIT_ORIGEN_FACTURA   = 2^Y  → Pedido creado porque se ingresó una factura
                               Tiene respaldo contable en AFIP. No anular livianamente.
```

El flujo correcto para ingesta de facturas:
1. Sistema pregunta: ¿A qué pedido corresponde esta factura?
2. Si el operador selecciona uno → se vincula
3. Si no existe → sistema crea Pedido con datos reales de la factura (cliente, items, totales), marca `flags_estado |= BIT_ORIGEN_FACTURA`

**Implicancias:**
- Un pedido con `BIT_ORIGEN_FACTURA` activo debe disparar advertencia antes de anular (el hecho contable ya ocurrió en AFIP)
- El campo `origen` en `pedidos` ya existe — se usará semánticamente: `FORZADO_FACTURA` / `FORZADO_REMITO`
- La tabla `remitos` mantiene `pedido_id NOT NULL` — siempre habrá un padre (real o forzado)

**Pendiente de implementación:** Requiere definir bits exactos libres en `flags_estado` + PIN 1974 para schema si hace falta.

---

### 2.7 Infraestructura — Lanzadores (Sesión anterior, consolidado aquí)

- `INICIAR_V5_SL_Tomy.bat`: launcher combinado que activa Soberana Y abre el browser desde P, sin necesidad de navegar a V5-LS.
- `SATELITE_TOMY.bat`: check HTTP previo (PowerShell `Invoke-WebRequest` 4s timeout). Si el servidor no responde: pantalla roja + "Avisale a Carlos". Si responde: abre normalmente.

---

## 3. Métricas

| Métrica | Valor |
|---|---|
| Bugs críticos resueltos | 4 (500 domicilios, edit→create, Rosa, nota invisible) |
| Causas del bug domicilios | 3 encadenadas (kwarg, junction table, Pinia) |
| Pedidos duplicados eliminados | 5 (dos pasadas de limpieza) |
| Rubros fusionados | GENERAL→General (4 prods en D, 7 en P) |
| Archivos backend modificados | 2 (service.py, models import) |
| Archivos frontend modificados | 4 (clientes.js, PedidoCanvas.vue, PedidoInspector.vue, PedidoTacticoView.vue) |
| Builds ejecutados | 1 (D/V5-LS, 6.91s, limpio) |
| Entornos sincronizados | D y P — paridad confirmada |
| Decisiones de arquitectura | 1 (Orígenes de Pedido — diseño acordado, implementación pendiente) |

---

## 4. Deudas Técnicas Activas

| ID | Descripción | Prioridad |
|---|---|---|
| DT-01 | Implementar BIT_ORIGEN_FACTURA / BIT_ORIGEN_REMITO en `flags_estado` + refactor de `create_from_ingestion` | ALTA |
| DT-02 | Botón de acceso a ABM de Rubros desde Gestión de Productos | MEDIA |
| DT-03 | Acción "Notas" (como Observaciones en Clientes) accesible sin abrir el inspector completo | BAJA |
| DT-04 | Diseño de "conciliación": vincular pedido forzado con pedido real cuando aparece | MEDIA |

---

## 5. Estado de Cierre

- **Sistema D (V5-LS)**: NOMINAL GOLD. Frontend buildeado y deployado a `static/`. Soberana apagada para el día.
- **Sistema P (Sonido_Liquido_V5)**: NOMINAL GOLD. Paridad con D confirmada. Vite dev server.
- **DB D**: `V5_LS_MASTER.db` — pedidos limpios, próximo #20, GENERAL dado de baja.
- **DB P**: `pilot_v5x.db` — GENERAL dado de baja, paridad con D.
- **Rama D**: `main`
- **Rama P**: `stable-v5-of-20260330`
