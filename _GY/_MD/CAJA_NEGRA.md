Sesión actual: 815

# CAJA NEGRA: Auditoría Genómica + apply_iva Bit40 (2026-05-22)

Sesión CA 2026-05-22 (815). Hash D: 1faac75e. Estado: NOMINAL GOLD.
Auditoría Genómica Completa: Descubrimiento de patrón sistémico donde cada regla nueva en `_audit_sovereignty` deja desactualizados los clientes históricos. Ejecutadas 5 consultas forenses contra pilot_v5x.db identificando 37 anomalías en total:
  - Bit 40 (DISCRIMINA_IVA): 28 RI pre-Sesión 812 sin Bit 40 prendido (causa: nunca fueron UPDATE post-REGLA3)
  - Bit 20 (PENDIENTE_REVISION): 6 clientes con 4 pilares OK pero Bit 20 prendido (fantasma)
  - Bit 19 (MEDALLA_ROSA): 3 clientes Rosa sin Bit 19
  - Bit 2 (GOLD_ARCA): consistente (OK)
  - Bit 1 (IS_VIRGIN): consistente (OK)
  - CF CUIT fallback: consistente (OK)
Script reparación masiva ejecutado: apagó Bit 20 en 6, encendió Bit 19 en 3, total 9 anomalías corregidas post-diagnóstico.
apply_iva Helper: Centralización de lógica fiscal en `backend/pedidos/router.py`. Función `_aplica_iva(pedido, cliente)` reemplaza 5 ocurrencias de tipo_facturacion string con Doctrina V6 (Circuito Bipolar: Bit 12 soberano + Bit 40 decide en blanco).
Commits: d84641b8 (apply_iva), 1faac75e (OMEGA auditoría).
Plan Auditoría Genómica documentado en INBOX: 4 pasos (Gy arqueología, CC forense, script reparación masiva, Utilidad Maestra flags).
Agenda 816 CA registrada: Mapa flags UX + 5 bugs pedidos (crítico: ingesta sin validación pedido refiere).
Canario CA/D: NOMINAL GOLD — LAVIMAR flags=13, 29/29 RI Bit40 OK post-reparación.
WAL checkpoint ejecutado pre-OMEGA.
OMEGA V2.2 ejecutado completo: Fase 1B, 2, 4, 6, 7.

**Agente:** Claude Code Haiku 4.5 — Hash D: 1faac75e | PIN: 1974

---

# CAJA NEGRA: Genoma Pedidos V6 + Operación Mudanza + Diff 4 (2026-05-22)

Sesión OF 2026-05-22 (814). Hash D: 5e1e2445. Estado: NOMINAL GOLD.
Genoma Pedidos V6: Introducción de `PedidoFlags` en backend/pedidos/constants.py con bits universales en la banda baja y banda alta (bits >= 32). Máscara de estados excluyentes (`STATE_MASK`) que abarca `ES_PRESUPUESTO` (Bit 32), `ES_FIRME` (Bit 33), `ES_CUMPLIDO` (Bit 34) y `ES_ANULADO` (Bit 35).
Operación Mudanza: Migración del campo string legacy `estado` a la estructura genómica en pilot_v5x.db para 31 pedidos y adición de la columna `fecha_vencimiento`.
Router Backend: Modificaciones en `backend/pedidos/router.py` para asegurar que las transiciones de estado apliquen `(flags & ~STATE_MASK) | NUEVO_ESTADO` en escrituras (Paso A) y validen estados con operaciones bitwise en lecturas (Paso B).
PedidoCanvas.vue (Diff 4): Integración de BigInt en frontend para evitar la pérdida de precisión en JS al evaluar flags > 31 (en particular `isClienteRI` con el Bit 40). Refactorización de `isSinIVA` (Motor Bipolar: Bit 12 del pedido y Bit 40 del cliente). selectProduct aplica divisor 1.21 en LISTA_5 únicamente para clientes RI. Desglose fiscal Ley 27.743 en pie del canvas discriminando IVA según el perfil impositivo y circuito (blanco/negro).
Canario D: NOMINAL GOLD — flags=13.

**Agente:** Antigravity (Gy) — Hash D: 5e1e2445

---

# CAJA NEGRA: DISCRIMINA_IVA Bit 40 + Purga Herejía del 15 (2026-05-20)

Sesión OF 2026-05-20 (812). Hash D: pendiente (pre-commit PIN 1974). Estado: NOMINAL GOLD.
DISCRIMINA_IVA Bit 40: `ClientFlags.DISCRIMINA_IVA = 1 << 40` (1099511627776). Responsable Inscripto = discrimina IVA, emite Factura A, precio de lista / 1.21. Implementado en 3 nodos: constants.py (definición canónica), afip_bridge.py (auto-encendido desde condicion_iva devuelta por RAR), service.py _audit_sovereignty REGLA 3 (toggle permanente en create/update según condicion_iva.nombre).
Purga Herejía del 15: 5 clientes en pilot_v5x.db tenían Bit 15 (32768 = FacturaFlags.PASADO_A_PEDIDO) encendido por error de IA anterior que confundió "Nivel 15" del Códice Arlequín (valor decimal = suma EXISTENCE+IS_VIRGIN+GOLD_ARCA+V14_STRUCT = 15) con "Bit 15" (posición = 1<<15). Purga: flags_estado & ~32768. 5 registros saneados. Canario NOMINAL GOLD.
BIBLIOTECA_NIKE.md: Módulo 2 actualizado con doctrina canónica "La Herejía del 15" — prohíbe asignar 1<<15 en clientes.flags_estado.
INBOX.md: pendiente sesión 813 registrado — diff 4 PedidoCanvas lógica selectProduct por Bit 12 (negro) + Bit 40 (RI) + CF (precio final con IVA incluido). isClienteRI computed ya diseñado.
Frontend diff 4 NO ejecutado — postergado sesión 813. No commitear.
Canario D: NOMINAL GOLD — flags=13. WAL checkpoint ejecutado.

**Agente:** Claude Code Sonnet 4.6 — Hash D: b0ac3c47

---

# CAJA NEGRA: HONNEY fix + DEOU F4 + CF CUIT fallback (2026-05-19)

