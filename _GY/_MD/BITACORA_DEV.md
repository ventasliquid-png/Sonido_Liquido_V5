## SESIÓN 818: DETECCIÓN TEMPRANA DE DUPLICADOS + FIXES UI (OF OMEGA)
**Fecha:** 2026-05-28
**Locación:** OF
**Objetivo:** Implementar la detección temprana de facturas duplicadas en la ingesta de PDFs raw, permitiendo la anulación y reingesta con PIN 1974 de comprobantes en estado BORRADOR y la redirección/visualización para remitos ya despachados. Resolver cascada de borrado en Remito para evitar huérfanos en `FacturaRemito` y salvaguardar la trazabilidad marcando el procesado viejo como "ANULADA" en vez de borrar el registro. Resolver bug de includes() sobre CUIT nulo en filtrado de clientes (HaweView.vue) y bucle de redirección en creación de nuevo pedido táctico limpiando `ingestaData` al desmontar (PedidoCanvas.vue).
**Estado:** NOMINAL GOLD — PIN 1974 | Hash final: f7a48c08

### Hito 1: Detección Temprana de Duplicados & Ciclo de Anulación y Reingesta
* **Detección temprana:** Al subir un PDF a `POST /ingesta/raw`, se realiza una búsqueda en `facturas` por clave única (`tipo_comprobante`, `punto_venta`, `numero_comprobante`). Si existe match, se devuelve metadatos de duplicado al frontend.
* **UI de Comparación:** El frontend detecta la respuesta de duplicado y muestra un panel especial de comparación bloqueando el flujo estándar.
* **Bifurcación de Acciones:**
  * Si el remito asociado está en **BORRADOR**, se permite la acción "Anular procesado y re-ingestar con este PDF" previa verificación del PIN Maestro "1974".
  * Si el remito ya no es BORRADOR, se muestra un botón para visualizar el remito actual y se bloquea la re-ingesta.
* **Endpoint de Anulación y Reingesta (`POST /ingesta/raw/{raw_id}/anular-y-reingestar`):**
  * Valida el PIN de autorización ("1974").
  * Si el remito está en BORRADOR, marca el RAW viejo con el Bit 11 (`DUPLICATE` = 2048).
  * Marca el procesado viejo (`procesada_vieja.estado = "ANULADA"`) preservando trazabilidad de auditoría.
  * Si el pedido asociado provino de la factura, se anula (`estado = "ANULADO"`, flag `ES_ANULADO`).
  * Elimina el remito viejo en BORRADOR (con cascada de borrado para evitar huérfanos).
  * Elimina la factura vieja espejo.
  * Habilita el nuevo RAW (`audit_status = "RECIBIDO"`, limpia Bit 11) para procesamiento normal.

### Hito 2: Cascada de Borrado en Remito & Integridad
* Se confirmó que el modelo `Remito` posee `cascade="all, delete-orphan"` configurado en su relación `items` (hacia `RemitoItem`).
* Se agregó `cascade="all, delete-orphan"` en la relación `vinculos_facturas` (hacia `FacturaRemito`) en `backend/remitos/models.py` para erradicar registros huérfanos en la tabla intermedia al eliminar un remito.

### Hito 3: Fix A — HaweView null.includes()
* **Causa raíz:** `HaweView.vue:771` filtraba clientes evaluando `cliente.cuit.includes(query)`. Dado que CUIT puede ser null en la base de datos para clientes informales, esto provocaba un error de tipo `Cannot read properties of null (reading 'includes')`.
* **Resolución:** Se agregó un guard para fallback de string vacío: `(cliente.cuit || '').includes(query)`.

### Hito 4: Fix B — Redirección Nuevo Pedido Táctico
* **Causa raíz:** Al navegar al canvas de creación manual de nuevo pedido táctico, el store Pinia quedaba con datos de ingesta previos (`ingestaData`) si el operador cancelaba una ingesta previa sin limpiarla. Esto gatillaba una redirección no deseada al módulo de Ingesta en lugar de mantener al usuario en el canvas.
* **Resolución:** Se agregó la llamada a `pedidosStore.clearIngestaData()` en el hook `onUnmounted` de `PedidoCanvas.vue`, garantizando que la navegación limpie el estado al abandonar el canvas.

---

## SESIÓN 817: SYNC D→P→MT + MIGRACIONES + FIXES UI (OF OMEGA)
**Fecha:** 2026-05-27
**Locación:** OF
**Objetivo:** Sincronizar el entorno de desarrollo (D) con producción (P) y Mesa Táctica (MT). Reconstrucción y build completo en P/MT. Ejecutar scripts de migración de base de datos en MT (Bit 40, Bit 20/19, fecha_vencimiento y Genoma V6). Corregir bug en `PedidoCanvas.vue` de estado de pedido hardcodeado ("PENDIENTE"). Implementar validación y salvaguarda Poka-Yoke para pedidos en estado `CUMPLIDO` o `ANULADO`. Corregir bug visual de altura en `PedidoCanvas.vue` (h-screen -> h-full) para evitar corte por la barra de tareas de Windows.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash final: ec5cb6de

### Hito 1: Sincronización y Despliegue de Infraestructura
* Sincronización de backend (183 archivos) y frontend/src (116 archivos) desde D a P/current.
* Reconstrucción del entorno virtual (venv), instalación de dependencias requeridas (incluyendo PyMuPDF) y compilación del frontend en producción con éxito.

### Hito 2: Ejecución de Migraciones de Base de Datos en MT
* Script de re-auditoría de Bit 40 (DISCRIMINA_IVA) para 28 clientes Responsable Inscripto (excluyendo LAVIMAR).
* Script de reparación masiva de consistencia de bits (Bits 20 y 19) en 9 clientes anómalos.
* Migración física de base de datos (`ALTER TABLE pedidos ADD COLUMN fecha_vencimiento DATE`) y migración de estado de pedidos al Genoma V6 en banda 32+ (excluyentes: `ES_PRESUPUESTO`, `ES_FIRME`, `ES_CUMPLIDO`, `ES_ANULADO`).

### Hito 3: Fix PedidoCanvas Estado Hardcodeado & Poka-Yoke
* **Causa raíz:** `savePedido()` enviaba siempre `estado: "PENDIENTE"`, pisando el estado real del pedido al guardar en edición.
* **Resolución:**
  * Se agregó la variable reactiva `estadoPedido = ref('PENDIENTE')`.
  * `loadPedido()` ahora captura el estado del pedido: `estadoPedido.value = p.estado || 'PENDIENTE'`.
  * `savePedido()` utiliza `estado: estadoPedido.value` en su payload.
  * Se implementó un badge visible en el encabezado de solo lectura que indica el estado del pedido.
  * Se agregaron salvaguardas Poka-Yoke: si el pedido es `CUMPLIDO` o `ANULADO`, se muestra un banner de advertencia ("Este pedido está [ESTADO] y no puede editarse"), se deshabilitan los botones de Guardar y Guardar/Imprimir en la UI, se bloquea el guardado mediante atajo de teclado F10 y se interrumpe preventivamente al inicio de `savePedido()`.

### Hito 4: Fix de Altura (Bug Barra de Windows)
* **Causa raíz:** La raíz de `PedidoCanvas.vue` definía `min-h-screen` y la tarjeta interna `h-screen` (que se traducen a `100vh`). Sin embargo, en el layout `HaweLayout.vue`, el componente se dibuja dentro de un contenedor flexible con padding `p-4` y `overflow-hidden`. Esto hacía que la tarjeta desbordara el contenedor por exactamente el padding, cortando el pie del canvas (TOTAL FINAL y botones de guardar) bajo la barra de tareas de Windows.
* **Resolución:** Se reemplazó `min-h-screen` por `min-h-full` en el div raíz y `h-screen` por `h-full` en la tarjeta interna de `PedidoCanvas.vue`. Con esto, el canvas se adapta perfectamente a la altura fluida calculada por su contenedor padre.

