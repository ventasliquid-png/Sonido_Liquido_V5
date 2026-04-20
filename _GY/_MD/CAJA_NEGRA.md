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