Sesión OF 2026-05-19 (811). Hash D: 208d6a46. Hash P: 937d5be. Estado: NOMINAL GOLD.
HONNEY fix: hard_delete_cliente() — guard IS_VIRGIN relajado para flags_estado=0 (fósiles pre-genoma). Frontend HardDeleteManager: amber border, label "CLIENTE IMPOSIBLE", botón habilitado, integrity safe.
DEOU F4: 3 bugs en alta rápida — cliente nacía inactivo (flags|=3 mínimo vital), CUIT era '' en lugar de null, _audit_sovereignty ausente en create_cliente. Fix: currentFlags|=3 en ClientCanvas, cuit:null en PedidoCanvas, _apply_cf_cuit_fallback+_audit_sovereignty+activo sync en create_cliente.
CF CUIT fallback: nuevo método _apply_cf_cuit_fallback() en ClienteService — si condicion_iva='Consumidor Final' y cuit=null → asigna '00000000000'. Llamado antes de _audit_sovereignty en create y update.
Borrado Dai (pilot_v5x.db) — fósil de test, PIN 1974.
Deuda técnica Rosa unification documentada en INBOX.md: 3 estrategias divergentes (Bit4/nibble/Bit19).
Commits D: 1e5d4327 (HONNEY), 0286f0df (DEOU), 208d6a46 (CF CUIT). Cherry-picks P: 85a48b8, 0b31fe2, 937d5be.

**Agente:** Claude Code Sonnet 4.6 — Hash D: 208d6a46 / Hash P: 937d5be

---

# CAJA NEGRA: FIX C4 ClientCanvas + IVA Rosa + Navegación + Bit 4 Migración (2026-05-18)

Sesión OF 2026-05-18 (810). Hash D: ff77a309. Hash P: 3e060bb. Estado: NOMINAL GOLD.
FIX C4 ClientCanvas.vue: has4Pillars bifurcado — Rosa valida es_entrega, Gold valida es_fiscal. Eliminado currentFlags &= ~2 (violación doctrina IS_VIRGIN desde frontend).
Syntax error Vite PedidoCanvas: bloque else espurio en savePedido (línea ~1306) eliminado. Vite arranca sin errores.
IVA Rosa: selectProduct divide precio /1.21 cuando isSinIVA && origen === 'LISTA_5'. Template v-if="!isSinIVA" oculta sección IVA para informales.
Reset post-save: resetPedido(skipConfirm=true) — sin confirm() espurio tras guardar.
Navegación corregida: PedidoList.vue (2x) y PedidoInspector.vue (2x) — ruta muerta /hawe/tactico reemplazada por named routes PedidoCanvas / PedidoEditar.
Migración Bit 4 (PIN 1974): _audit_sovereignty() gap documentado (requiere segmento_id). UPDATE manual V5_LS_MASTER.db: 4 clientes Rosa confirmados. Sync pilot_v5x.db: 2 nuevas + Ana Robles ya tenía.
2 commits D: bf406415, ff77a309. 2 cherry-picks P: 5adf6f4, 3e060bb. Push confirmado en ambos.

**Agente:** Claude Code Sonnet 4.6 — Hash D: ff77a309 / Hash P: 3e060bb

---

# CAJA NEGRA: Auditoría Cruzada IS_VIRGIN + Motor Bipolar + Roseti 1482 (2026-05-18)

Sesión CA 2026-05-18 (809). Hash D: 4010b655. Estado: NOMINAL GOLD (OMEGA pendiente 810).
Auditoría cruzada Opus 4.7 + Antigravity Pro en serie — hallazgos convergentes confirman bugs reales.
IS_VIRGIN rename global: HAS_ACTIVITY → IS_VIRGIN en 15 archivos (clientes, pedidos, facturacion, ingesta, productos, remitos). Guard hard_delete invertido: if not (current_flags & IS_VIRGIN) — bloquea tocados, permite vírgenes.
Motor Bipolar canonizado: Bit 12 (NO_FISCAL_FORCE) del PEDIDO soberano para IVA. isClientRosa (Bit 4) solo para restricciones operativas. Fixes PedidoCanvas: isSinIVA Bit 12, wasIngesta pre-clear, Guardar e Imprimir condicional, 409 early return.
nivel_id huérfano eliminado ClientCanvas.vue:1557 — reemplazado por lógica CUIT genérico.
Roseti 1482 creado como domicilio plantilla (ID: 59b01b5a). DOMICILIO_ROSETI_ID en constants.py. _ensure_domicilio_rosa() en create/update cliente Rosa.
Deprecación documentada: campo cliente_id legacy en models.py Domicilio.
Fixes backend pedidos: C1 delete_pedido NameError, C3 NO_FISCAL_FORCE IVA 5 puntos, C5 STRICT_MODE_VIOLATION nivel_lista=None.
3 commits D: c2372d5a, bb5576c9, 4010b655. Push origin/main confirmado.

**Agente:** Claude Code Sonnet 4.6 + Opus 4.7 (auditor) + Antigravity Pro (auditor) + Nike Arq 5.5 — Hash D: 4010b655

---

# CAJA NEGRA: Doctrina Virginidad + Atomicidad Ingesta + Sync D↔P (2026-05-15)

Sesión OF 2026-05-15 (808). Hash D: 513796bf. Hash P: 5865616. Estado: NOMINAL GOLD.
FIX UX PedidoCanvas: botón "Guardar e Imprimir" oculto con v-if en flujo manual. wasIngesta capturado pre-clearIngestaData. Reset canvas post-guardado manual en vez de redirigir a PedidoList.
FIX Rosa/OPERATOR_OK: esOperatorOk bypasea todo el bloque fiscal en savePedido(). Sin borrador factura, sin remito puente.
Doctrina de Virginidad implementada: removidos 2 triggers incorrectos (4 pilares, Vanguard Canon). Agregados 2 triggers canónicos: CUMPLIDO en pedidos/router.py, CAE en facturacion/service.py. Ghost pedido remito manual nace PENDIENTE.
Diagnóstico 409 ingesta: raw 80af6b8b stuck en RECIBIDO con downstream ya existente (remito 0016-00002535 + factura AUTORIZADA_AFIP). Reconciliado manualmente (PIN 1974).
Atomicidad IngestaService.approve(): flush-only en create_from_ingestion, checkpoint PROCESANDO, estado ERROR en fallo. Único db.commit() al final del flujo exitoso.
Cherry-pick D→P: 4 commits sesión 807-808. Conflicto clientes/service.py resuelto con versión D (doctrina virginidad). Push P: d3173b2..5865616.