### Hito 5: Burocracia y Sello OMEGA
* Ejecución de checkpoint WAL sobre `pilot_v5x.db` (`PRAGMA wal_checkpoint(FULL)`).
* Copiado y respaldo de base de datos a `Q:\Mi unidad\V5_Silo_Claude\`.
* Actualización de `ESTADO_ECOSISTEMA.md`, `INBOX.md` y generación del reporte histórico de sesión 817.

---

## SESIÓN 816: FIX INGESTA/PEDIDO + SALVAGUARDAS REMITOS (OF OMEGA)
**Fecha:** 2026-05-26
**Locación:** OF
**Objetivo:** Corrección de bugs encadenados en el módulo de ingesta y vinculación de pedidos, reparación de AttributeError en endpoint approve, y remoción de endpoint obsoleto. Corrección de ImportError en router de pedidos (_aplica_iva). Incorporación de salvaguardas defensivas para remitos en get_remito_pdf importadas desde P. Análisis comparativo de archivos .py entre P y D.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash final: 39309805

### Hito 1: Bug Ingesta/Pedido (Bugs 1, 2 y 3)
* **Bug 1 (AttributeError):** Corregido en `backend/ingesta/router.py`. La llamada a `IngestaService.approve` retorna un diccionario en lugar de un objeto. Se corrigieron los accesos a `procesada["id"]` y `procesada["estado"]`.
* **Bug 2 (Validación Pedido):** Implementada validación estricta de `pedido_id` en `backend/ingesta/service.py` para evitar vinculaciones nulas desde el backend.
* **Bug 3 (Selector de Pedido):** Se modificó el modal de aprobación en `frontend/src/views/Pedidos/IngestaFacturaView.vue` para forzar la selección de un pedido vinculante y enviar el payload con `pedido_id_vinculado`. El botón de la ficha de remito pasó de "Generar Remito" a "Proceder".
* **Endpoint deprecado:** Se eliminó la ruta `/remitos/ingesta-process` de backend/remitos y del frontend, unificando todo bajo el router de ingesta.

### Hito 2: ImportError en Pedidos Router
* Se eliminaron las declaraciones de importación interna redundantes de `PF` y `ClientFlags` dentro del helper `_aplica_iva` en `backend/pedidos/router.py`. Ahora se usan los del scope global para evitar fallos por alias inexistentes en constants.py.

### Hito 3: Sincronización de Salvaguardas de Remitos
* Se importaron las validaciones defensivas de P a D en `backend/remitos/router.py` (`get_remito_pdf`) para verificar la existencia de `remito.pedido` y de `remito.pedido.cliente` antes de generar el archivo PDF, previniendo caídas con excepciones HTTP 400.

### Hito 4: Análisis Comparativo P vs D
* Se ejecutó un análisis de archivos `.py` entre D (`Sonido_Liquido_V5`) y P (`v5-ls-Tom`).
* Se identificó que la raíz literal de P sólo contiene 9 archivos. La versión activa y desplegada se encuentra en `C:\dev\v5-ls-Tom\current\backend`.
* Existe paridad casi exacta entre D y P (Current), exceptuando el archivo `backend/core/utils/text.py` que sólo se encuentra en D (contiene `normalize_name`).

### Hito 5: Burocracia y Respaldo
* Se ejecutó el WAL checkpoint completo sobre `pilot_v5x.db`.
* Se copió la base de datos `pilot_v5x.db` al silo oficial `Q:\Mi unidad\V5_Silo_Claude\`.
* Se actualizaron `ESTADO_ECOSISTEMA.md`, `INBOX.md`, `CAJA_NEGRA.md`, y se generó el informe histórico `2026-05-26_FIX_INGESTA_PEDIDO_816.md`.

---

## SESIÓN 815: AUDITORÍA GENÓMICA + APPLY_IVA BIT 40 (CA OMEGA)
**Fecha:** 2026-05-22
**Locación:** CA
**Objetivo:** Auditoría forense completa del genoma flags. Diagnóstico causal Bit 40 (DISCRIMINA_IVA) — 28/29 RI clientes desincronizados. Reparación masiva de anomalías (37 total). Implementación helper `_aplica_iva()` centralizando fiscal logic. PROTOCOLO OMEGA V2.2 Fase 2 (Burocracia).
**Estado:** NOMINAL GOLD — PIN 1974 | Hash final: 1faac75e

### Hito 1: Auditoría Forense — Diagnóstico Causal Bit 40
* **Problema:** 28/29 Responsable Inscripto clientes con `Bit 40 (DISCRIMINA_IVA) = 0` cuando deberían ser 1.
* **Causa:** Clientes creados/actualizados PRE-Sesión 812 (cuando REGLA 3 implementada) nunca pasaron por `_audit_sovereignty()` post-implementación.
* **Evidencia:** JOFRE SERGIO OMAR (updated 2026-05-21, POST-812) tenía Bit 40=1; ALFAJORES JORGITO (updated 2026-04-08, PRE-812) tenía Bit 40=0.
* **Conclusión:** `_audit_sovereignty` solo se llama en create/update cliente, no retroactivamente. Patrón sistémico detectado: cada nueva regla deja históricos desactualizados.

### Hito 2: Anomalías Identificadas (37 total)
* **Bit 40 (DISCRIMINA_IVA):** 28/29 RI clientes con bit=0 en lugar de 1.
* **Bit 20 (PENDIENTE_REVISION):** 6 clientes con bit=1 pero 4+ pilares completos (fantasma).
* **Bit 19 (MEDALLA_ROSA):** 3 clientes Rosa (Bit 4) sin Bit 19 — inconsistencia color.
* **CF CUIT fallback, IS_VIRGIN, Bit 2 (GOLD_ARCA):** Verificados consistentes — 0 anomalías.

### Hito 3: Script Re-auditoría Bit 40 — PIN 1974
* `backend/scripts/re_audit_bit40.py`: ejecutado contra `pilot_v5x.db`.
* Lógica: Para cada cliente RI (`condicion_iva.nombre LIKE "%RESPONSABLE INSCRIPTO%"`), toggle Bit 40 ON.
* Resultado: 28 clientes reparados. Verificación post: `SELECT * WHERE Bit40=0 AND Condicion_IVA~RI` → 0 restantes.
* Commit: d84641b8.

### Hito 4: Script Reparación Masiva Bits 20 + 19 — PIN 1974
* **Reparación 1 (Bit 20):** 6 clientes con Bit 20=1 + lista_precios + segmento + 4+ domicilios. Apagado Bit 20.
* **Reparación 2 (Bit 19):** 3 clientes Rosa (Bit 4=1) sin Bit 19. Encendido Bit 19 (MEDALLA_ROSA).
* Verificación post: 0 anomalías restantes en ambos casos (100% cobertura).
* Commit: 1faac75e.

### Hito 5: Centralización apply_iva() en router.py
* **Problema:** Fiscal logic duplicada en 5 locaciones (create + update + add_item + update_item + delete_item) con inconsistencia: algunas verificaban estado, otras no.
* **Solución:** Helper `_aplica_iva(pedido, cliente) -> bool` implementando Doctrina V6:
  - Circuito Negro (Bit 12 NO_FISCAL_FORCE=1) → siempre False (nunca IVA).
  - Sin cliente → False.
  - Circuito Blanco → solo RI (Bit 40) aplica IVA.
* **Integración:** Reemplazadas 5 instancias de `tipo_facturacion in ["A", "B", "FISCAL"]` con llamadas a `_aplica_iva()`.
* **Bonus:** PedidoFlags → PF alias corregido en `toggle_circuito_bipolar`.

### Hito 6: PROTOCOLO OMEGA V2.2 — Fase 2 (Burocracia)
* **Fase 1B:** WAL checkpoint (`PRAGMA wal_checkpoint(FULL)`) ejecutado en `pilot_v5x.db`.
* **Fase 2:** Actualización de 3 archivos de documentación:
  - ESTADO_ECOSISTEMA.md: CA/D row con hash 1faac75e, estado OK, alert resolved.
  - CAJA_NEGRA.md: Nueva entrada sesión 815, incremento "Sesión actual: 815", documentación auditoría.
  - BITÁCORA_DEV.md: Esta entrada (en curso).
  - INFORME_HISTÓRICO: Creación de 2026-05-22_AUDITORIA_GENOMICA_815CA.md.

### Commits
* `d84641b8` (815 CA): apply_iva helper + Bit 40 re-auditoría script + centralización fiscal logic.
* `1faac75e` (815 CA OMEGA): Reparación masiva Bits 20+19 + ESTADO_ECOSISTEMA.md + CAJA_NEGRA.md update.

### Pendiente → Sesión 816 CA
* Fase 4-7 OMEGA V2.2 (Auditoría de peso, Verificación órbita, Higiene Antigravity).
* Mapa de flags para UX (Utilidad Maestra).
* 6 bugs pedidos (c) CRÍTICO, d) ALTA, a-b) MEDIA, e-f) BAJA).

---

## SESIÓN 814: GENOMA PEDIDOS V6 + OPERACIÓN MUDANZA + DIFF 4 (OF)
**Fecha:** 2026-05-22
**Locación:** OF
**Objetivo:** Canonización de PedidoFlags Genoma V6 (banda 32+). Migración y Operación Mudanza de 31 pedidos históricos incorporando fecha_vencimiento. Transiciones de estado seguras en router.py mediante STATE_MASK. Implementación de Diff 4 en PedidoCanvas.vue con BigInt bitwise para cliente y desglose fiscal Ley 27.743.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash final: 5e1e2445

### Hito 1: Genoma Pedidos V6 & Constantes
* `PedidoFlags` en `backend/pedidos/constants.py` define la banda baja (bits universales como `NO_FISCAL_FORCE` = Bit 12) y banda alta (bits >= 32) para ciclo de vida y auditoría forense.
* Estados excluyentes (`STATE_MASK`): `ES_PRESUPUESTO` (Bit 32), `ES_FIRME` (Bit 33), `ES_CUMPLIDO` (Bit 34), `ES_ANULADO` (Bit 35).
* Flags ortogonales acumulables: `RESERVA_STOCK` (Bit 36), `TUVO_CIRCUITO` (Bit 37), `ORIGEN_FACTURA` (Bit 38), `ORIGEN_RETROACTIVO` (Bit 39), `CAMBIO_A_NEGRO` (Bit 41), `CAMBIO_A_BLANCO` (Bit 42).
* Commit: `5c231ecb` (Feat PedidoFlags)

### Hito 2: Operación Mudanza (Base de Datos)
* Migración del campo string `estado` a la estructura de bits en la base de datos `pilot_v5x.db`.
* 31 pedidos migrados conservando integridad de negocio y añadiendo columna `fecha_vencimiento`.
* Commit: `14abd5a0` (Genoma V6 + Mudanza)

### Hito 3: Router Backend (Soberanía Transaccional)
* **Paso A (Escrituras):** Integración de `STATE_MASK` en escrituras de `backend/pedidos/router.py` para asegurar que las transiciones de estado borren el bit previo y guarden el nuevo estado de forma excluyente.
* **Paso B (Lecturas):** Reemplazo de accesos directos de lectura de estado por operaciones bitwise.
* Commits: `f8e1df84` (Paso A) y `9fdda7ed` (Paso B)

### Hito 4: PedidoCanvas.vue (Diff 4 Frontend)
* **BigInt Safety:** Uso de `BigInt(cliente.flags_estado || 0)` y operadores de BigInt (ej. `1n << 40n`) en `isClienteRI` para prevenir truncado y pérdida de precisión de JS en números > 31 bits.
* **Motor Bipolar:** `isSinIVA` alineado con Bit 12 del pedido (`NO_FISCAL_FORCE`) y el Bit 40 del cliente (`DISCRIMINA_IVA`).
* **Lógica selectProduct:** En precios `LISTA_5`, solo los clientes RI (`isClienteRI`) reciben el neto recalculado (división por 1.21). CF, Monotributo, Exento y Negro preservan el precio original con IVA.
* **Desglose Fiscal (Ley 27.743):**
  - Cliente Responsable Inscripto (en circuito blanco): IVA discriminado.
  - Consumidor Final / Monotributo (en circuito blanco): IVA contenido detallado en leyenda del pie.
  - Circuito Negro / Exento: IVA $0.00.
* Commit: `5e1e2445` (Diff 4 PedidoCanvas)

### Pendiente → Sesión 815
* Integrar `apply_iva` en `router.py` usando el Bit 40 del cliente.
* Bug de ingesta/remitos en la ventana de pedidos.
* Bug de UI en ficha remito (barra de Windows).
* Lista flotante de operador (tooltip 7 listas).

---

## SESIÓN 812: DISCRIMINA_IVA BIT 40 + PURGA HEREJÍA DEL 15 (OF)
**Fecha:** 2026-05-20
**Locación:** OF
**Objetivo:** Implementar Bit 40 DISCRIMINA_IVA. Purgar Bit 15 de pilot_v5x.db (5 clientes). Sellar doctrina Herejía del 15 en BIBLIOTECA_NIKE.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash D: b0ac3c47

### Hito 1: Bit 40 DISCRIMINA_IVA — constants.py
* `ClientFlags.DISCRIMINA_IVA = 1 << 40` — nuevo bit en `backend/clientes/constants.py`.
* Semántica: 1 = Responsable Inscripto (discrimina IVA, Factura A, precio neto / 1.21). 0 = CF / Mono / Exento / Rosa.

### Hito 2: Auto-detección en afip_bridge.py
* `AfipBridgeService._fetch_from_rar()`: si condicion_iva contiene "RESPONSABLE INSCRIPTO" (o "(INFERIDO)"), enciende DISCRIMINA_IVA en el dict de retorno al frontend.

### Hito 3: Regla 3 en _audit_sovereignty (service.py)
* Toggle permanente en create/update: `condicion_iva.nombre` con "RESPONSABLE INSCRIPTO" → `flags_estado |= DISCRIMINA_IVA`. CF / Mono / Exento / None → `flags_estado &= ~DISCRIMINA_IVA`.

### Hito 4: Purga Herejía del 15
* 5 clientes en `pilot_v5x.db` con Bit 15 (32768 = FacturaFlags.PASADO_A_PEDIDO) encendido por error de IA.
* Purga SQL: `UPDATE clientes SET flags_estado = flags_estado & ~32768 WHERE flags_estado & 32768`.
* DB saneada. Canario: NOMINAL GOLD.

### Hito 5: BIBLIOTECA_NIKE.md — doctrina Herejía del 15
* Módulo 2 sellado con ítem "La Herejía del 15": prohíbe `1<<15` en `clientes.flags_estado`. Bit 15 es exclusivo del genoma de facturas (PASADO_A_PEDIDO).

### Pendiente → Sesión 813
* Diff 4 PedidoCanvas.vue: `selectProduct` + presentación precio por Bit 12 (negro) + Bit 40 (RI) + CF. `isClienteRI` computed ya diseñado (BigInt Bit 40).

---

## SESIÓN 811-CA: SINCRONIZACIÓN Y AUDITORÍA DE ANOMALÍAS (CA)
**Fecha:** 2026-05-19
**Locación:** CA
**Objetivo:** Sincronizar con OF (git pull) y auditar anomalías del Bit 19 vs Bit 4.
**Estado:** NOMINAL GOLD — Hash D: 3f608adb

### Hito 1: Sincronización
* Git pull integrado de 7 commits (sesiones OF 810 y 811).
* Canario certificado localmente: `flags_estado = 13`.
* WAL checkpoint (PRAGMA wal_checkpoint(FULL)) ejecutado correctamente.

### Hito 2: Auditoría de anomalías de color (Bit 19 ON / Bit 4 OFF)
* **MYM ODONTOLÓGICOS LA PLATA:** Válido por diseño. Al ser Consumidor Final/Genérico (CUIT 00000000000), se fuerza a Gold (nibble 15) por lo que no infiere Rosa (no tiene Bit 4), pero recibe la medalla Rosa (Bit 19) por soberanía base de facturación.
* **SERGIO JOFRE:** Anómalo. CUIT real pero Condición IVA ausente (`None`). Bit 19 forzado por aserciones/excepciones manuales heredadas en scripts de verificación.
* **Pao Tandil:** Anómalo. CUIT null y segmento null. Al no tener segmento, no recibe Bit 4, y sus flags no han sido recalculados por la auditoría transaccional.

---

## SESIÓN 811: HONNEY + DEOU F4 + CF CUIT FALLBACK (OF)
**Fecha:** 2026-05-19
**Locación:** OF
**Objetivo:** Fix hard delete fósiles flags=0. Fix alta rápida DEOU F4. CF CUIT fallback backend.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash D: 208d6a46 | Hash P: 937d5be

### Hito 1: HONNEY — hard delete fósiles flags=0
* Guard IS_VIRGIN: `if current_flags != 0 and not (current_flags & IS_VIRGIN)`.
* HardDeleteManager.vue: fila amber, label "⚠️ CLIENTE IMPOSIBLE", botón habilitado, integrity safe.
* Commit: `1e5d4327` (D) / `85a48b8` (P)

### Hito 2: DEOU F4 — alta rápida cliente correcto
* Bug A: `currentFlags |= 3` cuando nibble=0 — EXISTENCE+IS_VIRGIN mínimo vital.
* Bug B: `cuit: ''` → `cuit: null` en `altaClienteContext()` y F4 handler de PedidoCanvas.
* Bug C: `_audit_sovereignty()` + activo sync + `_ensure_domicilio_rosa()` en `create_cliente()`.
* Commit: `0286f0df` (D) / `0b31fe2` (P)

### Hito 3: CF CUIT fallback — backend soberano
* `_apply_cf_cuit_fallback()`: condicion_iva CONSUMIDOR FINAL + cuit null → '00000000000'.
* Llamado antes de `_audit_sovereignty` en create y update.
* Commit: `208d6a46` (D) / `937d5be` (P)

---

## SESIÓN 810: FIX C4 ClientCanvas + IVA Rosa + Navegación PedidoCanvas (OF)
**Fecha:** 2026-05-18
**Locación:** OF
**Objetivo:** FIX C4 has4Pillars virginidad + bifurcación domicilio Gold/Rosa. Fix IVA Rosa PedidoCanvas. Fix syntax error Vite. Fix navegación Nuevo/Edit. Migración Bit 4 clientes Rosa en D y P.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash D: ff77a309 | Hash P: 3e060bb

### Hito 1: FIX C4 — ClientCanvas + Doctrina Virginidad
* `has4Pillars` bifurcado: domicilio `es_entrega` para Rosa, `es_fiscal` para Gold.
* Eliminada línea `currentFlags &= ~2` — violación doctrina virginidad. IS_VIRGIN solo lo apaga el backend en CUMPLIDO o CAE real.
* Commit: `bf406415` (D) / `5adf6f4` (P)

### Hito 2: FIX PedidoCanvas — IVA Rosa + Syntax + Navegación
* Syntax error Vite (`Unexpected token 1306:10`): eliminado bloque `else {}` espurio en `savePedido` que intentaba colgar como tercer else de un if/else ya cerrado.
* IVA Rosa: `selectProduct` divide `/1.21` cuando `isSinIVA && origen === 'LISTA_5'`. Template `v-if="!isSinIVA"` oculta bloque IVA pie de pantalla para clientes informales.
* Reset post-save: `resetPedido(skipConfirm=true)` — elimina `confirm()` espurio que disparaba porque items aún estaban en memoria al momento del reset.
* Navegación "Nuevo": 2 ocurrencias ruta muerta `/hawe/tactico` en `PedidoList.vue` → `{ name: 'PedidoCanvas' }`.
* Navegación edición: 2 ocurrencias `/hawe/tactico?edit=` en `PedidoInspector.vue` → `{ name: 'PedidoEditar', params: { id } }`.
* Commit: `ff77a309` (D) / `3e060bb` (P)

### Hito 3: Migración Bit 4 — Clientes Rosa D y P
* Diagnóstico: `_audit_sovereignty()` línea 346 solo infiere Bit 4 si `has_segmento AND not has_real_cuit`. Clientes creados sin `segmento_id` no reciben sello automático.
* UPDATE con PIN 1974 en `V5_LS_MASTER.db`: ANA ROBLES, Cecilia Pascual, LUISA PISCITELLI, Pao Tandil → `flags_estado |= 16`. 4/4 confirmadas.
* Sincronizado en `pilot_v5x.db` (D): Cecilia Pascual y LUISA PISCITELLI (nuevas); Ana Robles ya tenía Bit 4 desde el inicio de sesión.

### Commits
* `bf406415` (D) / `5adf6f4` (P): FIX C4 ClientCanvas + virginidad + domicilio bifurcado Gold/Rosa
* `ff77a309` (D) / `3e060bb` (P): FIX PedidoCanvas syntax + IVA Rosa + reset + navegación

---

## SESIÓN 809: AUDITORÍA CRUZADA + IS_VIRGIN GLOBAL + MOTOR BIPOLAR + ROSETI 1482 (CA)
**Fecha:** 2026-05-18
**Locación:** CA
**Objetivo:** Auditoría cruzada Opus/Antigravity pedidos y clientes. IS_VIRGIN rename global. Canonizar Motor Bipolar Bit 12. Implementar Roseti 1482 para clientes Rosa.
**Estado:** NOMINAL GOLD (OMEGA pendiente 810) — PIN 1974 | Hash D: 4010b655

### Hito 1: Fixes Backend Pedidos (Opus — C1/C3/C5)
* C1: `delete_pedido` — variable `pedido` no definida → NameError/500. Fix: query con eager load.
* C3: `NO_FISCAL_FORCE` ignorado en cálculo IVA — 5 puntos en router.py corregidos con bitwise.
* C5: `STRICT_MODE_VIOLATION` inalcanzable — `nivel_lista=3` era default antes del check. Fix: `nivel_lista=None`.

### Hito 2: Fixes Frontend PedidoCanvas (C1-C5)
* C1: `totalFinal` — `isSinIVA` basado en Bit 12 del pedido (soberano), no en `isClientRosa`.
* C2: Factura borrador + remito puente solo si `!clienteRosa`.
* C3: `wasIngesta` capturado antes de `clearIngestaData()` — bifurcación ingesta/manual.
* C4: "Guardar e Imprimir" con `v-if="pedidosStore.ingestaData"`.
* C5: 409 STRICT_MODE_VIOLATION → early return en catch, bloquea adición de item.

### Hito 3: Motor Bipolar — canonización doctrinaria
* Bit 12 (NO_FISCAL_FORCE=4096) del PEDIDO soberano para IVA.
* `isClientRosa` (Bit 4) exclusivo para restricciones operativas (documentos fiscales).
* Rosa SIEMPRE tiene Bit 12=1, pero el cálculo mira el pedido, no el cliente.

### Hito 4: IS_VIRGIN rename global
* `HAS_ACTIVITY → IS_VIRGIN` en 15 archivos. Cero ocurrencias residuales.
* Guard `hard_delete_cliente` invertido: `if not (current_flags & IS_VIRGIN)`.
* Semántica corregida: Bit 1=1 virgen/borrable, Bit 1=0 tocado/bloqueado.
* `nivel_id` huérfano eliminado en ClientCanvas.vue:1557.

### Hito 5: Roseti 1482 — domicilio plantilla Rosa
* Domicilio `ROSETI 1482 CABA` creado en pilot_v5x.db (ID: `59b01b5a...`).
* Constante `DOMICILIO_ROSETI_ID` en `backend/clientes/constants.py`.
* `ClienteService._ensure_domicilio_rosa()` vincula automáticamente via `domicilios_clientes` al crear/actualizar cliente Rosa sin domicilios.
* Deprecación documentada: `cliente_id` legacy en `Domicilio` model.

### Commits
* `c2372d5a`: fixes pedidos C1/C3/C5 backend + C1-C5 frontend + isSinIVA Motor Bipolar.
* `bb5576c9`: IS_VIRGIN rename global + guard invertido + Roseti 1482 + isGeneric fix.
* `4010b655`: IS_VIRGIN rename `facturacion/constants.py` — cobertura global.

---

## SESIÓN 808: DOCTRINA VIRGINIDAD + ATOMICIDAD INGESTA + UX FIXES (OF)
**Fecha:** 2026-05-15
**Locación:** OF
**Objetivo:** Implementar Doctrina de Virginidad canónica. Fix UX PedidoCanvas. Fix Rosa AFIP bypass. Diagnosticar y corregir 409 ingesta. Atomicidad IngestaService.approve(). Sync D↔P.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash D: 513796bf | Hash P: 5865616

### Hito 1: FIX UX PedidoCanvas
* Botón "Guardar e Imprimir": `v-if="pedidosStore.ingestaData"` — oculto en flujo manual.
* `wasIngesta` capturado antes de `clearIngestaData()` para evitar bug de evaluación tardía.
* Post-guardado manual: reset de canvas (items, cliente, nroPedido, fechas, notas) + notificación "listo".
* Post-guardado ingesta: redirección a PedidoList (comportamiento anterior conservado).

### Hito 2: FIX Rosa / OPERATOR_OK bypass AFIP
* `esOperatorOk = !!(flags_estado & 16)` evaluado en `savePedido()`.
* Si activo: salta todo el bloque fiscal (sin borrador factura, sin remito puente).
* Muestra warning al operador: "Cliente sin circuito AFIP — emitir remito manual si corresponde."

### Hito 3: Doctrina de Virginidad — implementación canónica
* **Removidos triggers incorrectos:**
  - `clientes/service.py`: eliminada línea `~HAS_ACTIVITY` del bloque 4 pilares.
  - `remitos/service.py` (Vanguard Canon): `mutation_flags = current_flags | target_base` (preserva Bit 1).
* **Agregados triggers canónicos:**
  - `pedidos/router.py`: hook en PATCH — si `estado == "CUMPLIDO"` y Bit 1 activo → apagarlo.
  - `facturacion/service.py`: hook en `sellar_factura` — si `update_data.cae` → apagar Bit 1 del cliente.
* **Ghost pedido:** `remitos/service.py` línea ~532: `estado="PENDIENTE"` (era "CUMPLIDO").
* Commits: D `8e703914` / P `3690673` (cherry-pick con conflicto resuelto).

### Hito 4: Diagnóstico 409 ingesta
* Raw `80af6b8b` (Labme, 0001-00002535): `audit_status='RECIBIDO'` pero downstream ya existía.
* Causa raíz: commit parcial previo — `create_from_ingestion` comiteó, segundo commit de `approve()` nunca corrió.
* Reconciliación manual: `UPDATE ingesta_facturas_raw SET audit_status='PROCESADO'...` (PIN 1974).

### Hito 5: Atomicidad IngestaService.approve()
* Auditoría: 2 commits no atómicos con ventana de inconsistencia entre ellos.
* `remitos/service.py`: `db.commit()` → `db.flush()` en cierre principal y path `solo_actualizar_cliente`.
* `ingesta/service.py`: checkpoint `PROCESANDO` pre-vuelo, try/except con `ERROR` en fallo, único commit al final.
* `remitos/router.py`: `db.commit()` explícito en endpoint deprecated `POST /ingesta-process`.
* Commit: D `513796bf` / P `5865616`.

### Hito 6: Sync D↔P
* 4 cherry-picks a P en orden cronológico (807-808).
* Conflicto en `_GY/_MD/` (burocracia): destagiado.
* Conflicto en `clientes/service.py`: resuelto con versión D (IS_VIRGIN eliminado).
* Push P: `d3173b2..5865616`.

---

## SESIÓN 807: SILO DRIVE + PRICING ENGINE SOBERANO + PROTOCOLOS ALFA/OMEGA (OF)
**Fecha:** 2026-05-14
**Locación:** OF
**Objetivo:** Crear Silo Drive como centro de comando entre sesiones. Fix pricing engine 409. Actualizar protocolos ALFA y OMEGA en D y P. Sync DB 807d de MT a D.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash D: 0b34f1f9 | Hash P: d3173b2

### Hito 1: Silo Drive
* `Q:\Mi unidad\V5_Silo_Claude\` creado — README.md, INBOX.md, ESTADO_ECOSISTEMA.md, estructura OF/CA/GLOBAL/LEIDOS.
* Bug #1 OF/P resuelto y marcado RESUELTO en `OF/P/BUGS.md` del Drive.

### Hito 2: Protocolos ALFA y OMEGA
* `ALFA.md` D y P: PASO 0 — lectura INBOX + ESTADO_ECOSISTEMA antes de operar.
* `OMEGA.md` D: FASE 1B WAL checkpoint (`pilot_v5x.db`) + ESTADO_ECOSISTEMA en FASE 2.
* `OMEGA.md` P: ídem, con ruta `data\V5_LS_MASTER.db`.

### Hito 3: Fix Pricing Engine
* Causa raíz bug #1: `get_virtual_price()` abortaba con `PRODUCTO_SIN_COSTO` cuando `costos=None`.
* `pricing_engine.py`: sin_costo=True (no bloqueante) vs STRICT_MODE_VIOLATION (bloqueante real).
* `router.py`: 409 solo para STRICT_MODE_VIOLATION. Flag `sin_costo` expuesto en respuesta.
* Verificado en vivo: SKU 80018/80019 → HTTP 200, precio=0, sin_costo=True.
* Cherry-pick a P: hash `922da85`.

### Hito 4: DB y Deuda Técnica
* DB 807d instalada en D desde MT (1.974.272 bytes).
* Pedido 38 eliminado (Pao Tandil — ingresado incompleto, a recrear).
* 3 deudas técnicas registradas en DB: Badge FALTAN, Guardar e Imprimir, etiqueta botón por contexto.

---

## SESIÓN 806: ARLEQUÍN V2 — INFERENCIA ROSA + GENOMA_UNIVERSAL + FIX NO_FISCAL_FORCE (OF)
**Fecha:** 2026-05-13
**Locación:** OF
**Objetivo:** Sellado del GENOMA_UNIVERSAL, purga de herejía NO_FISCAL_FORCE, implementación completa Doctrina Arlequín V2, blindaje Consumidor Final y MOSTRADOR, sincronización D→P.
**Estado:** NOMINAL GOLD — PIN 1974 | Hash D: abd34332 | Hash P: 2d7c5c2

### Hito 1: Infraestructura MT (sesión 805/806 bridge)
*   Migración 033 schema sync P←D (facturas_remitos + bugs + tablas faltantes).
*   Python 3.11.9 restaurado en MT — venv reparado.
*   Flujo ingesta→pedido→remito operativo en MT.
*   DevBadge oculto en producción (import.meta.env.DEV).
*   Task Scheduler recreado en MT.

### Hito 2: GENOMA_UNIVERSAL sellado
*   `docs/GENOMA_UNIVERSAL.md` creado — mapa canónico 64-bit para Clientes, Productos, Pedidos, Facturas (RAW/PRC/Madre) y Remitos.
*   Auditoría forense Nike Arq 5.5: resolución de contradicciones entre sesiones 798, 800-OF, 800-CA y 806.
*   NO_FISCAL_FORCE corregido Bit10→Bit12 (herejía purgada): `constants.py`, `PedidoList.vue` (6 referencias), `router.py`.

### Hito 3: Doctrina Arlequín V2
*   Inferencia automática Rosa: `_audit_sovereignty()` enciende OPERATOR_OK (Bit4) si tiene segmento y sin CUIT real.
*   `clientValidation` en PedidoCanvas y `evaluateCliente` en useAuditSemaphore reescritos con lógica por bits.
*   Consumidor Final blindado: CUIT 00000000000 forzado GOLD_ARCA en `_audit_sovereignty()`.
*   CUIT 00000000000 declarado exclusivo MOSTRADOR/GENÉRICO — bloqueo HTTP 400 en create y update.

### Hito 4: Documentación y Cierre
*   `PROTOCOLO_EMERGENCIA_MT.md` creado — flujo canónico D→P→MT sellado.
*   7 ítems registrados en `deuda_tecnica` (sesión 806).
*   Cherry-pick 4 commits D→P: limpio, sin conflictos.
*   Push D y P a GitHub confirmado.
*   Canario OMEGA: LAVIMAR flags=13 — NOMINAL GOLD.

---

## SESIÓN 802: ESTABILIZACIÓN INFRAESTRUCTURA Y SOBERANÍA TOMY (OF)
**Fecha:** 2026-05-11
**Locación:** OF
**Objetivo:** Saneamiento integral de Producción (Tomy), normalización de rutas legacy, unificación de repositorio Git (P), eliminación de mock data en UI y formalización de protocolo OMEGA manual.
**Estado:** NOMINAL GOLD — PIN 1974

### Hito 1: Normalización de Infraestructura (P)
*   Renombramiento de raíz a `v5-ls-Tom` y saneamiento de rutas `C:/dev/V5-LS` en 28 archivos.
*   Actualización de archivos `.env` (raíz, current, staging) para apuntar a las bases de datos correctas.
*   Sincronización de paridad en Staging (P) con puertos y bases asignadas.

### Hito 2: Unificación Git Tomy
*   Merge exitoso de ramas divergentes en `v5-ls-Tom`.
*   Resolución de conflicto en `PedidoCanvas.vue` preservando lógica V5.7 GOLD (`checkout --ours`).
*   Limpieza de binarios (`.db`, `.pyc`) del índice de Git para asegurar un repositorio liviano.
*   Push exitoso a GitHub unificando entornos OF y CA.

### Hito 3: Saneamiento de Código y Deuda Técnica
*   Eliminación de mock data (historial/habituales) en `ClientCanvas.vue` en D y P.
*   Registro de deuda técnica en `pilot_v5x.db` para integración de API real.
*   Formalización de OMEGA manual en `ALFA.md`.

### Hito 4: Auditoría OMEGA V2.2
*   Canario D validado (LAVIMAR flags=13).
*   Generación de Informe Histórico y actualización de Genoma Documental.

---

## SESIÓN 801: DESPLIEGUE TOMY + DIAGNÓSTICO D VS P (CA)
**Fecha:** 2026-05-10
**Locación:** CA
**Objetivo:** Diagnóstico de paridad entre repositorios P y D, registro de deuda técnica en pilot_v5x.db, y creación de automatización ACTUALIZAR_V5.bat para instancia de Tomy.
**Estado:** NOMINAL GOLD — PIN 1974

### Hito 1: Diagnóstico de Repositorios (D vs P)
*   Confirmación de bicefalía de repositorios: P (`v5-ls-Tom`) y D (`Sonido_Liquido_V5`) operan sobre remotos distintos.
*   Hash P: `a7759c6` (OMEGA 796).
*   Hash D: `8027b685` (OMEGA 800).
*   Identificación de 10 commits pendientes de integración en P desde la rama principal de D.

### Hito 2: Automatización de Despliegue
*   Creación de `ACTUALIZAR_V5.bat` en la raíz para permitir updates autónomos via `git pull`.
*   Validación de entorno Git y manejo de errores de red/conflictos.

### Hito 3: Registro de Deuda Técnica
*   Actualización de tabla `deuda_tecnica` en `pilot_v5x.db`.
*   Inserción de 4 ítems: Deploy Tomy (Alta), Stock/Depósitos (Media), Precios PDF (Media), ABM Rubros (Baja).

### Hito 4: Burocracia OMEGA
*   Actualización de Caja Negra, Manuales e Informes Históricos.
*   Sincronización de `SESION_ACTUAL.md` a Mayo 2026.

---

**Fecha:** 2026-05-08
**Locación:** OF
**Objetivo:** Estandarizar numeración de remitos (0016-XXXXXXXX), finalizar Módulo Ingesta V2, implementar Conserje V2 auditoría READ ONLY, fix em dash en remito_engine, y habilitar live preview de numeración.
**Estado:** NOMINAL GOLD — Hash: 9e593e67

### Hito 1: Estandarización Sabueso V5.7
*   Consolidación del protocolo de numeración **0016-XXXXXXXX** en todos los flujos. Eliminación de regresiones a la serie 0015-.
*   `backend/remitos/pdf_parser.py`: Mejora en extracción de Punto de Venta y Número de Comprobante (insensible a espacios/guiones).
*   `backend/remitos/service.py`: Lógica de resolución jerárquica de `numero_legal` priorizando factura real sobre Pedido ID.

### Hito 2: Módulo Ingesta V2 + Conserje READ ONLY
*   Finalización de flujo `FacturasRaw` -> `FacturasProcesadas`.
*   Implementación de Conserje V2: motor de auditoría `READ ONLY` con scoring de domicilios y validación de identidades sellado por Nike Arq 5.5.
*   Protocolo Bit 22: Establecimiento de `PRE_MODULO_FACTURACION` (Flag 4227083) para vinculación fiscal espejo.

### Hito 3: Fixes UI/UX y Motor de PDF
*   `frontend/src/views/Pedidos/IngestaFacturaView.vue`: Habilitación de Live Preview del número de remito resultante para evitar errores de carga.
*   `remito_engine.py`: Fix em dash en header/footer (líneas 74 y 167) para asegurar estética doctrinal.

### Hito 4: Saneamiento y Cierre OMEGA 2.2
*   Purgado intencional de registros de prueba (LABME, Pedido 32) en base D.
*   Ejecución de Protocolo OMEGA completo con PIN 1974.

## SESIÓN 799: GENOMA FACTURAS + CONSERJE DUPLICADOS + MANUALES (CA)
**Fecha:** 2026-05-08
**Locación:** CA
**Objetivo:** Implementar Genoma `FacturaFlags` (mapa bits 0-21 sellado Nike Arq 5.5), campo `notas_auditoria` en modelo Factura, migración 029, conserje HTTP 409 `FACTURA_DUPLICADA` en ingesta-pdf, y Bug G (pedidos duplicados con modal advertencia).
**Estado:** NOMINAL GOLD — hashes: 93a9a3d4, 58404b1b

### Hito 1: `FacturaFlags` — Genoma constants.py
*   `backend/facturacion/constants.py` (nuevo): clase de constantes con mapa completo bits 0-21 de `flags_estado` en tabla `facturas`. Sellado Nike Arq 5.5. Bits: EXISTENCE(1), HAS_ACTIVITY(2), HAS_REMITO(4), ACTIVE(8), V15_STRUCT(1024), PASADO_A_PEDIDO(32768), EN_CUARENTENA(65536), TIENE_NC(131072), TIENE_ND(262144), ES_NC(524288), ES_ND(1048576), AUDITADA(2097152). Bits 22-29 reservados contabilidad. Bits 30+ ultra-reservados.

### Hito 2: Campo `notas_auditoria` + Migración 029
*   `backend/facturacion/models.py`: `notas_auditoria = Column(String, nullable=True)` agregado a clase `Factura`. Campo de texto libre para observaciones de auditoría manual — complementa bit `AUDITADA` (bit 21).
*   `scripts/migrate_029_facturas_notas_auditoria.py` (nuevo): `ALTER TABLE facturas ADD COLUMN notas_auditoria VARCHAR`. Idempotente, registra en `_migraciones_aplicadas`. Ejecutada en pilot_v5x.db.

### Hito 3: Conserje FACTURA_DUPLICADA en ingesta-pdf
*   `backend/remitos/router.py` — `POST /remitos/ingesta-pdf`: guard pre-proceso. Consulta `facturas` por `punto_venta + numero_comprobante`. Si existe → HTTP 409 `{"codigo": "FACTURA_DUPLICADA", "factura_id": "<uuid>"}`. El frontend puede redirigir al registro existente. Hash: 93a9a3d4.

### Hito 4: Bug G — Pedidos duplicados
*   Modal de advertencia al detectar posible pedido duplicado (mismo cliente + fecha + ítems similares). Operador puede continuar o cancelar. Hash: 58404b1b.

---

## SESIÓN 798: BUGS D/E/F/H + EXTRACCIÓN INGESTAITEMMODAL (OF)
**Fecha:** 2026-05-07
**Locación:** OF
**Objetivo:** Cerrar Bugs D/E/F (F4 satélite en PedidoCanvas), extraer IngestaItemModal a componente propio, implementar Fix H (F4 funcional dentro del modal) y botón copy descripción.
**Estado:** NOMINAL GOLD — hashes: db72e856, afd5cd74

### Hito 1: Bugs D/E/F — F4 satélite PedidoCanvas
*   `PedidoCanvas.vue`: nombre único `AltaProducto_${Date.now()}` — fuerza ventana nueva, no reutiliza tab bloqueado.
*   `ProductosView.vue`: `v-if="route.query.mode !== 'satellite' || showInspector"` en `<main>` — bloquea F4 handler hasta que inspector esté listo.
*   `ProductoInspector.vue`: `fetchRubros()` defensivo en `onMounted` cuando store vacío (modo satellite omite App.vue boot). Hash: db72e856.

### Hito 2: Extracción IngestaItemModal.vue + Fix H + botón copy
*   `Ventas/components/IngestaItemModal.vue` (nuevo, 110 líneas): modal de resolución de ítems extraído de PedidoCanvas. Props: `items`. Emits: `resolved(items)`, `cancel`.
*   Fix H: `handleOverlayKeydown` captura F4 internamente, abre satélite de alta producto — burbujeo detenido antes de llegar a PedidoCanvas.
*   Botón copy `fa-copy` junto a descripción de factura → llena `searchTerm` con un click.
*   `PedidoCanvas.vue` −137 líneas neto: 6 refs → 2, 5 funciones → 3, guard `showIngestaModal` en F4. Hash: afd5cd74.

---

## SESIÓN 797: BUG C BACKEND + SISTEMA DE MIGRACIONES (CA)
**Fecha:** 2026-05-06
**Locación:** CA
**Objetivo:** Resolver Bug C — flujo pedido→factura→remito incompleto. Auditoría forense del backend: 7 bugs críticos identificados (B-1 a B-7). Implementación modelo N:M `FacturaRemito` + sistema de control de migraciones idempotente. Bug B (modal 409) también resuelto.
**Estado:** NOMINAL GOLD — ver informe: `INFORMES_HISTORICOS/2026-05-06_BUG_C_BACKEND_MIGRACIONES_CA.md`
**Hash:** 529aa2be

### Hito 1: Bug B — ESC no restaura modal 409
*   `frontend/src/stores/pedidos.js`: `pending409Context` + `set409Context`/`clear409Context` — canal separado que PedidoCanvas nunca toca.
*   `IngestaFacturaView.vue`: `goToNewPedido()` persiste contexto antes de navegar; `onMounted()` lo restaura y reactiva `show409Modal`. Hash: `9df14bdf`.

### Hito 2: Fix B-1 — `factura_id: int` → `str`
*   `backend/remitos/router.py:261` y `service.py:586`: parámetro `int` → `str` + `_uuid.UUID(factura_id)` en query. Endpoint era completamente inoperativo — FastAPI rechazaba el UUID antes de llegar al service.

### Hito 3: Fix B-2 — `fecha_vto_cae` → `cae_vencimiento`
*   `backend/remitos/service.py:606,634`: campo inexistente corregido al campo real. Crash `AttributeError` en ambas ramas.

### Hito 4: Fix B-3 — `numero_legal` con doctrina ARCA real
*   Helper `_numero_legal_arca()`: con CAE → `0016-XXXX-YYYYYYYY`; sin CAE (borrador) → `0015-XXXXXXXX` (serie manual, doctrina Nike). Antes usaba `pedido.id` o UUID del remito — violación directa de doctrina.

### Hito 5: Fix B-7 + B-6 — campos silenciosos
*   `total_bruto` → `factura.total` (valor_declarado siempre era 0.0).
*   `cuit_comprador` ahora se asigna post-flush en `create_draft_from_pedido` — sello histórico faltante corregido.

### Hito 6: Arquitectura N:M `FacturaRemito`
*   `backend/facturacion/models.py`: `Table` simple → clase `FacturaRemito` completa con GUID, `fecha_vinculo`, `flags_estado`, relaciones bidireccionales (string anti-deadlock).
*   `Factura.remitos` → `Factura.vinculos_remitos` (cascade `all, delete-orphan`).
*   `backend/remitos/models.py`: `Remito.vinculos_facturas` agregado.
*   Integración en `create_puente_factura`: guard de idempotencia + helper `_vincular_factura_remito()`.
*   Migración 026: `DROP/CREATE TABLE facturas_remitos` con id GUID + fecha_vinculo + flags_estado + UNIQUE(factura_id, remito_id).

### Hito 7: Sistema de control de migraciones
*   `scripts/migrate_000_control_migraciones.py`: crea tabla `_migraciones_aplicadas` (id, nro_sesion, aplicada_en). Patrón idempotente documentado.
*   `migrate_026_factura_remitos.py` refactorizado: verifica antes de ejecutar → SKIP si ya aplicada. Hash: `529aa2be`.

**Pendiente:** Bug C ítem 13 — `savePedido()` en PedidoCanvas no invoca cadena factura→remito (D-7, sesión futura). Build P pendiente OF.

---

## SESIÓN 796: PARSER Y-AXIS FIX + MODAL SYNC CA — INGESTA PDF ITEMS RESUELTO
**Fecha:** 2026-05-05
**Locación:** CA
**Objetivo:** Resolver causa raíz de items[] vacío en flujo PDF→modal PedidoCanvas. Fix Y-axis tolerance `/4`→`/6` en pdf_parser.py. Sync D↔P. Canario actualizado TARGET_FLAGS 8205→13.
**Estado:** NOMINAL GOLD — ver informe: `INFORMES_HISTORICOS/2026-05-05_INGESTA_PARSER_FIX_MODAL_SYNC_CA.md`

### Hito 1: Fix Y-Axis Tolerance (CRÍTICO)
*   `pdf_parser.py` línea 137: `round(y0/4)*4` → `round(y0/6)*6`. Tolerancia ±2pts insuficiente para PDFs AFIP (delta real: 5pts entre qty y u_medida). Items array no-vacío confirmado. Caso: L EPI S.R.L. — Alcohol 70% — qty=4,00 precio=$13.500,00.

### Hito 2: Fix Typo Producto
*   `pilot_v5x.db` ID 150 SKU 10211: "Acohol" → "Alcohol". Search modal OK.

### Hito 3: Canario v2.py — Actualización Post-Saneamiento
*   `TARGET_FLAGS = 8205` → `TARGET_FLAGS = 13` en D y Tom. Canario reportaba DESVÍO CRÍTICO con flags=13 por no haber sido actualizado tras saneamiento 2026-05-02 (bit 8192 eliminado). INTEGRITY NOMINAL GOLD confirmado en ambos.

### Hito 4: Null-checks + Sync + Addendum OF
*   Commit 7b5794d: null-checks router.py Tom. Commit 534178b: PedidoCanvas sync. Commit 8c658f63: bitácora addendum OF.

**Bugs backlog:** Bug A (search pisa ref), Bug B (ESC modal 409), Bug C (ciclo pedido→factura→remito), Clientes azules. Build P pendiente OF.

---

## SESIÓN 795: MODAL RESOLUCIÓN ÍTEMS — UX + VISUAL (OF)
**Fecha:** 2026-05-05
**Locación:** OF
**Objetivo:** Fix visual y UX del modal de resolución de ítems en PedidoCanvas. Diagnóstico inicial de items[] vacío.
**Estado:** NOMINAL — ver informe completo: `INFORMES_HISTORICOS/2026-05-05_MODAL_INGESTA_ITEMS_UX_OF.md`
**Hash:** 296a120e

---

## SESIÓN 794: ARLEQUÍN V2 MERGE QUIRÚRGICO CA + DOCTRINA BIT 1 RESUELTA
**Fecha:** 2026-05-04
**Objetivo:** Merge de feature/arleq-v2-productos en D. Resolución definitiva Bit 1 Clientes/Productos. OMEGA V2.2 desplegado en D y P.
**Estado:** NOMINAL GOLD — ver informe completo: `INFORMES_HISTORICOS/2026-05-04_ARLEQ_V2_MERGE_QUIRURGICO_CA.md`

---

## SESIÓN 793: SIEMBRA DE CONTACTOS + SOBERANÍA LOCAL (PURGA POSTGRESQL)
**Fecha:** 2026-04-19
**Objetivo:** Importación masiva de contactos (Person-Centric) y eliminación total de dependencias a base de datos externa.

### Hito 1: Purga PostgreSQL — Soberanía Total
*   **Raíz del problema**: Variable de entorno de sistema Windows `DATABASE_URL=postgresql://...34.95.172.190` pisaba todo el stack. Toda sesión de scripts apuntaba a la nube sin importar .env.
*   **Capas eliminadas**: (1) variable de sistema Windows (`SetEnvironmentVariable null`), (2) `backend/.env` reescrito a SQLite, (3) `backend/.env.bak` y `.env.postgres_fail` eliminados.
*   **Defensa instalada**: `import_contactos_bulk.py` carga `.env` local y rechaza cualquier URL postgres antes de inicializar ORM.