**Agente:** Claude Code Sonnet 4.6 — Hashes D: 513796bf / P: 5865616

---

# CAJA NEGRA: Silo Drive + Pricing Engine Soberano + Protocolos ALFA/OMEGA (2026-05-14)

Sesión OF 2026-05-14 (807). Hash D: 0b34f1f9. Hash P: d3173b2. Estado: NOMINAL GOLD.
Silo Drive creado: Q:\Mi unidad\V5_Silo_Claude — README, INBOX, ESTADO_ECOSISTEMA, estructura OF/CA/GLOBAL/LEIDOS.
ALFA.md D y P: PASO 0 con lectura de INBOX + ESTADO_ECOSISTEMA en cada despertar.
OMEGA.md D y P: FASE 1B WAL checkpoint obligatorio antes de exportar DB. ESTADO_ECOSISTEMA como primer ítem de burocracia.
Fix pricing engine: costos=None ya no bloquea con 409 — precio soberano del operador. STRICT_MODE_VIOLATION reservado para cliente inválido.
3 deudas técnicas registradas (sesión 807): Badge FALTAN, Guardar e Imprimir, etiqueta botón por contexto.
DB 807d instalada en D desde MT (5 pedidos nuevos: 34-38). Pedido 38 eliminado (Pao Tandil — incompleto, a recrear).
Canario D: NOMINAL GOLD — flags=13.

**Agente:** Claude Code Haiku 4.5 — Hashes D: 0b34f1f9 / P: d3173b2

---

# CAJA NEGRA: Arlequín V2 — Inferencia Rosa + GENOMA_UNIVERSAL + fix NO_FISCAL_FORCE (2026-05-13)

Sesión OF 2026-05-13 (806). Hash D: abd34332. Hash P: 2d7c5c2. Estado: NOMINAL GOLD.
GENOMA_UNIVERSAL.md sellado por Nike Arq 5.5 — mapa canónico de bits para todas las entidades del ecosistema.
Herejía NO_FISCAL_FORCE purgada: Bit10 (1024) → Bit12 (4096) en constants.py, PedidoList.vue (6 refs) y router.py.
Doctrina Arlequín V2 implementada: inferencia automática de cliente Rosa (OPERATOR_OK Bit4) en _audit_sovereignty().
Consumidor Final blindado: CUIT 00000000000 forzado GOLD_ARCA, nunca infiere Rosa.
CUIT 00000000000 declarado exclusivo del MOSTRADOR/GENÉRICO (bloqueo en create y update).
PROTOCOLO_EMERGENCIA_MT.md creado. 7 ítems registrados en deuda_tecnica.
DevBadge oculto en producción (import.meta.env.DEV). Cherry-pick D→P limpio (4 commits).
Canario D: NOMINAL GOLD — flags=13.

**Agente:** Claude Code Sonnet 4.6 — Hashes D: abd34332 / P: 2d7c5c2

---

# CAJA NEGRA: Estabilización Infraestructura y Soberanía Tomy (2026-05-11)

Sesión OF 2026-05-11 (802). Saneamiento integral de Producción (Tomy): Carpeta renombrada a `v5-ls-Tom` para consistencia. Exorcismo de rutas legacy (`C:/dev/V5-LS`) en 28 archivos físicos (scripts, logs, bitácoras). Saneamiento de archivos `.env` en `current` y `staging` de P. Unificación de repositorio Git Tomy: merge de divergencias OF/CA, limpieza de binarios (.db, .pyc) del índice y push a GitHub (`2abc8d6`). Eliminación de mock data en `ClientCanvas.vue` (D y P) y registro de deuda técnica para API real de inteligencia comercial. Formalización de protocolo OMEGA estrictamente manual en `ALFA.md`. Canario D: NOMINAL GOLD — flags=13.

**Agente:** Antigravity (Gy V5) — PIN 1974

---

# CAJA NEGRA: Estandarización Numeración 0016 + Ingesta V2 (2026-05-08)

Sesión OF 2026-05-08 (800). Módulo Ingesta V2 completo (FacturasRaw/Procesadas). Conserje v2 READ ONLY sellado por Nike. Factura Espejo Bit 22 (PRE_MODULO_FACTURACION = 4227083). Sabueso V5.7: estandarización 0016-XXXXXXXX en remitos (pdf_parser.py robustecido). Live preview numeración en UI Ingesta. Fix em dash en remito_engine.py (L74, L167). Purgado de LABME y Pedido 32. OMEGA V2.2 ejecutado (PIN 1974). Genoma actualizado: 851.

**Agente:** Antigravity (Gy V5) — Hash: 9e593e67

---

# CAJA NEGRA: Genoma Facturas + Conserje Duplicados CA (2026-05-08)

Sesión CA 2026-05-08 (799). `backend/facturacion/constants.py` (nuevo): clase `FacturaFlags` con mapa completo bits 0-21 de `flags_estado` en tabla facturas, sellado Nike Arq 5.5. Bits: EXISTENCE(1), HAS_ACTIVITY(2), HAS_REMITO(4), ACTIVE(8), V15_STRUCT(1024), PASADO_A_PEDIDO(32768), EN_CUARENTENA(65536), TIENE_NC(131072), TIENE_ND(262144), ES_NC(524288), ES_ND(1048576), AUDITADA(2097152). `models.py`: `notas_auditoria = Column(String, nullable=True)` en Factura — texto libre para observaciones de auditoría, complementa bit 21. Migración 029 ejecutada (`ALTER TABLE facturas ADD COLUMN notas_auditoria VARCHAR`, idempotente, registrada en `_migraciones_aplicadas`). Conserje en `POST /remitos/ingesta-pdf`: guard pre-proceso consulta `facturas` por `punto_venta + numero_comprobante` → HTTP 409 `FACTURA_DUPLICADA` con `factura_id` si existe. Bug G: modal advertencia pedidos duplicados (mismo cliente + fecha + ítems similares) — operador decide continuar o cancelar. Canario D: NOMINAL GOLD — flags=13.

**Agente:** Claude Code Sonnet 4.6 — Hashes: 93a9a3d4 (técnico), 58404b1b (Bug G)

---

# CAJA NEGRA: Bugs D/E/F/H + IngestaItemModal Extracción OF (2026-05-07)

Sesión OF 2026-05-07 (798). Bug C ítem 13 ya resuelto en CA-797. Esta sesión: Bugs D/E/F (F4 satélite PedidoCanvas) — Fix F: `ProductoInspector.vue` fetchRubros defensivo en modo satellite; Fix D+E: ProductosView v-if en `<main>` + nombre único `AltaProducto_${Date.now()}` en PedidoCanvas. Hash: db72e856. Extracción IngestaItemModal.vue: modal de resolución de ítems extraído de PedidoCanvas (-137 líneas) a componente propio con props `items`, emits `resolved/cancel`. Fix H integrado: F4 en modal abre satélite de alta producto via `handleOverlayKeydown`. Botón copy descripción→buscador. Bugs registrados: IngestaItemModal navegación teclado pendiente. Migraciones ejecutadas en D: 026, 027, 028, 029 (facturas schema drift, EmpresaTransporte.activo). Tablas nuevas en pilot_v5x.db: `deuda_tecnica`, `roadmap`. Hash final: afd5cd74.

**Agente:** Claude Code Sonnet 4.6 — Hashes: db72e856, afd5cd74

---

# CAJA NEGRA: Bug C Backend + Migraciones CA (2026-05-06)

Sesión CA 2026-05-06 (797). Bug B resuelto: `pending409Context` en store pedidos + restore en `onMounted` de IngestaFacturaView — canal separado que PedidoCanvas nunca toca (usa `clearIngestaData`). Bug C: 7 bugs forenses en endpoint `/remitos/puente/desde_factura/{id}` — `factura_id: int→str` (endpoint inoperativo), `fecha_vto_cae→cae_vencimiento` (AttributeError), doctrina numeración `0016-XXXX-YYYYYYYY`/`0015-XXXXXXXX`, `total_bruto→factura.total` (silencioso 0.0), `cuit_comprador` post-flush. Arquitectura N:M: clase `FacturaRemito` con GUID + fecha_vinculo + flags_estado reemplaza `Table` simple, guard idempotencia en `_vincular_factura_remito()`. Sistema migraciones: `_migraciones_aplicadas` + patrón SKIP/REGISTER en migrate_000 y migrate_026. Pendiente: D-7 savePedido→cadena factura→remito. Informe: `INFORMES_HISTORICOS/2026-05-06_BUG_C_BACKEND_MIGRACIONES_CA.md`

**Agente:** Sonnet (arquitecto) + Claude Code Sonnet 4.6 (ejecutor) — Hashes: 9df14bdf, 0cf51130, 529aa2be

---

# CAJA NEGRA: Parser Y-Axis Fix + Modal Sync CA — Ingesta PDF Items (2026-05-05)

Sesión CA 2026-05-05 (796). Causa raíz items[] vacío: tolerancia Y-axis `/4` (±2pts) insuficiente para PDFs AFIP — qty y u_medida en misma línea visual pero con delta real 5pts. Fix: `/4`→`/6`. Caso validado: L EPI S.R.L., Alcohol 70% qty=4,00 precio=$13.500,00. Typo DB corregido (Acohol→Alcohol ID 150). Canario v2.py actualizado TARGET_FLAGS 8205→13 post-saneamiento 2026-05-02. Bugs backlog: A (search/ref modal), B (ESC 409), C (ciclo logístico), Clientes azules, Build P pendiente. Informe: `INFORMES_HISTORICOS/2026-05-05_INGESTA_PARSER_FIX_MODAL_SYNC_CA.md`

**Agente:** Claude Code Sonnet — Hashes: pendiente commit OMEGA

---

# CAJA NEGRA: Arlequín V2 Merge CA — Doctrina Bit 1 Resuelta (2026-05-04)

Sesión CA 2026-05-04. Merge quirúrgico feature/arleq-v2-productos en D (5 archivos). 3 bugs post-merge corregidos (VIRGINITY→HAS_ACTIVITY, default=2, lógica hard_delete). Doctrina Bit 1 canonizada: 1=virgen/borrable, 0=tocado/bloqueado. OMEGA V2.2 en D y P. Informe: `INFORMES_HISTORICOS/2026-05-04_ARLEQ_V2_MERGE_QUIRURGICO_CA.md`

**Agente:** Sonnet (arquitecto) + Claude Code Haiku (ejecutor) — Hash D: f9ae409a — Hash P: 8ad0ad58

---

# CAJA NEGRA: Modernización IVA V1 & Espejado Soberano D↔P (2026-04-24)

## 1. Modernización IVA V1 (Satelite)
Se eliminó la dependencia de consola (`.bat` arcaico) para la ingesta. Se implementó una **Interfaz Web (FastAPI + Jinja2)** que permite:
- **Drag & Drop**: Ingesta intuitiva de archivos ZIP/CSV de ARCA.
- **Reportería Avanzada**: El `ReportGenerator` ahora incluye el campo `Tipo` (FAC/NC/ND) y la sumatoria de `Σ (Otros Tributos)`, crucial para el saldo operativo fiscal.
- **Lanzador**: Se creó `LANZAR_IVA_WEB.bat` para facilitar el acceso de Tomy.

## 2. Espejado Soberano D↔P
Se detectaron divergencias críticas entre el entorno de Desarrollo (D) y Producción (P).
- **Acción**: Sincronización binaria del Backend y reconstrucción (`npm run build`) del Frontend en P.
- **Resultado**: Paridad 1:1 alcanzada. El nuevo módulo de **Facturación** y las mejoras de logística ahora son nativas en Producción.

## 3. Estabilización de Producción (BioTenk)
- **Remitos**: Se resolvió la orfandad del remito #2528 re-vinculándolo al Pedido #28 tras la purga del duplicado #29.
- **PDF Engine**: Se corrigió el truncado de domicilios en `remito_engine.py` mediante la concatenación de `calle + numero + localidad` en el Router.
- **UX**: Se forzó el cambio de Favicon a **Lila/Violeta** en P para evitar errores de contexto operativo.