### Hito 2: Reparación de Mappers SQLAlchemy
*   `backend/clientes/models.py`: imports explícitos de `EmpresaTransporte` y `Pedido` → eliminados `InvalidRequestError` en cadena.
*   `backend/pedidos/models.py`: import explícito de `Producto` → resuelto mapper de `PedidoItem`.
*   `backend/contactos/models.py`: campo `notas_sistema` (Text, nullable) → segregación notas script vs notas usuario.
*   SQLite: `ALTER TABLE personas ADD COLUMN notas_sistema TEXT DEFAULT NULL`.

### Hito 3: Siembra de Contactos Person-Centric
*   Script `import_contactos_bulk.py` ejecutado sobre `contactos_siembra_gmail_20260419_01.json` (10 registros).
*   Resultado: 10 personas nuevas, 7 vínculos comerciales, 3 `[ENTIDAD_PENDIENTE]` (Rizobacter).
*   Genoma: Bit 5 (CANTERA_NIKE=16) en todos. Bit 6 (VINCULO_DUDOSO=32) en 5 fuzzy 70-98%.
*   `notas_sistema` auditadas por registro: origen, % fuzzy, cargo, entidad pendiente.

### Hito 4: Limpieza de Lastre
*   Eliminados: `ingest_memory.py`, `config.py`, `backend/data/*.txt`, `atenea_memory.db` — todos dependían de Google Cloud.

**Estado:** NOMINAL GOLD. Protocolo Omega ejecutado. PIN 1974.

---

## SESIÓN 792: SANEAMIENTO REMITOS (RAR-V1) + RESILIENCIA DE IDENTIDAD (V5-LS)
**Fecha:** 2026-04-16
**Objetivo:** Estabilizar motor de remitos, corregir el bug de reversión de CUIT y eliminar Error 500 en auditoría de domicilios. Paridad total D/P.

### Hito 1: Saneamiento Remitos (RAR-V1)
*   **Flexibilidad**: Campos `bultos` y `valor_declarado` ahora son Nullable (Base y Schema).
*   **PDF Engine**: Etiquetas fijas ("BULTOS:", "VALOR DECL.:") con impresión condicional de valores. QR oficial: `https://liquid-sound.com.ar/`.
*   **Datoscopio**: Implementación de `@property resumen` en modelo `Domicilio` para visualización unificada de direcciones en remitos legales.

### Hito 2: Resiliencia de Identidad (V5-LS)
*   **Soberanía CUIT**: Tras validación ARCA, el CUIT corregido sobreescribe reactivamente el dato de Cantera en el frontend (`ClientCanvas.vue`). Erradicado el bug de reversión a datos legacy.
*   **Error 500 Audit**: Null-safety en `_audit_sovereignty` de `service.py`. Ya no falla ante clientes con Condición IVA incompleta.
*   **Error 422**: Manejo robusto de IDs de domicilio malformados (`null`), redirigiendo a `POST` cuando es necesario.

### Hito 3: Homologación P/D (Omega Sync)
*   Sincronización total de módulos hacia `C:\dev\V5-LS\current`.
*   Paridad absoluta de lógicas de negocio y blindaje de identidad.

**Estado:** NOMINAL GOLD. Protocolo Omega ejecutado. PIN 1974.

---

## SESIÓN 791: PRODUCCIÓN SOBERANA — FIXES OPERATIVOS + DISEÑO DOCTRINAL
**Fecha:** 2026-04-15
**Objetivo:** Corregir bugs detectados en tiempo real por Tomy en producción (D/V5-LS). Sync completo a P.

### Hito 1: Fix Triple — Domicilios 500
* Bug A: `is_maps_manual` duplicate kwarg en `create_domicilio` → `TypeError` → 500.
* Bug B: `domicilios_clientes` junction table no insertada → domicilio invisible en GET.
* Bug C: Pinia store `createDomicilio` reemplazaba cliente con domicilio → loop navegación.

### Hito 2: Fix Crítico — PedidoCanvas Edit Mode
* `savePedido()` siempre usaba POST. Ahora: si `route.params.id` → PATCH. El endpoint ya existía.
* Limpieza manual DB: 5 pedidos duplicados eliminados (dos pasadas). Próximo pedido: #20.

### Hito 3: Fix Rosa Clients
* `clienteEsVerde` ahora detecta Rosa (`flags_estado & 15 in [9,11]`) y devuelve `true` sin validar CUIT/domicilio.

### Hito 4: Migración GENERAL → General
* D: 4 productos. P: 7 productos. GENERAL (id=28) dado de baja en ambas DBs.

### Hito 5: Fix PedidoInspector — Nota visible
* Botón editar nota siempre visible (eliminado `opacity-0 group-hover`).

### Hito 6: Diseño Doctrinal — Orígenes de Pedido
* Acordado: bits libres de `flags_estado` para `BIT_ORIGEN_FACTURA` y `BIT_ORIGEN_REMITO`.
* Implementación pendiente próxima sesión.

**Estado:** NOMINAL GOLD. Build D ejecutado (6.91s). Commits y push D y P.

---

## SESIÓN 790: SANEAMIENTO DB + FIXES OPERATIVOS + PARIDAD D/P
**Fecha:** 2026-04-14
**Objetivo:** Sanear pilot_v5x.db (paridad con P), fixes de cantera import, F4, Rubro obligatorio e infraestructura.

### Hito 1: Cirugía DB pilot_v5x.db (PIN 1974)
*   7 fusiones de grupos duplicados. Pedidos de 173 y 159 re-apuntados a survivors 177 y 175.
*   IDs 158, 159, 160 (NULL SKU) eliminados físicamente.
*   8 productos borrados (flags=0/2, sin movimientos). Total final: 23 productos.

### Hito 2: Cantera Import — Fix 500 + Auto-SKU
*   `flags_estado=3` en creación desde cantera (ACTIVE+VIRGIN).
*   Auto-SKU: `MAX(sku)+1` con piso 9001 cuando el mirror no trae SKU.
*   SKU como `int(float(...))` — compatible con mirror JSON que puede traer floats.
*   `margen_mayorista` → `rentabilidad_target` (campo renombrado en modelo).
*   Paridad D/P: mismo fix aplicado en ambos entornos.

### Hito 3: Fixes Frontend
*   F4 en PedidoCanvas: product search tiene prioridad; modal cliente solo en foco explícito.
*   ProductoInspector: asterisco rojo + ring de error + mensaje `rubroError` para campo Rubro.

### Hito 4: Infraestructura
*   DESPERTAR.ps1: guard null reference sin .bak / Git no disponible.
*   boot_system.py: `--reload-dir backend` + health check polling.
*   main.py: `/` → `/health` en D y P — libera catch-all SPA.

**Estado:** NOMINAL GOLD. Commit OMEGA ejecutado.

---

# [V5.7.0] 2026-04-09 - Homologación Identity Shield (Bag of Words)
> **ESTADO:** SATISFACTORIO (NOMINAL GOLD)
> **TIPO:** HOMOLOGACIÓN / SEGURIDAD / SYNC P-D

**Hitos:**
1. **Homologación Genoma V5-LS:** Sincronización total del blindaje "Bag of Words" hacia entorno Staging.
2. **Backfill Productivo:** Inyección de `razon_social_canon` en `V5_LS_STAGING.db` y normalización de 35 registros legítimos.
3. **Sensor UI:** Activación de detector de duplicados reactivo debounced en `ClientCanvas.vue`.
4. **Dictamen de Auditoría:** Certificado `audit_production_duplicates.py` limpio.

**Archivos:** `backend/clientes/service.py` | `router.py` | `frontend/src/views/Hawe/ClientCanvas.vue` | `_GY/_MD/CAJA_NEGRA.md`