---
**Marcador de Sesión**: 2026-04-24_OMEGA_MODERNIZACION_ESPEJADO
**Agente**: Antigravity (Gy V5)

---

# CAJA NEGRA: Estrategia de Soberanía Fiscal & Centro de Liquidación (2026-04-23)

## 1. Validación de Arquitectura "Soberana" (Fase 1)
Se ratificó el funcionamiento del **Asistente de Facturación (Modo Espejo ARCA)**. La premisa es que el sistema asume la soberanía del cálculo fiscal (prorrateos de descuentos e IVA) para evitar errores humanos al cargar en la web oficial de AFIP. 
- **Carga Manual**: Se confirmó que el CAE y el Número de Comprobante son tokens externos generados por ARCA que el usuario debe re-ingresar en HAWE para "sellar" la operación.
- **Estado Nominal**: Verificación exitosa del bitmask de sesión (Bit 851) y la paridad de datos.

## 2. Definición de Fase 2: Ingesta Asincrónica
Se esbozó la lógica de **Ingesta de CAE**:
- El sistema permitirá arrastrar el PDF de la factura emitida en AFIP o importar un CSV de "Comprobantes Emitidos" para automatizar el sellado de los borradores, eliminando el "copia-pega" manual.

## 3. Calibración Bipolar
Se revisó la lógica de filtrado en `PedidoList.vue`. El Bit 1024 (`NO_FISCAL_FORCE`) opera como el switch maestro entre los circuitos **Oficial (Esmeralda)** e **Interno (Índigo)**.

---
**Marcador de Sesión**: 2026-04-23_OMEGA_ESTRATEGIA_FISCAL
**Agente**: Antigravity (Gy V5)

---

# CAJA NEGRA: Siembra Contactos + Purga PostgreSQL (2026-04-19)

## 1. Variable de sistema Windows — la fuente real del problema
`DATABASE_URL=postgresql://postgres:Spawn8559@34.95.172.190:5432/postgres` estaba seteada a nivel de usuario en el registro Windows (`HKCU\Environment`). Esta variable pisaba cualquier `.env`, cualquier fallback en `database.py`, y cualquier override manual. Todos los scripts apuntaban a la nube sin excepción. Eliminada con `[System.Environment]::SetEnvironmentVariable('DATABASE_URL', $null, 'User')`.

## 2. IP `34.95.172.190` vs `104.197.57.226`
El sistema tenía dos IPs de Postgres distintas en diferentes archivos. `34.95.172.190` era la variable de sistema (Spawn8559). `104.197.57.226` era la de `backend/.env` (SonidoV5_2025). Ambas eliminadas. El stack opera 100% local.

## 3. Defensa en capas en `import_contactos_bulk.py`
El script ahora: (1) carga el `.env` raíz del proyecto vía `load_dotenv`, (2) si la URL resultante sigue siendo postgres, fuerza `sqlite:///pilot_v5x.db`. Esto hace al script inmune a contaminación de entorno sin importar qué haya en el sistema operativo.

## 4. Segregación notas en Persona (Person-Centric)
- `notas_globales`: texto visible para el operador (Carlos escribe, asigna tags)
- `notas_sistema`: auditoría del script (origen, % fuzzy match, cargo detectado, ENTIDAD_PENDIENTE)
Los dos campos son independientes para evitar que el audit sobreescriba notas comerciales.

## 5. Genoma de la siembra (10 contactos)
- flags=16 (solo Bit5): María E. Garrido, Joshua Sosa, Sebastián Fiorito, Facundo Ardissone, Ignacio Gonzalo
- flags=48 (Bit5+Bit6): Marcelo Massel, Agustina Verea, Matias E. Castelo, Carolina Papatanasi, Vanesa Vinciguerra
- 3 contactos con `[ENTIDAD_PENDIENTE: Rizobacter*]` — listos para vincular cuando se cree la empresa

---
**Marcador de Sesión**: 2026-04-19_OMEGA_SIEMBRA_SOBERANIA_LOCAL
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: Forense Git Tom + Diagnóstico DB CA (2026-04-18 — Sesión 2)

## 1. Remoto `produccion` eliminado de D
- D tenía configurado `produccion → v5-ls-Tom.git`. No era automático (CIERRE solo hace push a `origin`), pero era un vector de push manual. Eliminado con `git remote remove produccion`. D ahora tiene un único remoto: `origin`.