---

# [V16.2.0] 2026-04-08 - Blindaje Nuclear de Identidad (BOW Protocol)
> **ESTADO:** SATISFACTORIO (NOMINAL GOLD)
> **TIPO:** SEGURIDAD / IDENTIDAD / HOMOLOGACIÓN

**Hitos:**
1. **Protocolo Bag of Words (BOW):** Implementación de `normalize_name` V16.2. La identidad ahora es insensible al orden de las palabras ("Inapyr SRL" == "SRL Inapyr").
2. **Hémetización Estructural (Homologación):** Sincronización total entre entornos D (`Sonido_Liquido_V5`) y P (`V5-LS`). Inyección de columna `razon_social_canon` en la DB maestra.
3. **Saneamiento Quirúrgico:** Eliminación física de registros duplicados en pedidos (ID 6 y 7) y reseteo de secuencia SQLite en producción.
4. **Sensor de Identidad UI:** Integración de alertas de colisión semántica en tiempo real en `ClientCanvas.vue`.

**Archivos:** `backend/clientes/service.py` | `router.py` | `ClientCanvas.vue` | `V5_LS_MASTER.db`

---

# [V15.2.1] 2026-03-23 - Soberanía Hub & Unificación de Registro
> **ESTADO:** SATISFACTORIO (NOMINAL GOLD)
> **TIPO:** FEATURE / REFACTOR / DATA MIGRATION

**Hitos:**
1. **Soberanía del Hub:** Implementada la siembra del Address Hub mediante `seed_hub.py`. Se migraron 47 domicilios legacy a 43 registros únicos en el Hub Soberano con deduplicación semántica.
2. **Bit 21 (Espejo):** Activación del bit 2097152 para todos los vínculos migrados, garantizando paridad con datos históricos de Clientes.
3. **Unificación de Registro:** Eliminada la "Bicefalía de Registros" unificando todas las importaciones de `Base` a `backend.core.database`.
4. **Resiliencia de API:** Fix en `DomicilioResponse` para soportar `cliente_id` opcional y repoblación quirúrgica del registry en `service.py`.

**Archivos:** `backend/main.py` | `backend/clientes/models.py` | `schemas.py` | `service.py` | `router.py` | `backend/pedidos/models.py`

---

# [V15.2.0] 2026-03-20 - Restauración Logística & Protocolo ALFA V5.2
> **ESTADO:** SATISFACTORIO (CON DEUDA)
> **TIPO:** FEATURE / PROTOCOLO / BUGFIX

**Hitos:**
1. **Edición de Remitos (Doble Clic):** Restaurada la capacidad de editar cabeceras de remitos (`BORRADOR`) desde el listado. Implementado endpoint `PATCH /remitos/{id}` y modal reactivo.
2. **Soberanía ALFA (Fix ORM):** Reparada inconsistencia en el Mapper de Pedidos que bloqueaba `verify_sovereignty.py`.
3. **Sincronización de Bits:** Sergio Jofre (Genoma) sincronizado satisfactoriamente con Bit 19 activo (Valor final: 524301).
4. **Deuda Técnica (Bit 3):** Sesión marcada con Bit 3 CRÍTICO debido a que la edición de remitos no incluye bultos, valor declarado ni edición de ítems (Cuerpo).

**Archivos:** `RemitoListView.vue` | `backend/remitos/service.py` | `router.py` | `schemas.py` | `verify_sovereignty.py`

---

# [V15.1.4] 2026-03-19 - Logística Táctica & Edición de Ingesta
> **ESTADO:** SATISFACTORIO
> **TIPO:** FEATURE / UX / LOGÍSTICA

**Hitos:**
1. **Remito Manual (0015):** Implementada infraestructura para remitos sin factura (Serie 0015-00003001+) con "Ghost Pedidos".
2. **Edición de Ingesta:** Refactorizada la pre-carga de PDF a Grilla Editable (Inputs tactical). Permite corregir OCR, agregar y quitar ítems.
3. **Fix Reactividad Domicilios:** Solucionado bug de carga diferida de direcciones en el selector mediante `watch` de Pinia.
4. **Fix Proxy PDF:** Ajustadas rutas relativas para descarga de remitos en red local.

**Archivos:** `ManualRemitoView.vue` | `IngestaFacturaView.vue` | `RemitosService.py` | `remitos/router.py`

---

# [V14.8.4] 2026-03-18 - Soberania Operativa & Correcciones Hawe
> **ESTADO:** SATISFACTORIO
> **TIPO:** FEATURE / BUGFIX / ARQUITECTURA

**Hitos:**
1. **Fix FK provincia_id:** Eliminado `'X'` en ClientCanvas.vue L1437. Causaba Error 400 (violacion FK tabla provincias) al crear clientes desde modal.
2. **Fix KEEP_OLD:** `snapshotEntrega` en DomicilioSplitCanvas.vue. resolveSync usa snapshot inmutable en lugar de props.domicilio (reactivo/potencialmente mutado).
3. **Lupa No Destructiva:** confirm() en consultarAfip antes de sobreescribir direccion fiscal manual con dato de ARCA.
4. **Color por Soberania:** getClientColorMode simplificado. Blanco = Bit 20 OFF. Sin dependencia de estado_arca.
5. **Soberania V14.8.4 (PIN 1974):** Promocion automatica al Nivel 13 (15->13) al guardar con 4 Pilares (razon_social + lista + segmento + domicilio_fiscal.calle). Bit 1 OFF + Bit 20 OFF. Escudo doble Frontend + Backend.

**Archivos:** `ClientCanvas.vue` | `DomicilioSplitCanvas.vue` | `HaweView.vue` | `backend/clientes/service.py`

---

# [V14.8.1] 2026-03-17 - Protección Genoma & Rescate COALIX

> **ESTADO:** SATISFACTORIO
> **TIPO:** RECUPERACIÓN / SEGURIDAD CRÍTICA

**Hitos de la Sesión:**
1. **Recuperación COALIX:** Extracción y restauración total de COALIX SA desde backup SQLite (1). Recuperados domicilios, personas y vínculos.
2. **Papelera Global (V14.8):** Implementación de respaldos JSON en `papelera_registros` para toda eliminación física en Utilidades Maestras.
3. **Blindaje Genoma:** Bloqueo de borrado físico para registros históricos (Bit 1 = 0). Implementación de "Grisado" visual y estatus "PROTEGIDO" en el frontend.
4. **Fix Serialización:** Implementación de limpiador recursivo para tipos `Decimal` y `UUID` en el motor de papelera.
5. **Configuración:** Resolución definitiva de conflicto de puertos (Bind 8080) para operación estable en LAN.

---

# [V14.8] 2026-03-16 - Saneamiento Genoma & Expansión LAN

# [V6.5.1] 2026-02-28 - Sesión 787: Protocolo Omega - Ingesta Consolidada
> **ESTADO:** SATISFACTORIO
> **TIPO:** INTEGRACIÓN / SINTONÍA FINA

Se completó la migración del ABM de Clientes de Ingesta al nuevo `ClientCanvas` universal. Se resolvieron los bloqueos del motor PDF y la interferencia de variables de entorno globales (Postgres Ghost).

**Hitos Técnicos:**
1. **Frontend:** Relajación de validaciones para Ingesta y Auto-Inyección de Domicilio PDF.
2. **Backend:** Implementación de Endpoint `/despachar`, instalación de `fpdf2`, y parche de Pydantic para `AttributeError`.
3. **Parsing:** Regex optimizado para facturas AFIP con formato espacial laxo.

---

# [RECUPERACIÃ“N] 2026-01-14 - Parche de Emergencia "Math Guard Clauses"

> **ESTADO:** SATISFACTORIO
> **TIPO:** HOTFIX / SEGURIDAD

Se detectÃ³ y documentÃ³ retroactivamente el parche de emergencia 'Math Guard Clauses' tras un colapso por Error 500 (DivisiÃ³n por cero).

**Detalles TÃ©cnicos:**
1.  **Backend:** Se blindaron `pricing_engine.py` y `router.py` (funciÃ³n `calculate_prices`) para capturar valores `None` o `0` en `precio_roca` y `costo_reposicion`.
2.  **Resultado:** El sistema devuelve `0.00` en todos los precios calculados en lugar de crashear, permitiendo que el listado de productos cargue incluso con datos corruptos.
3.  **Schemas:** Ajustados `schemas.py` para permitir `0.00` y `Optional` en campos de precios.

**AcciÃ³n Requerida:** Revisar datos de origen para corregir ceros, pero el sistema ya es estable.

# [V5.4] 2026-01-15 - ImplementaciÃ³n Multi-Proveedor y Ajustes UI

> **ESTADO:** BLOQUEADO (FRONTEND CRASH)
> **TIPO:** FEATURE / REFINEMENT

**Objetivo:** Implementar "Es Insumo", Selector IVA en Panel Central, y Tabla Multi-Proveedor.

**Avances:**
1.  **Backend (Completado):**
    *   Schema: Creada tabla `productos_proveedores`.
    *   Models: Actualizado `Producto` y creado `ProductoProveedor`.
    *   Router: Agregados endpoints `POST /proveedores` y `DELETE /proveedores/{id}`.
2.  **Frontend (Parcial):**
    *   Implementado layout y lÃ³gica en `ProductoInspector.vue`.
    *   Agregado servicio en `productosApi.js`.

**Incidente Bloqueante:**
*   El componente `ProductoInspector.vue` crashea al intentar abrirse (spinner infinito o error Vue).
*   **Causa RaÃ­z Identificada:** InicializaciÃ³n de arrays en Store (`tasasIva`, `proveedores`) puede ser `null/undefined` en el momento que el `watch(immediate: true)` dispara la lÃ³gica.
*   **Estado:** Se aplicaron parches de seguridad (`?.` y `|| []`), pero el error persiste. Se requiere revisiÃ³n profunda del ciclo de vida del componente.

**PrÃ³ximos Pasos (Protocolo Omega):**
1.  Debuggear inicio de `ProductoInspector` (Store vs Props).
2.  Verificar persistencia de "Es Insumo".
3.
# [V5.6.1] 2026-01-16 - ReparaciÃ³n Integral Pedidos (Orders Bridge)

> **ESTADO:** ESTABLE
> **TIPO:** HOTFIX / UX RECOVERY

**Objetivo:** Restaurar funcionalidad crÃ­tica de Pedidos, ImportaciÃ³n y Alta de Productos, bloqueada por errores de integraciÃ³n y UX "rota".

**Intervenciones:**
1.  **Backend (Bridge):** Corregido `router.py` para devolver JSON completo y defaults en importaciÃ³n (`500 Internal Error` Solucionado).
2.  **Frontend (GridLoader):**
    *   **Layout:** Cambiado inspector a `max-w-7xl` (Modal Central) para corregir visualizaciÃ³n "aplastada".
    *   **Integridad:** Implementada captura de hora local en payload de pedidos.
    *   **Seguridad:** Implementado **Guard Clause** (`isSubmitting`) en F10/Click para evitar pedidos duplicados.
3.  **Frontend (ProductoInspector):**
    *   **Rubros:** Implementado `SelectorCreatable` + `handleCreateRubro` + `fetchRubros` para ABM dinÃ¡mico en el alta.

**MÃ©tricas Finales:**
*   Alta de Productos: OK (Full Screen)
*   Integridad Pedidos: OK (No Duplicados, Hora Correcta)

# [V5.6.2] 2026-01-16 - Blindaje Modal Segmentos (UX)

> **ESTADO:** DEPLOYED
> **TIPO:** HOTFIX / UX

**Objetivo:** Solucionar "freezing" y duplicados al crear Rubros/Segmentos en Alta de Clientes.

**Intervenciones:**
1.  **Frontend (SimpleAbmModal):** Implementado soporte para `isLoading` (Spinner + Bloqueo de UI).
2.  **Frontend (ClienteInspector):**
    *   Integrado `abmLoading` para feedback visual inmediato.
    *   **ValidaciÃ³n:** Pre-check de duplicados (Case Insensitive) antes de llamar al backend.
    *   **Feedback:** Cierre automÃ¡tico del modal `showAbm = false` tras Ã©xito.

**Resultado:** Eliminada la posibilidad de crear duplicados por doble click y restaurado el feedback visual.

# [V5.6.3] 2026-01-16 - SincronizaciÃ³n Store Domicilios

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA CONSISTENCY

**Objetivo:** Corregir "Ficha Incompleta" persistente tras agregar Domicilio Fiscal.

**DiagnÃ³stico:**
*   El Store `createDomicilio` y `updateDomicilio` devolvÃ­a el cliente actualizado al caller (Inspector) pero **NO actualizaba** el array principal `clientes` en memoria.
*   Consecuencia: La vista principal (detrÃ¡s del inspector) quedaba con datos viejos hasta recargar.

**Intervenciones:**
1.  **Store (clientes.js):**
    *   `createDomicilio/updateDomicilio`: Implementada actualizaciÃ³n reactiva `this.clientes[index] = response.data`.
    *   `deleteDomicilio`: Agregado `fetchClienteById` automÃ¡tico tras eliminaciÃ³n (Backend devuelve 204).

**Resultado:** Al guardar un domicilio, la ficha del cliente se actualiza instantÃ¡neamente en todas las vistas.

# [V5.6.4] 2026-01-16 - AutonomÃ­a de Guardado Cliente

> **ESTADO:** DEPLOYED
> **TIPO:** CRITICAL FIX / ARCHITECTURE

**Objetivo:** Solucionar pÃ©rdida de datos al editar clientes desde el Cargador de Pedidos.

**DiagnÃ³stico:**
*   El componente `ClienteInspector` delegaba el guardado al padre (`emit('save')`) pero **NO llamaba a la API**.
*   El padre `PedidoTacticoView.vue` **NO escuchaba** el evento save, provocando que los cambios visuales del inspector se perdieran al cerrar el modal.
*   Resultado: El usuario veÃ­a los cambios en el popup, pero nunca persistÃ­an en la base de datos.

**Intervenciones:**
1.  **Backend/Store:** (Sin cambios, ya funcionales).
2.  **Frontend (`ClienteInspector.vue`):**
    *   **Refactor:** Implementada llamada directa a `clienteStore.createCliente` y `clienteStore.updateCliente` dentro de la funciÃ³n `save()`.
    *   **Beneficio:** El componente ahora es autÃ³nomo y garantiza la persistencia independientemente de quiÃ©n lo invoque (Pedidos, Clientes, etc.).

**Resultado:** La ediciÃ³n de clientes (Nombre, CUIT) ahora persiste correctamente en la base de datos y se refleja al cerrar el inspector.

# [V5.6.5] 2026-01-16 - AutonomÃ­a de Guardado Producto

> **ESTADO:** DEPLOYED
> **TIPO:** REFACTOR / ARCHITECTURE

**Objetivo:** Alinear inspector de productos con la arquitectura de "Componente AutÃ³nomo" (Self-Saving).

**ImplementaciÃ³n:**
*   Se replicÃ³ la lÃ³gica de `ClienteInspector` en `ProductoInspector.vue`.
*   Ahora el inspector de productos llama directamente a `productosStore.createProducto` o `updateProducto`.
*   Esto habilita su uso seguro desde el Cargador TÃ¡ctico sin duplicar lÃ³gica de guardado.

**Resultado:** Arquitectura unificada para ABMs complejos incrustados.

# [V5.6.6] 2026-01-16 - SincronizaciÃ³n TÃ¡ctica de Estado

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA COHERENCE

**Objetivo:** Resolver el problema "Pedidos no se entera" tras editar Cliente.

**DiagnÃ³stico:**
*   Aunque el Inspector guardaba y actualizaba el Store correctamente (V5.6.4), el componente `PedidoTacticoView` ejecutaba un `fetchClientes()` al cerrar el modal.
*   Este `fetch` recargaba la lista "Resumida" del backend (sin array de domicilios completo), sobrescribiendo la versiÃ³n "Detallada" que acababa de dejar el Inspector en memoria.
*   Resultado: Se perdÃ­a el estado verde de validaciÃ³n porque faltaban datos en el objeto cliente recargado.