## 2. Tom's CIERRE.ps1 y OMEGA.md — sin cross-push
- Tom empuja a `prod` (remoto inexistente → falla silenciosa con `SilentlyContinue`). Sin riesgo.
- OMEGA.md de Tom: push a `origin` (Tom's own GitHub). Sin riesgo.

## 3. DB de Tom en CA — diagnóstico
- `data/V5_LS_MASTER.db` (CA): 9 pedidos, 37 clientes. Rubros con códigos numéricos pre-refactor (`'6'`, `'26'`, `'27'`). Sin LAVIMAR.
- DB con ~18 pedidos (OF real) está **atrapada en OF** — gitignoreada, nunca viajó. Hay que ir a buscarla físicamente o subirla al Drive.
- `.bak` del commit 13-Apr en git: sin tablas (WAL no checkpointed al commitear).

---
**Marcador de Sesión**: 2026-04-18_OMEGA2_FORENSE_GIT_TOM
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: Huérfanos + Alta de Rubro en Caliente + Adopción (2026-04-18)

## 1. Indicadores de Huérfandad (Bit 3)
- Dot neon `#24e70f` en tarjetas y listado. Borde verde en inspector. Filtro "Huérfanos" client-side.
- **Fix crítico**: `flags_estado` faltaba en `ProductoRead` → frontend recibía `undefined` → dots nunca aparecían.

## 2. Alta de Rubro en Caliente (F4)
- Modal ámbar desde el selector de Rubro. Backend genera `codigo` automáticamente (3 chars ASCII + sufijo numérico).
- `SelectorCreatable`: F4 siempre emite `create`. "Crear..." visible al fondo cuando hay texto.

## 3. Protocolo de Adopción V5.9
- Reasignación a cualquier rubro → Bit 3 limpiado silenciosamente en backend.
- Reasignación a General desde huérfano → modal de confirmación especial antes de guardar.

## 4. Fix Ciclo Reactivo (bug alto de rubro)
- `fetchRubros()` → reemplazo reactivo del store → watch `deep:true` disparaba `full-sync` borrando el form.
- Solución: `productosStore.rubros.push(newRubro)` directo + `localProducto.value.rubro_id = id`. Sin re-fetch.
- F10 ruteado: si modal abierto → `saveRubroFromModal`; si no → `save()` del producto.
- `showRubroModal` hoisted antes de los watches (fix Temporal Dead Zone).

## 5. Fix handleSave
- `ProductosView.handleSave` llamaba doble a `updateProducto`. Simplificado a actualizar lista local con resultado del inspector.

---
**Marcador de Sesión**: 2026-04-18_OMEGA_HUERFANOS_ALTA_RUBRO
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: Saneamiento Remitos (RAR-V1) + Resiliencia de Identidad (2026-04-16)

## 1. Saneamiento de Remitos (RAR-V1)
- **Flexibilidad de Datos**: Modificación de `schemas.py` y `models.py` para que `bultos` y `valor_declarado` sean opcionales (`nullable`).
- **QR Oficial**: URL actualizada a `https://liquid-sound.com.ar/` en el motor de PDF.
- **Estética de PDF**: Etiquetas fijas ("BULTOS:", "VALOR DECL.:") con valores condicionales para evitar ceros innecesarios.
- **Dirección Completa**: Integración de `@property resumen` en el modelo `Domicilio` para visualización unificada en remitos desde ingesta.

## 2. Resiliencia de Identidad (V5-LS)
- **Fix Reversión CUIT**: Implementación de sincronización soberana en `ClientCanvas.vue`. Tras validación ARCA, el CUIT corregido sobreescribe reactivamente el dato de Cantera durante el `updateCliente`.
- **Fix Error 500**: Null-safety inyectado en `_audit_sovereignty` de `service.py`. El sistema ya no crashea si un cliente importado carece de Condición IVA durante la auditoría de domicilios.
- **Blindaje 422**: Manejo de IDs nulos en persistencia de domicilios, redirigiendo correctamente a `POST` cuando el registro es nuevo.

## 3. Homologación de Entornos
- Sincronización binaria total de los módulos `clientes`, `remitos` y `Canvas` hacia el repositorio de producción `V5-LS`.

---
**Marcador de Sesión**: 2026-04-16_OMEGA_ESTABILIZACION_SOBERANA
**Agente**: Antigravity (Gy V5)

---

# CAJA NEGRA: Producción Soberana — Fixes Operativos + Diseño Doctrinal (2026-04-15)

## 1. Fix Domicilios — Triple Causa del 500
- **Kwarg duplicado**: `is_maps_manual` en `model_dump()` + constructor → `TypeError`. Fix: agregar al `exclude`.
- **Junction table**: `create_domicilio` no insertaba en `domicilios_clientes` (N:M). `GET /clientes/{id}` usa joinedload por esa tabla → domicilio invisible. Fix: `db.execute(domicilios_clientes.insert().values(...))`.
- **Pinia corruption**: `createDomicilio` en store hacía `splice(index, 1, response.data)` donde `response.data` es Domicilio, no Cliente → store corrompido → loop navegación. Fix: `client.domicilios.push(response.data)`.

## 2. Fix PedidoCanvas — Edit Mode
- `savePedido()` siempre llamaba `POST /pedidos/tactico`. En modo edición (route.params.id presente) debe llamar `PATCH /pedidos/{id}`. El endpoint PATCH ya existía y funcionaba — nunca se invocaba.
- Impacto: Tomy generó ~5 pedidos duplicados en producción. Limpiados manualmente en dos pasadas.

## 3. Fix Rosa Clients — clienteEsVerde
- Rosa: `(flags_estado & 15) in [9, 11]`. No tienen CUIT ni domicilio obligatorio. El computed `clienteEsVerde` los evaluaba igual que clientes formales → siempre rojo. Fix: detección `isRosa` + `return true` anticipado.

## 4. Migración GENERAL → General
- D: 4 prods migrados de rubro id=28 a id=26. P: 7 prods. `activo=0` en GENERAL (id=28) en ambas DBs.

## 5. Fix PedidoInspector — Nota invisible
- Botón ✏ editar nota tenía `opacity-0 group-hover/nota:opacity-100` → invisible. Fix: `text-yellow-500/50` siempre visible.

## 6. Diseño Doctrinal — Orígenes de Pedido (PENDIENTE implementación)
- La ingesta de facturas creaba pedidos en $0 silenciosamente (satisfy `pedido_id NOT NULL` en remitos). Mal.
- Diseño acordado: bits libres de `flags_estado` identifican el origen. `BIT_ORIGEN_FACTURA` (con respaldo AFIP, no anular livianamente). `BIT_ORIGEN_REMITO` (sin respaldo, pendiente de facturar).
- El Remito siempre tiene pedido padre (real o forzado). No hay "huérfanos" — son categorías de pedido.

---
**Marcador**: 2026-04-15_OMEGA_PRODUCCION_SOBERANA_FIXES
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: Saneamiento DB + Fixes Operativos + Paridad D/P (2026-04-14)

## 1. Cirugía DB — pilot_v5x.db
- **Objetivo**: Llevar D a paridad con P post-saneamiento productivo del 13/04.
- **7 fusiones ejecutadas**: grupos {156→179}, {176,186→172}, {169→6}, {170→149}, {171→175}, {173→177}, {152→161}. Pedidos re-apuntados (173→177, 159→175).
- **NULL SKU eliminados**: IDs 158, 159, 160 — borrados físicamente tras reapuntar pedido de 159 a survivor 175.
- **Limpieza física**: 8 productos borrados (flags=0 ó flags=2, sin movimientos). Estado final: **23 productos**.

## 2. Fixes Backend — Cantera Import
- **flags_estado=3**: Productos importados desde cantera ahora nacen con bits ACTIVE+VIRGIN seteados.
- **Auto-SKU**: Si el producto llega sin SKU del mirror, se asigna `MAX(sku)+1` con piso en 9001. Rango cantera: 9001+.
- **SKU Integer**: Conversión `int(float(sku_raw))` — maneja strings `"123"` y floats `"123.0"` del mirror JSON.
- **rentabilidad_target**: Fix de campo renombrado (ex `margen_mayorista`) que causaba 500 en importación.
- **Paridad D/P**: Mismo código aplicado en ambos entornos.

## 3. Fixes Frontend
- **F4 PedidoCanvas**: Apertura condicional corregida — product search tiene prioridad; modal cliente solo en foco explícito del campo cliente.
- **Rubro obligatorio ProductoInspector**: Asterisco rojo + ring de error + mensaje de validación `rubroError`.

## 4. Fixes Infraestructura
- **DESPERTAR.ps1**: Guard contra null reference cuando `.pasaporte_v5.json` no existe o Git no disponible. Mensaje informativo si no hay `.bak`.
- **boot_system.py**: `--reload-dir backend` (evita reload por writes de Vite). Health check polling vs `sleep(5)` fijo.
- **main.py (D y P)**: Ruta `/` → `/health` — libera el catch-all SPA para servir `index.html` en raíz.

---
**Marcador de Sesión**: 2026-04-14_OMEGA_SANEAMIENTO_DB_FIXES_OPERATIVOS
**Agente**: Claude Code (Sonnet 4.6)

# CAJA NEGRA: Remitos V5.8 GOLD & Productos Fase 1 (2026-04-10)

## 1. Resolución Logística Remitos
- **Problema**: Truncamiento de direcciones en ingesta ARCA.
- **Motor de Scoring (🪄)**: Algoritmo de comparación heurística para pre-selección automática de sedes legítimas (SSoT).
- **Alta Dinámica (➕)**: Persistencia reactiva de nuevas sedes de entrega directamente desde el flujo de ingesta.
- **Paridad P/D**: Sincronización absoluta de la lógica de resolución entre V5-LS y Desarrollo.

## 2. Modernización de Productos (Protocolo Alfa)
- **Diagnóstico**: Identificación de deuda técnica en IDs (Integers vs UUIDs).
- **Refactor Arquitectónico**: Extracción de lógica de negocio (SKU, Precios, Virginidad) a `service.py`.
- **Cierre Fase 1**: Routers saneados y centralizados en la capa de servicio.

---
**Marcador de Sesión**: 2026-04-10_OMEGA_REMITOS_PRODUCTOS_GOLD
**Agente**: Gy (Antigravity V5)

# CAJA NEGRA: Homologación Identity Shield V5.7 (2026-04-09)

## 1. Homologación Genoma V5-LS
- **Sincronización**: Paridad total entre Dev y Producción/Staging para el Protocolo Nike (Bag of Words).
- **Backend Master**: Inyección de `razon_social_canon` en `V5_LS_STAGING.db` y backfill de 35 registros legítimos.
- **Circuit Breaker**: Implementación de bloqueo por colisión canónica estricta (Bloqueo Nuclear).

## 2. Sensor UI Antigravedad
- **Componente**: `ClientCanvas.vue` en Staging actualizado con sensor reactivo debounced.
- **Auditoría**: Certificación `audit_production_duplicates.py` limpia. Estado: NOMINAL GOLD.

---
**Marcador de Sesión**: 2026-04-09_OMEGA_HOMOLOGACION_NIKE
**Agente**: Antigravity (Atenea AI)

# CAJA NEGRA: Blindaje Nuclear de Identidad (2026-04-08)

## 1. Protocolo Bag of Words V16.2
- **Lógica**: Refactor de `normalize_name` para ser insensible al orden de las palabras ("El Taller SRL" == "SRL El Taller").
- **Implementación**: Tokenización, eliminación de ruido (<2 chars), ordenamiento alfabético y sellado único.
- **Unificación de Siglas**: Saneo nativo de puntos en siglas ("S.R.L." -> "SRL").

## 2. Hémetización Estructural (Homologación P)
- **DB Master**: Inyección de columna `razon_social_canon` en `V5_LS_MASTER.db`.
- **Saneamiento**: Recanonización masiva de 37 registros en producción. 
- **Sincronización**: Paridad total de lógica entre entornos D (Desarrollo) y P (Producción).

---
**Marcador de Sesión**: 2026-04-08_OMEGA_BLINDAJE_NUCLEAR
**Agente**: Antigravity (Google DeepMind)

# CAJA NEGRA: Deudas Técnicas + Sync DB INAPYR (2026-04-02)

## 1. Sincronización de Base de Datos (CA → OF)
- Base CA reemplazó base OF. Backup: `pilot_v5x_PRE_CA_20260402.db`.
- Incorporado: INAPYR S.R.L. (CUIT 30714145351, codigo_interno 46), pedido INGESTA_PDF
  (factura 00001-00002514), remito con CAE `86139705410697` (vto 10/04), 2 domicilios La Plata.
- Canario post-migración: NOMINAL GOLD (flags 8205).

## 2. Auditoría flags_estado — BigInteger 64-bit
- 7 modelos activos: BigInteger confirmado. SQLite permisivo (INTEGER = hasta 8 bytes).
- Pydantic: `int` Python arbitrario. Sin validators de cap 32 bits.
- **Dictamen: Deuda ya resuelta. Cerrada sin cambios.**

## 3. Conexion_Blindada.py — OpenSSL desacoplado
- Antes: rutas absolutas hardcodeadas `C:\Program Files\Git\...`.
- Después: `OPENSSL_PATH` env var → `shutil.which("openssl")` → fallback Windows.
- `.env.example` creado en raíz con documentación.

## 4. Limpieza de Entorno — 37 Scripts Huérfanos
- Eliminados: debug_* (21), test_* (15), miner.py (1) de raíz, scripts/ y backend/.
- Conservados: `tests/test_v7_*.py` — pendiente revisión formal.
- Tesseract: confirmado ausente en requirements.txt.

---
**Marcador de Sesión**: 2026-04-02_OMEGA_DEUDAS_TECNICAS
**Agente**: Claude Code (Anthropic CLI)

# CAJA NEGRA: Burbuja Tomy V5-LS + Auditoría Seguridad (2026-04-01)

## 1. Auditoría de Seguridad npm
- Incidente real: Claude Code v2.1.88 con source map (~60MB) publicado por error en npm (31/03/2026).
- Instalación Carlos: nativa, no npm → no afectada. Versión activa: 2.1.89.
- axios en proyecto: 1.13.2 (no troyanizado). plain-crypto-js: no encontrado.
- Acción: eliminado binario obsoleto `claude.exe.old.*`.

## 2. Blindaje V5-LS (Puerto Unificado 8090)
- **main.py**: corregido `static_dir` path (faltaba un nivel `..` para llegar a `V5-LS/static/`).
- **LANZAR_V5_SOBERANA.bat**: eliminado `python -m http.server 5174`. Un proceso único en 8090 sirve API + SPA.
- **SATELITE_TOMY.bat**: actualizado a puerto 8090.
- **Login.vue (V5-LS)**: fix endpoint `:8000` → `api proxy`; fix texto blanco sobre blanco.

## 3. Fixes Dev Versionados (trabajo de Gy del 31/03)
- **ClientCanvas.vue**: UUID nulo al crear cliente (`emit` propagaba formulario sin ID del servidor).
- **PedidoCanvas.vue**: F10 bloqueado en modal (faltaba guarda `if (showClientModal.value) return`).
- **Login.vue**: puerto 8000 hardcodeado → `api.post('/auth/token')`; inputs sin color de texto.

## 4. Deuda Activa
- npm run build pendiente en V5-LS antes de que Tomy opere en producción.

---
**Marcador de Sesión**: 2026-04-01_OMEGA_BURBUJA_TOMY
**Agente**: Claude Code (Anthropic CLI)

# CAJA NEGRA: Operación Vanguardia V5-LS (2026-03-30)

## 1. Reestructuración de Infraestructura
- **Directorio Raíz**: Desmantelado `V5_RELEASE_09` ➔ Elevado a `V5-LS`.
- **Jerarquía Soberana**: Segmentación en `current/`, `data/`, `archive/`, `shared/` para independencia modular.

## 2. Movimiento de Activos y Limpieza
- **Código Fuente**: Despliegue de backend y frontend en `current/`. Purga física de `venv` y `node_modules`.
- **Base de Datos**: Migración de `pilot_v5x.db` a `V5_LS_MASTER.db` (568 KB Nominal Gold).
- **Credenciales**: Centralización de `Clave-Jason.jason` en `shared/credentials/`.

## 3. Configuración de Soberanía
- **Network Stack**: Puerto **8090** asignado.
- **Environment Logic**: Inyección de rutas absolutas en `.env` para bypassear fallos de ruta relativa en LAN.

---
**Marcador de Sesión**: 2026-03-30_OMEGA_VANGUARDIA_V5LS
**Agente**: Gy (Antigravity V5 - Atenea)

# CAJA NEGRA: Sesión Entrega V5-LS Tomy (2026-03-27)

## 1. Network & Routing
- **Puerto 8090/5174**: Definición de arquitectura dual para evitar colisiones en LAN IP 192.168.0.34.
- **Ruta Hardcodeada (Bug)**: Localización de `pilot_v5x.db` forzado en el arranque. Se devolvió la soberanía al `.env`.
- **Axios Absolute Fix**: Reemplazo de `/clientes` por `http://192.168.0.34:8090/clientes` en assets minificados.

## 2. Integridad de Datos
- **Purga Master**: Eliminación de SKUs de prueba (Agua/Soda) y reseteo de `sqlite_sequence`.
- **Censo de Clientes**: Verificación de 32 registros legítimos en la base de producción final.

---
**Marcador de Sesión**: 2026-03-27_OMEGA_SUPREMO_FINAL
**Agente**: Gy (Atenea AI)

# CAJA NEGRA: Sesión Perfección Soberana V5.5 GOLD (2026-03-26 Parte 2)

## 1. Movimiento de Bits y Genoma
- **Bit 6 (OC_REQUIRED)**: Implementación de Poka-Yoke visual (Neon Blue) y validación en PedidoCanvas.
- **Bitwise Logic**: Calibración en Frontend para diferenciar obligatoriedad de asterisco vs borde neón.

## 2. Intervención en el Núcleo (Backend)
- **Decimal Fix**: Refactorización de 8 puntos en `backend/pedidos/router.py` usando `Decimal(str(item.cantidad))` para evitar TypeErrors con floats.
- **ProductoCosto Extensions**: Inyección de `costo_reposicion` y `margen_sugerido` en modelos y esquemas Pydantic.

## 3. Persistencia Física y UI
- **PedidoCanvas (Ficha #ID)**: Transformación en "Ficha del Pedido" con título dinámico e hidratación mejorada.
- **Rentabilidad Dinámica**: Panel F8 migrado de estático a dinámico con lógica de cálculo viva sobre `items`.
- **Keyboard Optimization**: Secuencia de foco `Cliente -> OC -> SKU` (Hoja de cálculo mode).
- **Hotfix**: Blindaje de `RentabilidadPanel.vue` con guardas contra `undefined reduce`.

---
**Marcador de Sesión**: 2026-03-26_OMEGA_GOLD_SYNC_V8_6
**Agente**: Gy (Antigravity V5 - Atenea)

# CAJA NEGRA: Sesión Perfección Soberana V5.2 GOLD (2026-03-25 Parte 3)

## 1. Movimiento de Bits y Genoma
- **Bindings N/M**: Planeamiento estratégico documentado en `ANALISIS_TRANSPORTE_LOGISTICA.md` para integrar `EmpresaTransporte` y `NodoTransporte` en los domicilios del `Cliente`.

## 2. Intervención en el Núcleo (Backend)
- **Pydantic Property Forcing**: Implementación de `@property cliente_id` expuesta llanamente en `RemitoResponse` para bypassear las limitaciones de lazy-load de SQLAlchemy sin incurrir en N+1 Queries.
- **Client Mapping Fix**: Mapeo riguroso de `payload.cliente.id` en el Router de ingesta de facturas, eliminando la creación colateral de cuentas "Desconocido".
- **Cascaded Eradication**: Adición de `DELETE /remitos` con purga lógica del remito e interceptación física de eliminación en cascada para su Pedido de origen (sólo si es `INGESTA_PDF`).

## 3. Persistencia Física
- Cambios frontend directos en `RemitoListView.vue` inyectando botones de estado (Imprimir) y cierre (Trash) con reestructuración visual Poka-Yoke.

---
**Marcador de Sesión**: 2026-03-25_OMEGA_GOLD_SYNC_V3
**Agente**: Gy (Antigravity V5 - Atenea)