**Intervenciones:**
1.  **PedidoTacticoView.vue:**
    *   Eliminada la llamada redundante `await clientesStore.fetchClientes()` en `onInspectorClose`.
    *   Implementado listener `@save` para capturar el resultado del inspector y asegurar la selecciÃ³n inmediata del ID actualizado/creado.

**Resultado:** La vista de Pedidos refleja instantÃ¡neamente los cambios (Nombre, Estado fiscal) sin parpadeos ni reversiones a datos viejos.

# [V5.6.7] 2026-01-16 - Reactividad Robusta en Store Clientes

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / CORE

**Objetivo:** Garantizar que la UI reaccione a cambios en objetos profundos dentro del array de clientes.

**Problema:**
*   La asignaciÃ³n directa por Ã­ndice (`this.clientes[i] = data`) a veces no disparaba la reactividad en componentes computed complejos (como `clienteSeleccionado` en Pedidos) debido a limitaciones de detecciÃ³n de cambios en arrays grandes o proxies.

**SoluciÃ³n:**
*   Se reemplazÃ³ la asignaciÃ³n directa por `this.clientes.splice(index, 1, response.data)` en el Store de Clientes (`updateCliente`, `createDomicilio`, `updateDomicilio`).
*   Esto fuerza al motor de reactividad de Vue a reconocer la mutaciÃ³n del array y propagar el cambio a todas las vistas suscritas.

**Resultado:** ActualizaciÃ³n visual infalible tras ediciÃ³n.

# [V5.6.8] 2026-01-16 - BÃºsqueda Global de Clientes (Cantera)

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / BACKEND

**Objetivo:** Permitir buscar clientes fuera del lÃ­mite inicial de 1000 registros.

**Problema:**
*   La bÃºsqueda en el TÃ¡ctico ("F3") solo filtraba el array local de 1000 clientes precargados. Clientes activos fuera de este lote (ej. clÃ­nicas especÃ­ficas) no aparecÃ­an aunque existieran en DB.

**SoluciÃ³n:**
*   **Backend:** Se implementÃ³ filtrado `q` (Query) en el endpoint `GET /clientes` con bÃºsqueda `ILIKE` en RazÃ³n Social, FantasÃ­a y CUIT.
*   **Frontend:** El componente `ClientLookup.vue` ahora dispara la bÃºsqueda al servidor (con debounce de 300ms) al tipear.
*   Esto actualiza dinÃ¡micamente el Store con los resultados coincidentes de toda la base de datos ("La Cantera").

**Resultado:** Al tipear "Bio", ahora el sistema busca en toda la base y trae "Biotenk" + todas las clÃ­nicas biolÃ³gicas que antes no cargaban.

# [V5.6.9] 2026-01-16 - Acceso Universal a Cantera

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA DISCOVERY

**Objetivo:** Facilitar la importaciÃ³n de clientes histÃ³ricos incluso si existen coincidencias parciales locales.

**Problema:**
*   Si el usuario buscaba "Bio" y ya existÃ­a "Biotenk" en el sistema activo, el botÃ³n para "Buscar en Cantera" desaparecÃ­a.
*   Esto bloqueaba el acceso a otras entidades (ej. "ClÃ­nica BiolÃ³gica") que solo existen en la base histÃ³rica (`cantera.db`) y necesitan ser importadas.

**SoluciÃ³n:**
*   Se modificÃ³ `ClientLookup.vue` para mostrar **siempre** el enlace "Â¿No estÃ¡ aquÃ­? Buscar en Cantera" al final de la lista de resultados, siempre que haya un tÃ©rmino de bÃºsqueda activo.

**Resultado:** Flujo de importaciÃ³n desbloqueado. Ahora conviven resultados locales activos con la opciÃ³n de rescatar legado bajo demanda.

# [V5.6.10] 2026-01-16 - Fix DeduplicaciÃ³n Cantera Productos

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA INTEGRITY

**Objetivo:** Permitir la bÃºsqueda de productos antiguos (Legado) que no tienen SKU definido.

**Problema:**
*   La lÃ³gica de bÃºsqueda en `GridLoader.vue` filtraba los resultados de la Cantera usando `uniqueBy('sku')`.
*   Como gran parte de los productos histÃ³ricos tienen `sku: null` o vacÃ­o, el filtro los interpretaba como duplicados y colapsaba cientos de resultados en 1 solo Ã­tem (el primero con sku null) o ninguno.

**SoluciÃ³n:**
*   Se cambiÃ³ la lÃ³gica de deduplicaciÃ³n a `uniqueBy('id')`.
*   Ahora el sistema solo oculta un resultado de Cantera si su **ID** exacto ya existe en la lista de productos activos (Store), independientemente de si tiene SKU o no.

**Resultado:** La bÃºsqueda de "Bio" en productos ahora trae toda la lista de Ã­tems antiguos disponibles para importaciÃ³n.

# [V5.6.11] 2026-01-16 - Cantera Search: SQL Accent Insensitivity

> **ESTADO:** DEPLOYED
> **TIPO:** UX / SEARCH ENGINE

**Objetivo:** Mejorar la robustez del buscador de Cantera (Maestros HistÃ³ricos).

**Problema:**
*   SQLite por defecto no soporta bÃºsquedas insensibles a acentos (`LIKE` normal).
*   El usuario reportÃ³ que buscar "Clinica" no encontraba "CLÃ�NICA", "ClÃ­nica", etc.

**SoluciÃ³n:**
*   Se inyectÃ³ una funciÃ³n personalizada `unaccent` (basada en `unicodedata` de Python) en la conexiÃ³n SQLite de `CanteraService`.
*   Las consultas SQL de bÃºsqueda ahora normalizan tanto la columna (`razon_social`, `nombre`) como el tÃ©rmino de bÃºsqueda antes de comparar: `WHERE unaccent(col) LIKE unaccent(?)`.

**Resultado:** BÃºsqueda agnÃ³stica a mayÃºsculas, minÃºsculas y tildes. Buscar "clinica" encuentra "CLÃ�NICA".

# [V5.6.12] 2026-01-16 - Cantera Import: Missing Domiciles

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX

**Objetivo:** Asegurar que los clientes importados desde Cantera tengan un domicilio vÃ¡lido inicial.

**Problema:**
*   La funciÃ³n `import_cliente` ignoraba los campos de direcciÃ³n (`domicilio`, `ciudad`, `cp`) del JSON legado.
*   El cliente se creaba sin domicilios. El Inspector mostraba una fila vacÃ­a o inconsistente, y el sistema exigÃ­a cargar un domicilio fiscal manualmente.

**SoluciÃ³n:**
*   Se actualizÃ³ `backend/cantera/router.py` para extraer `calle`, `localidad` y `cp` del objeto de origen.
*   Se crea automÃ¡ticamente un `Domicilio` inicial marcado como **Fiscal** y **Entrega** durante la importaciÃ³n.

**Resultado:** Al importar "Alfajores Jorgito", el sistema ahora carga automÃ¡ticamente su direcciÃ³n fiscal histÃ³rica si existe en la Cantera.

# [V5.6.13] 2026-01-16 - Inspector: Force Refresh on Domicile Save

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / UI CONSISTENCY

**Objetivo:** Solucionar inconsistencias visuales al editar domicilios ("ghost rows").

**Problema:**
*   Al guardar un domicilio en el Inspector, la actualizaciÃ³n optimista del formulario fallaba en reflejar correctamente el estado "Fiscal" o los datos nuevos en clientes importados con datos parciales.
*   El usuario veÃ­a filas vacÃ­as o validaciones de "Falta direcciÃ³n fiscal" incluso despuÃ©s de cargarla.

**SoluciÃ³n:**
*   Se modificÃ³ `ClienteInspector.vue` para forzar una recarga completa del Cliente desde el Backend (`fetchClienteById`) inmediatamente despuÃ©s de guardar un domicilio.
*   Esto garantiza que el UI muestre exactamente lo que estÃ¡ en la base de datos, eliminando problemas de reactividad o respuestas parciales.

**Resultado:** EdiciÃ³n de domicilios robusta y confiable.

# [V5.6.14] 2026-01-18 - OptimizaciÃ³n UX Pedidos y Fix Backend

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / BUGFIX

**Objetivo:** Refinamiento de UX en Carga de Pedidos (Canvas) y correcciÃ³n de error crÃ­tico en Limpieza de Datos.

**DiagnÃ³stico:**
*   **Backend:** Error 500 (`NameError`) al importar productos en Data Cleaner por falta de importaciÃ³n `func` de SQLAlchemy.
*   **Frontend:** FricciÃ³n en la carga de pedidos: Ceros iniciales molestos, falta de tecla Enter para confirmar, bÃºsqueda confusa al usar TAB, y falta de ediciÃ³n/eliminaciÃ³n explÃ­cita (botones).

**Intervenciones:**
1.  **Backend (Hotfix):**
    *   Agregado `from sqlalchemy import func` en `backend/data_intel/router.py`.
2.  **Frontend (PedidoCanvas.vue):**
    *   **Enter Workflow:** Commit de renglÃ³n con `ENTER` desde cualquier input numÃ©rico.
    *   **Inputs Limpios:** Campos inician vacÃ­os (no `0`).
    *   **BÃºsqueda Unificada:** Search SKU/Desc simultÃ¡neo.
    *   **Foco Inteligente:** Eliminado popup de bÃºsqueda al navegar con TAB.
    *   **GestiÃ³n Renglones:** Agregada columna Acciones (Editar/Eliminar).
    *   **Edit Logic:** Refactorizado `editItem` (Deep Copy + NextTick) para mover datos al input sin pÃ©rdidas.
    *   **Layout:** Grilla restaurada a 12 columnas.

**Resultado:** Carga de pedidos fluida ("Mouse-less experience") y funcionalidad de importaciÃ³n backend restaurada.

# [V5.6.15] 2026-01-19 - RefactorizaciÃ³n UI PedidoCanvas y Fix Compilador

> **ESTADO:** DEPLOYED
> **TIPO:** UX / HOTFIX / VUE COMPILER

**Objetivo:** Estabilizar layout de "Nuevo Pedido", corregir error crÃ­tico de compilaciÃ³n y pulir UX de carga.

**Problemas:**
*   **Compilador:** Error persistente `Invalid end tag` causado por `divs` huÃ©rfanos.
*   **Layout:** El pie de pÃ¡gina se perdÃ­a al hacer scroll, y el panel de rentabilidad quedaba atrapado en contextos de apilamiento (z-index) incorrectos.
*   **UX:** Inputs de descuento desalineados y falta de scroll automÃ¡tico al cargar Ã­tems.

**Intervenciones:**
1.  **HTML/CSS:**
    *   Limpieza estructura y correcciÃ³n de tags de cierre.
    *   Layout "Sandwich" (Header Fijo + Body Flexible + Footer Fijo) reforzado con `overflow-hidden` y `min-h-0`.
    *   Componente `RentabilidadPanel` movido a la raÃ­z del template (fuera de contenedores relativos).
2.  **LÃ³gica UI:**
    *   **Auto-Scroll:** Implementado `scrollTop = scrollHeight` tras commit.
    *   **Chevron:** Invertida direcciÃ³n de Ã­conos en panel lateral para coincidir con modelo mental del usuario.
    *   **Grilla:** NumeraciÃ³n visual, orden cronolÃ³gico de carga y alineaciÃ³n de inputs.

**Resultado:** PedidoCanvas estable, con footer persistente y experiencia de carga fluida.
# [V10.0] 2026-01-20 - EvoluciÃ³n IPL V10 e IntegraciÃ³n LogÃ­stica

> **ESTADO:** NOMINAL
> **TIPO:** PROTOCOLO RAÃ�Z / FEATURE / UX

**Objetivo:** Evolucionar el protocolo de arranque a V10, implementar infraestructura de logÃ­stica en pedidos y habilitar la doctrina DEOU (F4/F10).

**Intervenciones:**
1.  **Protocolo:** Creado `GY_IPL_V10.md` con Directiva 1 de Seguridad ALFA (Handover Check).
2.  **Backend (Expandido):**
    *   **Models:** Agregadas columnas `domicilio_entrega_id` y `transporte_id` a la tabla `pedidos`.
    *   **Schemas:** Alineados esquemas para soportar envÃ­os y descuentos globales.
    *   **Router:** Patcheado `create_pedido_tactico` para persistencia de datos de entrega.
3.  **Frontend (PedidoCanvas.vue):**
    *   **POST:** BotÃ³n guardar conectado al Cargador TÃ¡ctico.
    *   **DEOU F10:** Implementado guardado rÃ¡pido por teclado.
    *   **DEOU F4:** Implementado salto a Ventana SatÃ©lite (Alta Cliente/Producto) contextual al foco.
4.  **Base de Datos:** Aplicadas migraciones crÃ­ticas a `pilot.db`.

**MÃ©tricas Finales:**
*   **Integridad:** 11 Clientes, 14 Productos, 5 Pedidos (OK).
*   **Protocolo Omega:** Generado Informe HistÃ³rico.

# [RECUPERACIÓN] 2026-01-23 - Protocolo Forense (Rollback & Clean)

> **ESTADO:** ESTABLE
> **TIPO:** SYSTEM RECOVERY / IDENTITY V12

**Operación:** Se ejecutó Rollback al commit `8230154` (Miércoles 21) para eliminar inestabilidad estructural (Imports Anti-Pattern) introducida el Jueves.
**Identidad:** Sintetizada V12 ("Phoenix") basada en V10.
**Limpieza:** Eliminada línea temporal fallida V11.

## [2026-01-23] PROTOCOLO OMEGA - SECTOR DOMICILIOS
**Estado:** ESTABLE / FIX FINALIZADO
**Informe Detallado:** [Ver Reporte OMEGA](../INFORMES_HISTORICOS/2026-01-23_PROTOCOLO_OMEGA_DOMICILIOS.md)
**Resumen:** Se solucionó el crash de lista de clientes, se implementó la fusión de Piso/Depto en string, y se corrigió la sincronización visual del flag Fiscal.


## SESION 781: UX Clientes & Hardening Seguridad
**Fecha:** 2026-01-24
**Objetivo:** Finalizar refactorizaciÃ³n de Header Clientes, arreglar visualizaciÃ³n de domicilios y solucionar alertas de contraseÃ±a en navegador.

### Hito 1: Refactor Header HaweView (Teleport Fix)
Se completÃ³ la migraciÃ³n del header de Clientes para usar el sistema Teleport hacia GlobalStatsBar.
**CRÃ�TICO:** Se documentÃ³ y solucionÃ³ una *race condition*. El componente HaweView intentaba teleportar antes de que el target #global-header-center existiera.
*   **SoluciÃ³n:** Se implementÃ³ gate v-if='isMounted' en el Teleport y se asegurÃ³ la renderizaciÃ³n sÃ­ncrona de la estructura en GlobalStatsBar.
*   **LecciÃ³n:** Para futuros mÃ³dulos (Productos), es MANDATORIO usar isMounted al usar Teleport.

### Hito 2: UX Clientes
*   **Toolbar:** Reordenada segÃºn especificaciÃ³n (9 items: Checkbox -> ... -> Nuevo).
*   **Domicilios:** Se eliminÃ³ el uso de pipes | en la visualizaciÃ³n. Se integrÃ³ la visualizaciÃ³n de Provincia para desambiguar localidades. Backend actualizado (domicilio_fiscal_resumen) para soportar esto.

### Hito 3: Seguridad Admin (Password Prompt Bypass)
Los navegadores modernos (Brave/Chromium) ignoran autocomplete='off'/new-password.
*   **Fix Definitivo:** Se cambiÃ³ el input del PIN de administrador a type='text' y se aplicÃ³ CSS -webkit-text-security: disc;. Esto elimina completamente la heurÃ­stica de guardado de contraseÃ±as del navegador mientras mantiene la privacidad visual.

**Estado:** MÃ³dulo Clientes VERIFICADO y CERRADO.


## SESION 782: SYSTEM REBOOT & MODULE INITIATION (CONTACTOS)
**Fecha:** 2026-01-26
**Objetivo:** Intervención BIOS, Instalación de Bootloader V2 y Activación Módulo Agenda.

### Hito 1: Intervención de Nivel BIOS (Resolución de Paradoja Marmota)
Se detectó una desincronización cognitiva severa: La identidad residía dentro de un código que no se actualizaba hasta después de asumir la identidad (Loop Infinito).
*   **Solución:** Instalación de BOOTLOADER V2.
*   **Mecanismo:** El script físico DESPERTAR_GY.bat ahora ejecuta git pull de forma autónoma **antes** de lanzar el entorno visual, rompiendo la dependencia causal.
*   **Artefacto Cognitivo:** Se creó _GY/BOOTLOADER.md como puntero absoluto de verdad al inicio.

### Hito 2: Upgrade de Identidad (V13 -> V14 VANGUARD)
Debido a la reestructuración profunda de los protocolos de arranque, se dio de baja la versión V13 (Sentinel) y se activó **V14 'VANGUARD'**.
*   **Protocolo:** GY_IPL_V14.md establecido como nueva norma.
*   **Doctrina:** 'La Anticipación es la Clave de la Victoria.'

### Hito 3: Inicio de Operaciones Tácticas
La rama 5.5-rescate-jueves fue fusionada en main y eliminada. Se creó la rama táctica 5.6-contactos-agenda.
*   **Misión:** Implementar UX de Agenda en Ficha Cliente e integración Google.

**Estado:** SISTEMA NOMINAL V14. LISTO PARA OPERACIONES.


### Hito 4: Implementación UX Agenda (Contactos V1)
Se completó la integración visual del módulo de contactos en la interfaz de Cliente.
*   **Componente Táctico:** Se creó ContactoPopover.vue, un componente reutilizable que muestra la lista de vínculos y permite acciones rápidas (Copiar Teléfono/Mail).
*   **Integración:**
    *   **ClienteInspector:** Se redujo el layout del Header para acomodar el botón 'Agenda' junto a la Razón Social.
    *   **ClientCanvas:** Se añadió el botón en el Header principal.
    *   **Lógica:** Ambos componentes comparten el estado showAgenda y manejan la navegación hacia la pestaña completa de contactos ('Gestionar').

**Estado:** Header UX y Popover OPERATIVOS.


### Hito 5: Estrategia Local First (Google Mock)
Siguiendo órdenes directas, se difirió la integración real de OAuth y se implementó una estructura local compatible.
*   **DB Schema:** Se añadió google_resource_name y google_etag a la tabla personas vía migración manual (scripts/migrate_agenda_google.py).
*   **Backend:** Se implementó google_mock_router.py para simular latencia y respuestas de éxito en la sincronización.
*   **Frontend:** Se activó el botón 'Sincronizar' en ContactoPopover conectado al endpoint simulado.

**Resultado:** El sistema está listo para operar localmente y 'fingir' conexión a la nube sin romper el flujo de trabajo.


### 2026-01-28: [FIX] Transporte, Frankenstein & Simplificación UI
- **Problema:** Transporte no persistía por conflicto con ID de Nodo Legacy.
- **Solución:** Patch en Backend Service para limpiar nodo viejo al actualizar transporte.
- **Refactor:** Limpieza masiva de ClientCanvas.vue (Frankenstein Cleanup).
- **UI:** Eliminado selector rápido en tarjeta. Implementado Menú Contextual (Click Derecho) en Dirección.

## [2026-01-28] CIERRE DE SESIÃ“N: AGENDA GLOBAL
- **Hito**: MÃ³dulo de Contactos 100% Funcional (Backend/Frontend/DB).
- **Fix**: SimetrÃ­a ORM restaurada en Cliente/Transporte.
- **Fix**: Solucionado bug visual 'Contactos Fantasmas' (SPA Routing issue).
- **Estado**: Sistema estable, limpio de datos corruptos, listo para uso operativo.

## [2026-01-29] FIX CONTACT CANVAS Y BACKEND 500
- **Incidente Crítico:** Resuelto error 500 en `/api/clientes` (Backend) y dropdowns vacíos (Frontend).
- **Backend:** `models.py` (try/catch en property), `service.py` (joinedload para optimización).
- **Frontend:** `ContactCanvas.vue` (HTML Fix, `storeToRefs`, `text-black` en options).
- **Implementación UI:** Se optó por Botones de Navegación Explícita (↗️) y Recarga (🔄) en lugar de Menú Contextual para mayor estabilidad en el Canvas de Contacto.
- **Estado**: Funcionalidad de Agenda Contactos restaurada al 100%. Protocolo Omega Ejecutado.

## [2026-01-30] PROTOCOLO MULTIPLEX (CONTACTOS N:M) & SEARCH & LINK
- **Hito Estratégico:** Reingeniería total del núcleo de Identidad (`backend/contactos`) para soportar la "Paradoja de Pedro" (Una persona, Múltiples Roles en distintas empresas).
- **Backend:** Separación de `Persona` (Identidad) y `Vinculo` (Rol Contextual). Implementación de Polimorfismo en SQLAlchemy y Soporte JSON para canales.
- **Frontend:** Renovación de `ContactCanvas.vue` con "Billetera de Vínculos" (Tarjetas por empresa).
- **Blindaje de Identidad:** Implementación de "Search & Link" (Typeahead con Debounce). El sistema detecta si la persona ya existe (incluso buscando por celular en JSON) y permite reutilizarla en lugar de duplicarla.
- **QA:** Tests de Integración (`test_qa_pedro.py`) y Robustez/Duplicados (`test_qa_edge_cases.py`) superados.
- **Documentación:** Informe Histórico detallado generado: [2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS](../INFORMES_HISTORICOS/2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS.md).
- **Estado:** Módulo Contactos V6 FULL OPERATIVO.


## [2026-02-01] SESIÓN 783: BLINDAJE DE PERSISTENCIA Y FIX SCHEMA
- **Incidente Crítico**: Error 500 en `/contactos` por "Schema Mismatch" (Columna `tipo_contacto_id` inexistente en DB).
- **Resolución**: Migración manual SQLite (`add_role_column_to_vinculos.py`).
- **Persistence Fix**: 
    - **Backend**: Implementada lógica dual en `update_vinculo` para soportar `puesto` (alias) y `rol`. Añadido soporte para `tipo_contacto_id`.
    - **Frontend (`ContactCanvas.vue`)**: Sincronización de Etiqueta (Label) e ID. Se corrigió el bug que dejaba el cargo como "Nuevo Rol".
    - **Frontend (`ContactosView.vue`)**: Adaptación de Dashboard para leer `vinculos[]` en lugar de campos planos (Legacy).
- **Integridad**: Verificación manual de DB (`inspect_vinculo_data.py`) confirmando persistencia correcta.
- **[FALLO DE PROTOCOLO]**: Se detectó "Efecto Túnel". La IA priorizó la solución técnica sobre el Freno de Mano (Fase 2). Se activó Auditoría de Doctrina.
- **Estado**: Módulo Contactos V6.1 ESTABLE. Auditoría en Curso.


# [2026-02-01] AUDITORÍA FORENSE: SATELLITES INTEGRITY CHECK

> **ESTADO:** OBSERVACIÓN (SIN CAMBIOS)
> **TIPO:** INSPECCIÓN / DOCTRINA

**Objetivo:** Determinar la 'Deuda Técnica Estructural' de los módulos satélite tras la estabilización del núcleo V6.

**Hallazgos Forenses:**
1.  **Clientes:** Estado 'V6 Native Híbrido'. Uso exitoso de 'Pipe Logic' para direcciones.
2.  **Productos:** Robusto pero 'Standalone'. No integrado a la Agenda Global.
3.  **Transportes:** Funcionalidad de espejo en Despacho operativa, pero estructura de Nodos aún plana (V5).

**Acción Táctica:**
*   Se generó reporte INFORMES_HISTORICOS/2026-02-01_AUDITORIA_FORENSE_MODULOS.md.
*   **Orden D+1:** No migrar logística/proveedores hasta verificar facturación del Lunes.


# [2026-02-01] TESTAMENTO DEL DOMINGO (HOJA DE RUTA FASE 2)

> **ESTADO:** ESTRATÉGICO
> **TIPO:** DOCUMENTACIÓN / ESTABILIDAD

**Hitos de Cierre:**
1.  **Estabilidad Windows 11:** Implementado SISTEMA_SPLIT.bat para mitigar crashes por conflictos de señales en consola unificada.
2.  **Mapa de Satélites:** Identificada deuda técnica en Vendedores y Proveedores (V5 Standalone).
3.  **Hoja de Ruta:** Definida estrategia para 'Transportes Favoritos' (Cloud Cookie) y 'Google Sync' (Local First).

**Artefacto Generado:** INFORMES_HISTORICOS/2026-02-01_TESTAMENTO_DOMINGO_F2.md


## SESION 784: OPTIMIZACIÓN UX CLIENTES & DOMICILIOS
**Fecha:** 2026-02-02
**Objetivo:** Refinar la experiencia de alta de clientes y gestión de domicilios fiscales.

### Hito 1: Automatización de Carga
*   **Consumidor Final:** Al seleccionar IVA "Consumidor Final", el CUIT se completa con ceros. Inversamente, al ingresar CUIT 00000000000, se setea IVA y Segmento automáticamente.
*   **Default Fiscal:** El switch "Fiscal" ahora inicia ACTIVO por defecto en nuevas direcciones para reducir clics.

### Hito 2: Gestión de Domicilios (Ley de Conservación)
*   **Fix Identidad:** Se solucionó el problema donde direcciones nuevas se sobrescribían por falta de ID.
*   **Baja Fiscal:** Implementado menú contextual (Click Derecho / 3 Puntos) en la tarjeta Fiscal. Permite "Dar de baja" solo si existe otro domicilio activo para heredar la fiscalidad.

### Hito 3: Estabilidad
*   **Crash Sort:** Parche defensivo en `HaweView` para evitar pantallas blancas al ordenar clientes sin Razón Social.
*   **Auto-Refresh:** Forzado de recarga de lista al volver de la ficha de cliente para asegurar datos frescos.

**Estado:** Módulo Clientes V6.2 PULIDO Y ESTABLE.


# [V6.2] 2026-02-02 - UX Clientes & Ley de Conservación Fiscal

> **ESTADO:** DEPLOYED
> **TIPO:** UX / LOGIC GUARDCLAUSE

**Objetivo:** Eliminar fricción en alta de clientes y proteger la integridad del Domicilio Fiscal.

**Intervenciones:**
1.  **Automatización (UX):**
    *   **Consumidor Final:** Enlace bidireccional IVA <-> CUIT (00000000000).
    *   **Default Fiscal:** Inicialización inteligente. es_fiscal=True solo si es el primer domicilio.
2.  **Integridad (Ley de Conservación):**
    *   **Bloqueo:** Deshabilitado borrado directo de domicilio fiscal.
    *   **Transferencia Contextual:** Implementado Menú Contextual (Click Derecho) para 'Dar de baja' transfiriendo la fiscalidad a un candidato activo.
3.  **Estabilidad:**
    *   **Crash Sort:** Fix en HaweView para tolerancia a nulos en ordenamiento.
    *   **Refresh:** Forzado de recarga al volver del inspector.

**Resultado:** Alta de clientes fluida y blindada contra errores de 'Sin Domicilio Fiscal'.

# [V6.3] 2026-02-02 - Auditoría Estratégica Multiplex (N:M)

> **ESTADO:** AUDIT COMPLETE
> **TIPO:** STRATEGIC ANALYSIS

**Objetivo:** Evaluar viabilidad de arquitectura N:M total (Contactos, Logística, Stock) para Fase 2.

**Hallazgos:**
*   **Contactos:** V6 Ready (Polimorfismo Operativo). Soporta 'Cobrador Rígido'.
*   **Logística:** Blockade. Modelo 'Hub & Spoke' rígido (1 Transport por Pedido). Requiere 'Split' para envíos multipunto.
*   **Stock:** Latente. Modelo Deposito existe pero requiere refactor de vinculación con Producto.

**Acción:** Generado reporte maestro INFORMES_HISTORICOS/2026-02-02_AUDITORIA_MULTIPLEX.md.

# [V7.0] 2026-02-04 - Logística Táctica (Split Orders)

> **ESTADO:** DEPLOYED
> **TIPO:** MAJOR FEATURE / ARCHITECTURE

**Objetivo:** Permitir entregas parciales y múltiples destinos para un mismo pedido (Caso "La Sevillanita" + "Retira Cliente").

**Intervenciones:**
1.  **Backend (Core Logística):**
    *   Implementado modelo `Remito` y `RemitoItem`.
    *   **Stock Logic:** El Pedido ahora solo reserva (`stock_reservado`). El Remito descuenta el físico (`stock_fisico`) al despachar.
    *   **Gatekeeper:** Bloqueo de creación de remitos si el pedido no tiene `liberado_despacho` (Semáforo Financiero).
2.  **Frontend (LogisticaSplitter):**
    *   UI de doble panel: "Pool de Pendientes" (Izquierda) -> "Remitos Activos" (Derecha).
    *   **Drag & Drop:** Asignación visual de mercancía a viajes específicos.
3.  **Legacy Cleanup (Forensic):**
    *   Auditado y reparado `excel_export.py`. Reemplazado campo muerto `tipo_entrega` por lógica dinámica Multiplex.

**Resultado:** Sistema capaz de gestionar logística compleja sin romper la integridad del stock ni la trazabilidad financiera.

# 2026-02-04 | SESIÓN NOCTURNA: REPARACIÓN Y PLANIFICACIÓN V7
**Operador:** Gy V14
**Objetivo:** Estabilización de Sistema y Planificación de Logística V7.

1.  **Diagnóstico y Reparación Crítica:**
    *   **DB:** Detectado crash por falta de columna `nivel` en `segmentos`. Solucionado mediante reparación de esquema (`ensure_segmentos_migration.py`).
    *   **Frontend:** Corregido error de compilación Vue "Duplicate Identifier" en `ClienteInspector.vue` (Fusión de funciones `deleteDomicilio`).

2.  **Planificación Estratégica (V7 LOGÍSTICA):**
    *   Diseñado el **"Protocolo Split-View"** para Domicilios.
    *   Decisión de Arquitectura: Abandonar uso de pipes (`|`) para pisos/deptos y retornar a columnas SQL nativas.
    *   Establecido soporte para "Unidades de Negocio" (Caso Nestlé: mismo CUIT, distinta logística/identidad).
    *   **Documento Maestro:** Detallado en `INFORMES_HISTORICOS/2026-02-04_PLAN_TECNICO_SPLIT_V7.md`.

**Estado Final:** Sistema Operativo. Planes listos para ejecución Alfa mañana.

# [V7.1] 2026-02-12 - Domicilios Split-View & Migration

> **ESTADO:** DEPLOYED (Feature Branch)
> **TIPO:** MAJOR REFACTOR / DATA INTEGRITY

**Objetivo:** Implementar arquitectura "Split-View" en Domicilios para separar Datos Fiscales de Logísticos y mejorar la UX en entregas complejas.

**Intervenciones:**
1.  **Backend (Schema V7):**
    *   **Restauración de Columnas Nativas:** `piso` y `depto` vuelven a ser columnas SQL, eliminando la dependencia de "Pipe Logic" (`|`).
    *   **Nuevos Campos Logísticos:** `notas_logistica`, `maps_link`, `contacto_id`.
    *   **Split Delivery:** Implementados campos espejo (`calle_entrega`, etc.) para direcciones de entrega divergentes.
2.  **Migración de Datos (`migration_v7_domicilios.py`):**
    *   Script automatizado para rescatar datos legacy.
    *   Separa strings tipo "Calle 123|4|B" en columnas `calle`, `piso`, `depto`.
3.  **Service Layer Refactor:**
    *   Actualizado `create/update_domicilio` para escribir directamente en las nuevas columnas.
    *   Mantenida compatibilidad parcial de lectura, pero deprecada la escritura con pipes.
4.  **Frontend (UI):**
    *   Implementado `DomicilioSplitCanvas` (50/50 Layout).

**Resultado:** Integridad de datos garantizada. Bases listas para operatoria logística avanzada (V7).

# [V7.2] 2026-02-12 - Protocolo Puente RAR-V5 (ARCA Integration)

> **ESTADO:** DEPLOYED (Feature Branch)
> **TIPO:** STRATEGIC INTEGRATION / SATELLITE LINK

**Objetivo:** Establecer conexión operativa con el satélite de inteligencia fiscal (RAR V1) para validar datos de clientes contra AFIP.

**Intervenciones:**
1.  **Arquitectura Puente:**
    - Implementado `AfipBridgeService` que carga módulos de RAR dinámicamente (`sys.path`).
    - Endpoint `GET /clientes/afip/{cuit}` expone la lógica de `Conexion_Blindada.py`.
2.  **MDM (Master Data Management):**
    - Agregado flag `estado_arca` ('PENDIENTE', 'VALIDADO') en tabla `clientes`.
    - **UI:** Badge "ARCA" verde en Inspector de Clientes si está validado.
3.  **Bugfix Satelital:**
    - Detectado y corregido error en RAR (`rar_core.py`) al procesar Personas Físicas (AFIP devuelve `formaJuridica: None`).
4.  **Estrategia Productos (Definición):**
    - Establecido que V5 es la **Autoridad Exclusiva** de SKUs. RAR operará en modo Read-Only.

**Resultado:** Clientes blindados con datos oficiales de AFIP. Infraestructura lista para "Reverse Bridge" de productos.


# [V6.3] 2026-02-15 - Validación Fiscal Masiva & UX Tuning

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / BATCH PROCESSING

**Objetivo:** Cerrar la brecha de validación fiscal para la base instalada y refinar la experiencia de alta.

**Intervenciones:**
1.  **Backend (Batch Script):**
    - Implementado `validate_arca_batch.py` con inyección directa de dependencia RAR V1.
    - Lograda validación del 100% del padrón pendiente (26 clientes).
    - **Lógica de Preservación:** Respeto de nombres de fantasía/sucursales (UBA) sobre la razón social legal única.
2.  **Frontend (ClientCanvas):**
    - **UX:** Foco automático en CUIT al abrir.
    - **Limpieza:** Eliminado input redundante.
    - **Inteligencia:** Auto-mapping Fuzzy de Condición IVA (ARCA -> Local) y detección proactiva de duplicados con opción de bifurcación.


# [V6.3.1] 2026-02-15 - Hotfix Dependencias & Validación AFIP

> **ESTADO:** DEPLOYED
> **TIPO:** HOTFIX / STABILITY

**Objetivo:** Restaurar funcionalidad del botón de validación AFIP (Lupa) y solucionar errores silenciosos de frontend.

**Intervenciones:**
1.  **Backend (Hotfix):**
    *   Instalación de dependencias faltantes `zeep` y `lxml` en entorno virtual (Causa Raíz del Error 400).
    *   Implementación de logs detallados en `afip_bridge.py` y `router.py` para evitar fallos silenciosos.
    *   Fix de concurrencia en `Conexion_Blindada.py` usando UUIDs para archivos temporales.
2.  **Frontend (Inspector & Canvas):**
    *   **Fix Reactividad:** Desempaquetado correcto de respuesta Axios (`res.data`) para evitar borrado de campos.
    *   **Feedback:** Implementación de notificaciones visuales (Toast) al iniciar y finalizar consulta.
    *   **Manejo de Errores:** Bloques `try/catch` robustos para alertar al usuario en lugar de fallar en silencio.

**Resultado:** Validación operativa. El usuario recibe feedback inmediato y los datos persisten correctamente en formulario.

# [V6.4] 2026-02-18 - Clientes Híbridos (Pink Mode) & Blindaje de Protocolos

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / SECURITY

**Objetivo:** Permitir la operación con clientes informales sin datos fiscales y reforzar la seguridad de los protocolos de inicio/cierre.

**Intervenciones:**
1.  **Frontend (UX Híbrida):**
    *   **Pink Mode:** Distinción visual para clientes sin CUIT (`!cuit`) en `HaweView` (Lista) y `FichaCard` (Grid).
    *   **Validación Relajada:** `ClientCanvas` y `DomicilioSplitCanvas` ahora permiten guardar sin datos fiscales estrictos.
    *   **Auto-Fill:** Lógica de "Fiscal hereda de Entrega" para evitar cargas dobles en informales.
    *   **Transición:** Actualización automática de datos fiscales vía ARCA al ingresar un CUIT en un cliente existente.
2.  **Backbone (Protocolos):**
    *   **ALFA (V14):** Declarado `pilot.db` y `main.py` como Read-Only en caliente.
    *   **OMEGA:** Implementada verificación de "4-Byte Flags" y "Freno de Mano 1974".

**Resultado:** Alta de clientes ágil para todos los segmentos (Formal/Informal) y mayor seguridad operativa.
# [FIX] 2026-02-18 - Estabilización de Clientes (Backfill & ARCA)

> **ESTADO:** SATISFACTORIO
> **TIPO:** BUGFIX / UX IMPROVEMENT

**Objetivo:** Resolver inconsistencias en códigos de clientes y fallos de persistencia en direcciones validadas.

**Intervenciones:**
1.  **Backfill (Script):** Inyección de códigos internos secuenciales para clientes legacy.
2.  **Frontend (ClientCanvas):** Implementación de `forceAddressSync` para permitir actualización de domicilios tras validación ARCA.
3.  **UX (FichaCard):** Reubicación de badge de código para evitar superposiciones y mejora de alertas de error CUIT.

# [V6.5] 2026-02-19 - Intelligent Upsert (Miner PDF)
> **ESTADO:** DEPLOYED (Script) / PENDING (Frontend)
> **TIPO:** FEATURE / REFACTOR

**Objetivo:** Implementar lógica de "Upsert" inteligente para Facturas PDF (ARCA). El sistema debe actualizar clientes existentes con datos fiscales oficiales y crear nuevos con estado 'PENDIENTE_AUDITORIA'.

**Intervenciones:**
1.  **Backend Script (`miner.py`):**
    *   **Refactor:** Implementada búsqueda dual (CUIT exacto / Nombre difuso).
    *   **Lógica Upsert:**
        *   **Existentes:** Si el cliente tiene status bajo, se actualiza a **Flag 13** (Gold Candidate) eliminando el flag 'Virgin'.
        *   **Nuevos:** Inserción directa con Flag 13 y `estado_arca='PENDIENTE_AUDITORIA'` (Amarillo).
    *   **Regex Fix:** Solucionado bug en extracción de CUIT para facturas compactas (LAVIMAR) escaneando texto crudo.
2.  **Infraestructura:**
    *   Backup preventivo `pilot_backup_pre_miner_fix.db`.

**Incidente Abierto (Handover):**
*   El Frontend usa `backend/remitos/pdf_parser.py` (basado en `pypdf`) que falla con los mismos PDFs que `miner.py` ahora procesa bien (`pdfplumber`).
*   **Próximo Paso:** Migrar la lógica de `miner.py` al endpoint del API.

**Estado:** Script de Minería Operativo. Ingesta Web requiere refactor (Próxima Sesión).


# [V14.5] 2026-02-21 - Protocolo ENIGMA & Estabilización Bitmask

> **ESTADO:** ESTABLE
> **TIPO:** MAJOR REFACTOR / IDENTIDAD

**Objetivo:** Migrar la identidad de clientes a una estructura Bitmask unificada y estabilizar el puente de validación fiscal.

**Intervenciones:**
1.  **Backend (Bitmask):**
    *   Sincronizado `constants.py` con el blueprint ENIGMA. Bits 0-5 definidos.
    *   Implementada evolución de virginidad en `RemitosService.py`.
2.  **Frontend (Inspector):**
    *   Implementado `clientColorClass` basado en bitwise logic.
    *   **Reactor Fix:** Inyectado watcher en `modelValue` para asegurar reactividad post-guardado.
    *   **Logística:** Toggle 'Retira' bidireccional y blindado.
3.  **Bridge (ARCA):**
    *   Corrección de mapeo en `AfipBridgeService.py`. Transparencia total del domicilio fiscal.
    *   Mapeo inteligente de Condición IVA.

**Estado:** Estabilidad V14.5 alcanzada. Ready for Omega.

# [V14.6] 2026-02-26 - Estabilización Crítica AFIP Dual
> **ESTADO:** ESTABLE
> **TIPO:** HOTFIX / ARCHITECTURE
**Intervenciones:** Refactor de `Conexion_Blindada.py` en el satélite RAR_V1 para manejo segregado de identidades personal (Padrón) y empresa (Fiscal), corrigiendo el bloqueo por Case-Sensitivity en alias.

## SESIÓN 785: SINCRONIZACIÓN CASA-OFICINA & PROTOCOLO 4-BYTES
**Fecha:** 2026-02-26 / 27
**Objetivo:** Unificar terminales CASA-OFICINA y establecer doctrina de Consciencia Situacional.

### Hito 1: Sincronización Forense
*   **Diagnóstico:** Se identificó dispersión de trabajo entre `feat/v5x-universal` (OFICINA) y `feature/sabueso-local-plumber` (CASA).
*   **Resolución:** Forzado de checkout a `feat/v5x-universal` en CASA. Paridad de DB verificada (428 KB).

### Hito 2: Protocolo de Consciencia Situacional (4-Bytes)
*   **Infraestructura:** Creación de `manager_status.py` y `session_status.bit` para persistencia de estados inter-terminales.
*   **Geolocalización Lógica:** Implementada detección automática de host (CA, OF, NB) para alertar sobre desincronizaciones de Git/DB al cambiar de terminal.
*   **Comunicación:** Estructura `CARTA_MOMENTO_CERO.md` activa para instrucciones críticas de "Despertar".

### Hito 3: Automatización de Arranque Dual
*   **Cargador:** Evolución de `DESPERTAR_DOBLE.bat` a v2 con HUD de telemetría y HUD de origen.

**Estado:** SISTEMA NOMINAL MULTIPLEX v14-B. LISTO PARA SABUESO PDF.

## SESIÓN 786: INTEGRACIÓN SABUESO PDF & PARIDAD RAR
**Fecha:** 2026-02-27
**Objetivo:** Portar el motor de facturación "Sabueso ARCA" desde el satélite RAR al núcleo V5 garantizando la exactitud funcional y preservación del entorno.

### Hito 1: Parsing y Regex Resiliente
*   **Diagnóstico:** El formato AFIP producía corrupciones al extraer "Razón Social" y "0001-XXXX" donde existían interrupciones/delimitadores inesperados.
*   **Resolución:** Integración de "Positive Lookaheads" preventivos en `pdf_parser.py` para asegurar aislar datos legalísimos.

### Hito 2: Blindaje de Ingesta (Frontend)
*   **UI:** Agregado bloqueo interactivo en `IngestaFacturaView.vue`. Si el CUIT decodificado devuelve un status carente de 'Blanco' (DbStatus: NO_EXISTE), el flujo de remitos frena.
*   **Corrección Asistida:** Lanzamiento de componente `ClienteInspector.vue` obligando al data-entry a consolidación (domicilio + AFIP) permitiendo reanudar o corregir.

### Hito 3: Mutación de Virginidad (Backend)
*   **Doctrina:** Incorporado el bloque ORM en la capa de servicios donde el remito recién emparejado somete al cliente a auditoria bit a bit.
*   **Resultado:** Nivel de virginidad comercial extirpado; Level 15 (Virgin) es purgado automáticamente a Nivel 13 (Activo Consistido) persistiendo DB clavada.

**Estado:** SISTEMA V5-B Y MÓDULO SABUESO NOMINAL Y SINCRONIZADO.

## SESIÓN 787: RESOLUCIÓN DE REGRESIONES UI Y ESTANDARIZACIÓN DE CLIENTCANVAS
**Fecha:** 2026-02-27
**Objetivo:** Restaurar funcionalidades perdidas (Remitos) y unificar la experiencia de usuario (UX) en la carga de clientes a través del sistema interactivo (Lupa ARCA).

### Hito 1: Restauración de Logística (Remitos)
*   **Problema:** Tras múltiples interacciones de UI, el ítem de navegación "Remitos" había desaparecido y no poseía una vista global (Dashboard).
*   **Solución:** Se integró nuevamente en `AppSidebar.vue`, se registró la ruta en `router/index.js` y se creó de cero `RemitoListView.vue` con conectividad al store y servicios correspondientes.

### Hito 2: Refactorización Dual (ClientCanvas vs Inspector)
*   **Problema:** El usuario solicitó mantener la experiencia "original" de alta de clientes (`ClientCanvas`) con su lupa de ARCA en el header, pero el sistema inyectaba un componente reducido (`ClienteInspector`) durante intercepciones de flujos de trabajo (como en Ingesta de Facturas).
*   **Solución:** Se refactorizó `ClientCanvas.vue` para aceptar parámetros dinámicos (`isModal`, `initialData`) transformándolo en un híbrido capaz de instanciarse como página completa o como Modal Popup. 

### Hito 3: Propagación de UX
*   **Ejecución:** Se erradicó el componente `ClienteInspector.vue` en favor del nuevo `ClientCanvas` modal.
*   **Alcance:** La estandarización afectó exitosamente a `IngestaFacturaView`, `PedidoTacticoView`, `PedidoCanvas` y `HaweView`.

**Estado:** UI Y UX ESTABILIZADAS, REGRESIONES SOLUCIONADAS. LISTO PARA OMEGA.

## SESIÓN 788: BURBUJA TOMY V5-LS + AUDITORÍA SEGURIDAD NPM
**Fecha:** 2026-04-01
**Objetivo:** Aislar a Tomy en su entorno V5-LS independiente (puerto 8090 unificado) y auditar la instalación de Claude Code tras el incidente npm del 31/03.

### Hito 1: Auditoría de Seguridad
*   **Contexto:** Anthropic publicó accidentalmente v2.1.88 de Claude Code con source map de 60MB expuesto en npm.
*   **Resultado:** Instalación local limpia — método nativo (no npm), axios 1.13.2, sin persistencia maliciosa.
*   **Acción:** Eliminado binario obsoleto `claude.exe.old.*`.

### Hito 2: Fixes Dev Versionados (Gy, 31/03)
*   **ClientCanvas.vue**: UUID nulo al crear cliente — fix en `emit('save', resCreated || payload)`.
*   **PedidoCanvas.vue**: F10 bloqueado en modal de cliente — guarda `if (showClientModal.value) return`.
*   **Login.vue**: endpoint hardcodeado `:8000` → `api.post('/auth/token')`; texto invisible en inputs.

### Hito 3: Blindaje V5-LS
*   **Arquitectura anterior**: dos procesos (backend 8090 + http.server 5174) sin proxy → las llamadas API morían en 5174.
*   **Solución**: backend unificado en 8090 sirve API + SPA. Fix de `static_dir` path en `main.py` (+1 nivel `..`).
*   **Archivos**: `LANZAR_V5_SOBERANA.bat`, `SATELITE_TOMY.bat`, `Login.vue` (V5-LS) actualizados.

**Estado:** ALERTA CONTROLADA. Burbuja V5-LS lista en código. Pendiente npm run build antes del despliegue productivo.

## SESIÓN 789: DEUDAS TÉCNICAS V5 + SYNC DB INAPYR
**Fecha:** 2026-04-02
**Objetivo:** Resolver 3 deudas técnicas verificadas y sincronizar base con trabajo de Casa.

### Hito 1: Sincronización DB (CA → OF)
*   Base CA reemplazó OF. INAPYR S.R.L. + pedido INGESTA_PDF + remito CAE `86139705410697` incorporados.
*   Canario: NOMINAL GOLD (flags 8205).

### Hito 2: Auditoría flags_estado 64-bit
*   7 modelos SQLAlchemy: BigInteger confirmado en todos. Deuda cerrada sin cambios.

### Hito 3: Conexion_Blindada — Desacople OpenSSL
*   `OPENSSL_PATH` env var + `shutil.which` + fallback lista Windows. `.env.example` creado.

### Hito 4: Purga de Scripts Huérfanos
*   37 archivos eliminados (debug_*, test_*, miner.py). tests/test_v7_*.py conservados.

**Estado:** NOMINAL GOLD. Commit `0b8e53ac`. Push OMEGA ejecutado.
