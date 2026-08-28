## SESION 856 (OF): CIERRE RETROACTIVO DE S855 (CA, 15/08) + FIX REAL DE CARD #93

**Fecha:** 2026-08-24 (cierre retroactivo -- la sesion 855 real ocurrio el 2026-08-15 en CA)
**Locacion:** cierre en OF
**Estado:** NOMINAL GOLD - Hash B: a732e6c (sin cambios) | Semaforo CS: [pendiente] | PIN 1974

### Hito 1: Descubrimiento de la brecha de fecha (CC)
* Al preguntar la fecha real del sistema: 2026-08-24, diez dias despues de lo que toda la sesion anterior asumia como "hoy". Verificado con `date`/`Get-Date`, no solo con archivos del Silo.
* Cruce de evidencia (git fetch, mtimes reales, API de Drive) confirmo Sesion 855 en CA (15/08), mas moderna que la nuestra y nunca cerrada.

### Hito 2: Contenido real de Sesion 855, verificado antes de narrarlo (CC + CS)
* CA pulleo a los hashes de cierre de S854, arreglo Card #93 en su disco (sin commitear), hizo recorrido completo del Board (17 escrituras, cards #106-115, duplicados resueltos, #21 reabierta).
* Canonizo 4 entradas en BIBLIOTECA_NIKE.md (21->26 encabezados, verificado independientemente hoy).
* Hallazgo central: de 5 decisiones a canonizar, 3 no tenian respaldo en disco (Genoma Cliente 30/07, C2/C3, "Regla A/B") -- venian de memoria de CS, descartadas antes de escribirlas como canon.

### Hito 3: Fix real de la herramienta (CC)
* `scripts/update_board.py` linea 6: `wb.active` -> `wb['Board V5']` explicito + verificacion de relectura post-guardado. Probado con escritura inocua antes de usarlo en serio.
* CA tiene el mismo fix sin commitear -- pendiente de reconciliar, no duplicar.

### Hito 4: Tres cards nuevas, halladas releyendo el propio protocolo (CS)
* #116: checkbox de Manuales en OMEGA permite vaciar contenido real con "sin cambios esta sesion".
* #117: fast-path de ALFA usa hash de codigo como proxy de integridad de datos -- no detecta drift de schema.
* #118 (CRITICA): canario de OMEGA FASE 1 hardcodeado a `pilot_v5x.db` -- confirmado que `C:\dev\v5-ls-Tom\OMEGA.md` tambien lo tiene, mismo patron que mato el backend de Tomy en S851.

### Hito 5: Cierre honesto, no maquillado (CC)
* Manuales de esta sesion NO se tildaron "sin cambios" -- se declaro explicitamente que la revision de contenido no se hizo (mismo checkbox que denuncia #116, no se repite el patron en el propio cierre que lo crea).
* CA no declaro territorio en S855 -- no se corrige a ciegas desde OF, queda pendiente en `SESION_NEXT.md`.

D:29e2bf0b B:a732e6c | PIN: 1974

---

## SESION 854 (OF): BR#8 CERRADA POR PRECEDENTE, BOARD RECONCILIADO, DIAGNOSTICO REMITO PARCIAL SIN FIX

**Fecha:** 2026-08-14
**Locacion:** cierre en OF
**Estado:** NOMINAL GOLD - Hash B: a732e6c (sin cambios) | Semaforo CS: VERDE | PIN 1974

### Hito 1: Verificacion de OMEGA de S853 (CC)
* Cruzados 5 indicadores documentales -- SI hubo OMEGA formal el 10/08; BR#8 quedo abierta a proposito, no por un cierre incompleto.

### Hito 2: BR#8 cerrada por evidencia de hash -- precedente sentado (CC + Carlos + CS)
* Criterio literal (hash Y arbol limpio) estructuralmente incumplible: MT rebuildea en cada arranque, current/static/index.html trackeado.
* Investigacion documental previa confirmo que el precedente de BR#4/Card #87 pesaba en contra de destrackear static/, no a favor -- static/ es lo que FastAPI sirve.
* Cerrada con evidencia de hash consistente 9 dias sin error, con salvedad explicita: codigo confirmado en el checkout de MT, build servido y E2E real no verificados hoy.

### Hito 3: Board reconciliado (CC)
* Card #102 (S853) nunca habia llegado al Board -- segunda perdida confirmada del bug wb.active (Card #93 -> ALTA). Escrita verbatim.
* Cards #103/#104/#105 creadas (angostar arbol_limpio; redundancia rebuild MT vs cherry-pick, Nike; canonizacion de dictamenes de Nike, proceso).

### Hito 4: Diagnostico del remito parcial -- causa real, sin fix (CC)
* cantidad_entregada confirmado expuesto con JSON real de Pedido #63 (100/50, Bit20 ON). Hipotesis de dato faltante descartada.
* Causa real de frontend: ManualRemitoView.vue auto-completa sin paso de seleccion; PedidoList.vue no renderiza cantidad_entregada por renglon ni oc, aunque los recibe.
* Hallazgo no buscado: pipeline de aviso "FALTA REFERENCIA OC" en PedidoInspector.vue inerte -- backend nunca envia cliente.oc_required. Bit 6 de Cliente muerto en las dos lecturas (OC_REQUIRED codigo, TRUSTED_MANUAL doctrina).
* Decision de Carlos: sandbox con datos de produccion en D descartado, no postergado -- Pedido #63 alcanza.

### Hito 5: Housekeeping (CC)
* session_counter.json aparecio en 0 (mismo sintoma de S853, causantes ya no existen en disco). Descartado, corregido a 854.

D:f65e8048 B:a732e6c | PIN: 1974

---

## SESION 853 (OF): OMEGA COMPLETO - HASHES STALE, CALLEJON DEL SHARE DE MT, REPORTE AUTOMATICO DE ESTADO, BR#8

**Fecha:** 2026-07-25 -> 2026-08-10 (16 dias, 3 maquinas)
**Locacion:** cierre en OF
**Estado:** NOMINAL GOLD - Hash B: a732e6c | Semaforo CS: AMARILLO | PIN 1974

### Hito 1: ALFA sobre sesion de 16 dias - hashes stale corregidos (CC)
* Fast-path denegado: hash local de D (`5a3677d6`) != `hash_D` registrado (`b43647f0`). FASE 1 completa.
* `SISTEMA_STATUS.json.OF` nunca se actualizo tras los push del 05/08 - el campo global `ultimo_hash_D_en_B` si, el bloque de maquina no. **Mismo error exacto que causo la crisis de identidad de CA del 03/08**, repetido siete dias despues.
* Edge Case A: stale lock de 6d 16h saneado. `timeout_minutos` sigue ausente del JSON pese a estar en doctrina (segundo arranque consecutivo que lo detecta).

### Hito 2: Acceso de red a MT - callejon cerrado con causa raiz (CC)
* Tres intentos. El share existe y responde, pero la reinstalacion de Win11 del 31/07 vacio el almacen de credenciales y la cuenta de MT no tiene contrasena: Windows rechaza SMB por politica de cuentas con clave en blanco.
* Descartado destrabarlo - implicaria desactivar una politica de seguridad en la maquina de produccion para una consulta de solo lectura. WinRM tampoco: `TrustedHosts` ni existe en la maquina reinstalada.

### Hito 3: MT reporta su propio estado - solucion estructural (CC)
* `espejo_mt.py` (Silo, fuera de git, fuera del flujo D->B->MT) ahora escribe `ESPEJO_MT/estado_mt.json` con hash, rama, ultimo commit, arbol limpio, archivos sucios y hostname, en cada corrida de su tarea programada en MT.
* Solo lectura sobre el repo, envuelto en `try/except` total, colocado **antes** del backup a proposito. Probado en cuatro frentes incluidos tres caminos de falla y dry-run completo.
* Cierra el hueco de que el estado de produccion solo se podia averiguar yendo fisicamente (Card #96).
* **Riesgo detectado y no resuelto:** el script no tiene guarda de maquina - correrlo sin `--dry-run` en OF sobrescribiria el espejo de MT con la base de prueba local.

### Hito 4: El hallazgo del Board y la BR#8 (CC + CS)
* BR#7 fue cerrada el 05/08 17:41 reportando pull a `a732e6c` y E2E completo en MT real, **pero sin fila en `BITACORA_VIVA.md`** - la bitacora de esa tarde corta a las 16:55 en 'pendiente PIN 1974 para MT'.
* El **Bit 7 (`BOARD_PENDIENTE`) estaba encendido** y se reporto como dato decodificado sin ir a mirar el Board, que tenia la respuesta a la pregunta que ocupo el dia.
* Evidencia corroborante hallada en disco: backup de la base real de MT escrito a las 17:51 (75/54/31, mismo linaje que el espejo) y `ultima_actualizacion` del JSON a las 17:41. Tres artefactos en esa franja.
* **BR#8 abierta** (unica activa): el hash del codigo en MT hoy sigue sin confirmar. Cierra sola con el primer `estado_mt.json`. `ultimo_hash_B_en_P` se dejo en `edaf219` deliberadamente.

### Hito 5: Housekeeping con causa (CC)
* `fix_status.py` y su copia `_PELIGRO_` no eran sueltos inertes: es un script de S842 que sobrescribe `SISTEMA_STATUS.json` con valores hardcodeados de julio. Correrlo habria revertido la correccion de hashes de esta misma sesion.
* Card #101 reclasificada de BAJA a real: los tres lanzadores abortan sin `data\V5_LS_MASTER.db` aunque el backend lea `current/`.
* `session_counter.json` corregido de 1 a 853. `.claude/launch.json` ignorado. `pyvenv.cfg` revertido en B.

---

## SESIÓN 852 (OF): CARD #100, DIAGNÓSTICO WinRM BLOQUEADO, CERTIFICACIÓN OMEGA/MT POR OTRA VÍA

**Fecha:** 2026-07-24
**Locación:** OF
**Estado:** NOMINAL GOLD — Hash D: 6bcf1057 (sin commit de código nuevo) | Hash B: edaf219 | PIN (pendiente FASE 3)

### Hito 1: Card #100 — diseño de Espejo/copia offline de MT (CC)
* Confirmado #99 como último ID leyendo `BOARD_V5.xlsx` real antes de numerar.
* MEJORA, MEDIA: mecanismo de actualización periódica (checkpoint ~30 min vía Task Scheduler) de una copia de solo-lectura de `V5_LS_MASTER.db` en el Drive, para consulta offline. Descartado copiar en cada movimiento A/B/M (riesgo de inconsistencia WAL/locking). Pendiente investigar si `backup_db.py` ya usa la API de backup online de SQLite antes de construir un mecanismo nuevo.

### Hito 2: Intento de cierre remoto de OMEGA/MT vía WinRM — bloqueado (CC)
* A pedido de Carlos, se intentó cerrar la deuda de Bit 19 de MT (abierta desde S846) ejecutando el checklist de certificación por `Invoke-Command` remoto desde OF contra `192.168.1.2`. `Test-WSMan` respondió OK, pero `Invoke-Command` falló: este cliente no tiene `192.168.1.2` en `TrustedHosts` — necesario porque ambas máquinas están en workgroup, no en dominio.
* Configurar `TrustedHosts` es un cambio de configuración de seguridad del sistema — CC no lo ejecutó unilateralmente, reportó el comando exacto a Carlos y pidió definición de credenciales para continuar. No se tocó `Bit19` ni `omega_cerrado` de MT en ese momento — la deuda quedó explícitamente abierta hasta tener evidencia real.

### Hito 3: Certificación OMEGA de MT completada por otra vía (S852-MT)
* MT terminó certificando su propio OMEGA — no vía el WinRM bloqueado, sino corrida directa en la máquina real (hostname "Izquierda"). Los 4 puntos verificados: canario NOMINAL GOLD, WAL checkpoint PASSIVE con un uvicorn de producción real corriendo (sin tocar el proceso), `backup_db.py` (encontró y corrigió un bug real: `FUENTES["MAESTRO"]` apuntaba a una copia en el Silo que nunca existió ahí, ni en MT ni en OF — fix con el mismo patrón `_env_db` de `canario_v2.py`), hash de git `edaf219` confirmado. `Bit19` apagado, deuda de varias semanas (desde S846) saldada.

### Hito 4: Verificación de limpieza git pedida por Carlos antes de cerrar (CC)
* `git status` en D y B confirmado limpio en ambos — sin commits ni cambios sin pushear de la sesión. Único hallazgo: los 3 archivos sueltos sin trackear en D, todos preexistentes de S851 (`audit_results.txt`, `audit_results_utf8.txt`, `_PELIGRO_fix_status.py`, ya documentados en Card #98) — ninguno nuevo.

---

## SESIÓN 851 (OF): CIERRE BR#5/BR#6, CAUSA RAÍZ BACKEND DE TOMY CAÍDO, INVESTIGACIÓN PEDIDO/REMITO

**Fecha:** 2026-07-23
**Locación:** OF
**Estado:** NOMINAL GOLD — Hash D: 42857e8f | Hash B: edaf219 | PIN 1974

### Hito 1: Cierre de las dos Banderas Rojas abiertas desde S850 (CC + Carlos)
* BR#5 (fork Bit 20 Clientes): propagación a MT confirmada — `LANZAR_V5_SOBERANA.bat` corrido por Carlos en MT trajo el pull, y la reparación de datos de clientes se verificó con un `SELECT` directo sobre `V5_LS_MASTER.db` real: Bit20 ON pasó de 7 a 1 — único caso genuino restante "Cecilia Pascual" (confirmada sin domicilio vinculado).
* La reparación sí tuvo PIN 1974 + backup previo (`data\V5_LS_MASTER_backup_pre_BIT20_MT_20260723_124953.db`, confirmado) + dry-run, autorizada por Carlos en chat — no quedó registrada en archivo en el momento, se reconstruyó y registró retroactivamente hoy. No fue `migrate_pin1974.py` (intacto desde 27/05) sino un script ad-hoc nuevo — decisión: no se versiona, cumplió su función puntual.
* BR#6 (auto-push de MT): confirmada resuelta — MT en `edaf219` incluye el commit del veto (`58c5d49`).

### Hito 2: Causa raíz del backend de Tomy caído dos veces hoy (CC)
* `current/scripts/canario_v2.py` en B era un duplicado legacy (sin tocar desde 2026-05-29) hardcodeado a la ruta de D. En MT esa ruta no existe → `calibracion_constitucional()` siempre fallaba → `radar_electrico()` encontraba "uvicorn" en el commandline del backend real → `espolon_defensivo()` lo mataba con `taskkill /F`. Eliminado el duplicado.
* La copia viva (`scripts/canario_v2.py`, tanto en D como en B) migrada a `scripts/_env_db.detectar_entorno_db()` (Card #93-bis) en vez de mantener una tercera lógica de detección de entorno en paralelo.
* IP muerta `192.168.0.34` (subred vieja de MT) en `scripts/ARRANQUE_V5.bat` corregida a `localhost`; chequeo de existencia de `data\V5_LS_MASTER.db` agregado (antes arrancaba a ciegas). Banner de "modo emergencia" agregado a `ARRANCAR_TOMY.bat` (el fallback real que se usó hoy mientras se investigaba — no actualiza código ni rebuildea frontend).
* Verificado en producción real: Carlos corrió `LANZAR_V5_SOBERANA.bat` en MT — cargó actualizaciones y abrió el sistema sin colgarse.

### Hito 3: Investigación de modelo — Remito/Factura complementario sobre el mismo Pedido (CC, sin fix)
* A pedido explícito de Carlos (caso real: pedido cargado con 6 E2 en vez de 9 E2, ya facturado y remitado por Remito #16), se investigó si el sistema soporta un segundo Remito/Factura complementario preservando la traza de lo ya entregado.
* Confirmado con evidencia de código: `Remito.pedido_id`/`Factura.pedido_id` son FK 1:N reales sin `unique`; `FacturaRemito` es una tabla puente N:M diseñada explícitamente para "split de pedidos, consolidaciones, re-facturación" (docstring propio). `PedidoItem.cantidad_entregada` + Bits 20/21 (`HAS_PARTIAL_DELIVERY`/`FULL_DELIVERED`) están vivos y conectados en `create_manual`. Bits 22/23 (facturación parcial) están reservados en el genoma sin lógica general detrás.
* Hallazgo real: `PATCH /pedidos/{id}` con `items` (usado por `PedidoCanvas.vue`, la pantalla estándar de edición) borra y recrea `PedidoItem`, cascadeando `DELETE` sobre los `RemitoItem` vinculados — destruye la traza de entregas parciales al corregir un pedido. Existe una vía no-destructiva ya en el código (`PATCH /pedidos/items/{item_id}`) pero no conectada al flujo de guardado principal.
* Card #99 creada (DEUDA, MEDIA) — sin diseño ni decisión tomada, queda para sesión futura (posible consulta a Nike sobre cuándo usar cada vía).

### Hito 4: Hallazgo de proceso — burocracia de cierre de S850 nunca commiteada (CC)
* `CAJA_NEGRA.md`, ambos Manuales, este mismo archivo, `.pasaporte_v5.json` y `session_counter.json` quedaron editados en disco tras el cierre de S850 (su FASE 2 sí se corrió) pero nunca se agregaron a un commit — el único commit de aquel cierre (`775216e1`) fue el de código. Contenido verificado correcto contra la narrativa ya conocida, conservado y sumado en el commit de cierre de esta sesión, no descartado.

### Hito 5: Precaución evitada — ejecución remota sin supervisión (CC)
* Antes de disparar `Invoke-Command` remoto contra MT para correr `LANZAR_V5_SOBERANA.bat` sin nadie presente, CC frenó y pidió confirmación explícita — mismo precedente documentado en S850 (misma pregunta de Carlos, misma respuesta) más un riesgo técnico concreto: el script tiene un `pause` interactivo y abre una consola vía `start`, ninguno de los dos pensado para correr bajo una sesión WinRM no interactiva. Carlos terminó corriéndolo él mismo, de forma física/propia.

## SESIÓN 850 (OF): PURGA DE FORK DE DOCTRINA BIT 20 CLIENTES + AUTOAUDITORÍA OMEGA

**Fecha:** 2026-07-20/22 (sesión abierta 20/07, cerrada 22/07 tras pausa sin OMEGA de por medio)
**Locación:** OF
**Estado:** NOMINAL GOLD (con Bandera Roja #5 abierta) — Hash D: 775216e1 | Hash B: 32f630a | PIN 1974

### Hito 1: Housekeeping de arranque (CC)
* Lock fantasma de agente en MT limpiado (`agente_activo`/Bit8), sin tocar el debt separado de Bit19 de MT.
* OC editable agregada al modal "Editar Remito" (`RemitoListView.vue`), reusando `pedidosStore.updatePedido()`. D `f5bdb53a` / B `371b04d`.
* `PEDIDOS_ESPEJO_DEV.xlsx` verificado correcto — no era bug.

### Hito 2: Acceso de red directo OF→MT (CC)
* Primer acceso habilitado vía share `\\Izquierda\dev` — requirió cambiar el perfil de red de Público a Privado y resolver credenciales SMB (sesión invitado vs autenticada) más permisos NTFS.
* Permitió verificar por lectura directa (no inferencia) que `ARRANQUE_V5.bat` de MT coincide con lo versionado, y que el auto-push de MT a `prod/main` es una feature deliberada (commits `7e608a1`/`a9ebe18`) que contradice la Regla de Hierro — reportado, sin resolver.

### Hito 3: Fork de doctrina de 4 meses — Bit 20 Clientes (CC)
* Catalogando archivos sueltos en MT apareció `migrate_pin1974.py`, que reveló dos significados opuestos del Bit 20 de `clientes.flags_estado` activos simultáneamente en producción: `PENDIENTE_REVISION` (V14, marzo) vs `ARCA_OK` (V15.1, posterior) — con al menos un cliente real mal clasificado (Cecilia Pascual, en D y MT).
* Nike dictaminó unificar a `PENDIENTE_REVISION`. Purga ejecutada en un solo commit (doctrina + backend + frontend) en D y B: `GENOMA_MASTER.md`, `BITS_CLIENTES.md`, `GENOMA_UNIVERSAL.md`, `backend/clientes/service.py`, `ClientCanvas.vue`, `HaweView.vue`, `ManualRemitoView.vue`.
* Error de cherry-pick detectado y corregido antes de pushear: 3/7 archivos habían aterrizado en árboles legacy de B (`frontend/` raíz, `staging/`) en vez de `current/` — revertido, recopiado a la ruta correcta, verificado con build real en D y B antes de commitear.
* Falta propagar a MT (PIN 1974, máquina apagada) y correr el script de reparación de datos para clientes ya mal clasificados (separado del commit de código, no ejecutado). Registrado como Bandera Roja #5, `ABIERTA`.

### Hito 4: Numeración de sesión reconstruida con evidencia (CC)
* A pedido explícito de Carlos, no se asumió el número por simple incremento: reconstruido cruzando `git log` de D/B contra `BITACORA_VIVA.md`/`INFORMES_HISTORICOS/` — confirmada 850, no la estimación inicial de 851. `session_counter.json` (huérfano, sin consumidor real) reparado de todos modos de `{count:0}` a `{count:850}`.
* Hallazgo honesto: la reconstrucción completa fue innecesaria — `_GY/_MD/CAJA_NEGRA.md` línea 1 ya tenía la respuesta ("Sesión actual: 850") desde el principio.

### Hito 5: Autoauditoría OMEGA y remediación (CC)
* A pedido de Carlos ("revisá Omega en Q y decime si cumple"), auditoría honesta contra el texto literal de `OMEGA.md` V3.3 — reveló brechas reales: Canario/WAL/backup/Excel de cierre nunca corridos, Bits 20-28 de agentes no recalculados, `actualizar_card000.py` no corrido (Card #000 stale), Manuales/`BITACORA_DEV.md`/`BANDERAS_ROJAS` no actualizados, falta rama `backup/` pre-push, formato de commit no conforme.
* Remediación en orden de prioridad fijado por Carlos: A) integridad de datos (Canario `OK`, WAL checkpoint `OK`, `backup_db.py`, `exportar_pedidos_excel.py` — todo corrido limpio); B) honestidad de estado (Bits 20-28 recalculados uno por uno — Bit22/GY encontrado prendido sin motivo, apagado; `actualizar_card000.py` corrido, semáforo bajado honestamente a `🔴 BANDERAS ROJAS` por la Bandera Roja #5 abierta); C) reconocido sin reescribir historia (rama `backup/` faltante y formato de commit no conforme — aplicar correctamente de acá en adelante, no retrofit); D) Manuales técnico/operativo actualizados, `BANDERAS_ROJAS` con fila nueva, FASE 4 verificada limpia, FASE 7 confirmada N/A (Gy no participó).
* Bug de secuencia autocapturado antes de ejecutar: `actualizar_card000.py` casi corre con `CAJA_NEGRA.md` ya en "851", lo que hubiera hecho que Card #000 mintiera la sesión siguiente como la actual — revertido temporalmente a "850", corrido, restaurado a "851".
* Gaps residuales detectados en una segunda pasada de autoverificación tras pregunta directa de Carlos ("¿está cumplido el Omega?"): `CONTEXTO_CS/` nunca regenerado y Bits 16-18 (semáforo CS) apagados pese a la Bandera Roja #5 — corregido (Bit18 ON, `generar_contexto_cs.py` corrido, semáforo `ROJO` real); esta misma bitácora (`BITACORA_DEV.md`) nunca abierta pese a estar en el pedido — corregido con esta entrada.

## SESIÓN 849 (OF): RECONCILIACIÓN D↔B, HISTORIAL DE NOTAS, REORGANIZACIÓN DEL SILO, CIERRE BR#4
**Fecha:** 2026-07-14/15 (sesión accidentada — corte de luz a mitad, retomada sin pérdida de contexto)
**Locación:** OF
**Estado:** NOMINAL GOLD — Hash D: 8429cb14 | Hash B: e3424a6 | PIN 1974

### Hito 1: Auditoría profunda del sistema (CC)
* Relevamiento completo de 17 Informes Históricos + Board (94→98 filas) + BANDERAS_ROJAS + panel. Hallazgo mayor: Cards #47/#48/#51/#52 resueltas en D desde hace un mes pero marcadas BACKLOG en el Board — verificado contra código real, no contra memoria del Board.
* Bit 40 (DISCRIMINA_IVA) investigado: presente en D y B, byte-idéntico. Poblet/Centro Pet deberían tenerlo ON (son Responsables Inscriptos) pero está OFF por edad de registro — no es bug, es backfill pendiente desde antes de la canonización de la regla.
* Card #44 rescatada: título vacío escondía el registro completo del fix de BR#3 (PIN 1974) — a punto de perderse en una limpieza futura de cards vacías.

### Hito 2: Reconciliación D↔B de `exportar_pedidos_excel.py` (CC)
* La detección de entorno (TOM/DEV vía `.env`) existía solo en B (`_detectar_entorno()`); D seguía con `argparse --entorno` + `DB_PATH` hardcodeado. Extraída a `scripts/_env_db.py` compartido, sin dependencia de `openpyxl`, para no duplicar la lógica una tercera vez.
* Verificado con ejecución real en ambos repos: D resuelve DEV desde su `.env` real (no un stub simulado), B sigue resolviendo TOM sin regresión.
* Hallazgo colateral: 4 callers (`execute_omega.py`/`omega_closure.py` en D y B) invocaban el script con un flag `--entorno` que en B llevaba meses siendo silenciosamente ignorado (Python no falla con argumentos extra si el script no usa `argparse`). Corregidos los 4, y `OMEGA.md` de ambos repos (documentaba el flag viejo).

### Hito 3: Feature "Historial de Notas" — canal CSV para MT (CC)
* Diseño iterado en 3 rondas con Carlos hasta viabilidad confirmada: hoja oculta + fórmulas de detección de cambios (descartado — fragilidad de versión de Excel) → hoja visible "Historial de Notas" dentro del mismo Excel (descartado — riesgo de pérdida en el full-overwrite del generador) → **CSV real separado**, con failover A/B, sync disparado por ALFA en MT con PIN 1974 como alerta+autorización en un solo paso.
* `scripts/sincronizar_historial_notas.py` (D→B, idéntico): `verificar_pendientes()`/`aplicar_sincronizacion()`, dedup por `(pedido, fecha/hora, nota)`, huérfanos (pedido no encontrado) reportados y nunca aplicados ni descartados silenciosamente.
* Bug real encontrado en prueba end-to-end aislada, antes de commitear: cuando la misma nota aparecía duplicada en A y B, solo se marcaba `Sincronizado` en el archivo que ganaba el dedup — el otro reaparecía como pendiente en la corrida siguiente, arriesgando duplicar el append en la DB. Corregido agrupando todas las ubicaciones por clave antes de marcar.
* Smoke test real (no simulacro aislado) contra la copia local de B (`current/V5_LS_MASTER.db`, snapshot S847, nunca la real de MT): detección → reporte → PIN 1974 → aplicación → verificación por query SQL directa → confirmación de que no reaparece. Nota de test en Pedido #2 de esa copia queda como evidencia intencional, no revertida (decisión explícita de Carlos).

### Hito 4: Reorganización del Silo — carpetas D\/B\/P\ (CC)
* Carpetas creadas para separar lo específico de cada entorno; migración de lo ya suelto en raíz queda como Card #98, sin ejecutar hoy salvo los casos evidentes.
* Inventario completo de la raíz — hallazgo importante: `CA/` y `OF/` ya tenían una estructura `D/`/`P/` por **máquina**, de mediados de mayo, abandonada dos meses, con bases reales de la Sesión 807 adentro. Anidada en `_LEGACY_MAQUINA_MAYO/` sin tocar el contenido.
* Resuelto en 6 puntos: basura borrada sin PIN (locks de Excel, dumps viejos de Board), 4 handoffs sueltos → `INFORMES_HISTORICOS/`, `PEDIDOS_ESPEJO.xlsx` + 4 timestamped (huérfanos, pre-reconciliación) → `D\`, `PEDIDOS_ESPEJO_TOM.xlsx` + los 3 `.bat` de arranque de MT → `P\` (los tres confirmados con evidencia — apuntan a `git pull prod main`, migraciones, puerto de Tomy).
* Corrección de rumbo a mitad de camino: los `HISTORIAL_NOTAS_TOM_*.csv`/`PEDIDOS_ESPEJO_TOM.xlsx` se habían puesto en `B\` en la primera pasada — corregidos a `P\` cuando Carlos aclaró el criterio ("la carpeta sigue al dato de producción, no al código que lo genera").

### Hito 5: Dictamen Nike sobre BR#4/Card #87 — `dist/` fuera del tracking (CC)
* Antes de ejecutar: confirmación con evidencia real de que `ARRANQUE_V5.bat` (el que efectivamente llega a MT vía `git pull`) rebuildea el frontend localmente comparando `git rev-parse HEAD` contra `.build_hash` — confirmado que ese marcador **no está versionado en git** (diseño correcto para que gitignorar `dist/` sea seguro). Encontrado además el precedente histórico exacto: Informe S843 documenta que `dist/` trackeado causó un ciclo de auto-bloqueo que atrasó MT 13 commits — la causa raíz que este fix corrige.
* `git rm -r --cached current/frontend/dist/` en B — 43 archivos, verificado con `git check-ignore` que la regla del `.gitignore` (que ya existía pero nunca tuvo efecto retroactivo) ahora sí los cubre. `current/static/` (lo que realmente sirve FastAPI) sin tocar.
* Card #87 y las 4 filas de `BANDERAS_ROJAS` cerradas con la evidencia completa — primera vez en varias sesiones con 0 banderas rojas activas en el sistema.
* Dos cards nuevas sin bloquear el cierre: `.build_hash` nunca persiste en MT en la práctica (cada arranque rebuildea completo, bajo impacto — Card #96), `static/assets/` acumula bundles viejos sin purgar (`xcopy` no borra huérfanos — Card #97).

### Hito 6: Reconciliación de `OMEGA.md` — 3 copias divergentes (CC)
* Encontrado al arrancar el cierre de esta sesión: el `OMEGA.md` canónico del Silo y la copia local de D habían divergido en direcciones opuestas desde S841 (Silo tenía todo el contenido de perfiles Completo/Lite que D nunca recibió; D tenía el fix de FASE 6 de Card #88 —verificación multi-remoto— que nunca llegó al Silo). La copia de B tenía además un bug de header real (decía "Entorno D", se autorreferenciaba a sí misma) y estaba congelada en V3.0 desde 2026-06-01, sin ninguna mejora de S841.
* Las 3 copias reconciliadas a V3.3 antes de ejecutar el propio cierre — no se podía correr "el protocolo completo" sin resolver primero cuál era la fuente de verdad.

## SESIÓN 844 (CA): FEATURE CUIT DUPLICADO + COLISIÓN DE GENOMA BIT 5 D/B
**Fecha:** 2026-07-06
**Locación:** CA
**Estado:** NOMINAL GOLD — Hash D: cf6248ba→pendiente commit cierre | Hash B: 218f2a3 (sin cambios) | PIN 1974

### Hito 1: Higiene de identidad y hallazgos de seguridad menores (CC)
* `.gy_identity` de la Silo desactualizado desde 2026-06-18 (decía "OF", máquina real CA) — corregido. SISTEMA_STATUS.json de CA sincronizado con su historial real (había cerrado S837 localmente).
* Card #89: `.gy_identity` versionado en git dentro de D hereda identidad de la última máquina que lo commitea — diseño roto, candidato a `.gitignore`.
* PIN 1974 en `MasterToolsView.vue` diagnosticado como cosmético — sin validación server-side en los 7 endpoints `/hard`. Reportado, sin fix (fuera de alcance).

### Hito 2: Feature "CUIT Duplicado / Unidades de Negocio" completo en D (CC)
* Antecedente real encontrado: plan técnico 2026-02-04 (`PLAN_TECNICO_SPLIT_V7.md`) ya especificaba el botón "Crear Nueva Unidad de Negocio", nunca completado; también Sesión 787 (erradicación `ClienteInspector`→`ClientCanvas`, no "Multiplex" como se creía inicialmente).
* Dictamen Nike: matching difuso (`SequenceMatcher`, umbral 0.85) sobre razón social y domicilio de entrega como gate, modal de 3 vías (`CuitConflictModal.vue`, nuevo), panel de hermanos (`GET /clientes/hermanos/{cuit}`).
* Guarda GOLD de CUIT único en `create_cliente` (sin antecedente documentado, a diferencia de la guarda de razón social) recibió excepción condicionada a Bit 5 (MULTI_CUIT); guarda de razón social (Blindaje Nuclear/INAPYR, 2026-04-08, PIN 1974) permanece intacta sin excepción.
* Fix adyacente: `except Exception` genérico en `create_cliente` crasheaba con `UnicodeEncodeError` (emoji + consola cp1252) antes de poder re-lanzar `HTTPException`, convirtiendo 400s legítimos en 500 opacos.
* Verificado con POST real + consulta directa a DB: Escenario A (nombre distinto, 201 + Bit 5 en DB) y Escenario B (nombre similar, 400 limpio pese al bit) confirmados en D.

### Hito 3: Colisión de genoma Bit 5 entre D y B — cherry-pick bloqueado (CC)
* Al cherry-pickear el feature a B: `AttributeError: ClientFlags has no attribute MULTI_CUIT`. Investigación reveló que B define Bit 5 (32) = `IS_GHOST` ("Operaciones Ocultas/Sin Rastro"), no `MULTI_CUIT`.
* Reconstrucción vía `git log`: origen común (`1574e950`, 12/03) con MULTI_CUIT en ambos repos; B redefinió el bit antes del 30/03; D perdió la línea de su propio archivo entre el 13/03 y el 20/05, reintroducida en Sesión 820 (31/05) — la misma sesión que investigó los "bits fantasma" de Bandera Roja #3 (Lácteos de Poblet SA, CENTRO PET ARGENTINA S.R.L.) evaluándolos solo contra la doctrina de D.
* Dato de esos clientes con Bit 5 ON confirmado únicamente en la copia LOCAL de `V5_LS_MASTER.db` dentro del checkout de B en CA (no es MT real, última modificación 2026-06-14).
* Reasignación de bit existente = Línea Roja explícita (FAQ_ARRANQUE.md) — no resuelto unilateralmente. Cherry-pick de los 5 archivos + build de `static/` revertido sin commitear; `constants.py` nunca se copió; working tree de B confirmado limpio. Card #90 creada, pendiente dictamen Nike.

---

## SESIÓN 843 (OF): OMEGA COMPLETO — DIAGNÓSTICO PUSH FALTANTE B→PROD + BITS 10/11
**Fecha:** 2026-07-03
**Locación:** OF
- Bits 10/11 (CS_PRESENTE/GA_PRESENTE) formalizados — modelo Principal/Consultivo, dictamen Nike 02/07.
- Diagnóstico y resolución de push faltante B→prod desde S842: 6 commits atrapados ~22hs (incluido fix crítico de `unicodedata`). Card #88 creada.
- Incursión directa de Carlos en MT: atraso de 13 commits por auto-bloqueo de `current/frontend/dist/`, resuelto con backup + migración 036 + rebuild.
- *(Nota S844: esta entrada se backfillea retroactivamente — no se había registrado en este archivo al momento de su cierre.)*

---

## SESIÓN 842 (CA): OMEGA LITE — FIXES TOPOLOGÍA Y UI
**Fecha:** 2026-07-02
**Locación:** CA
- S842 (CA): Cierre OMEGA Lite. Fixes UI Alta Producto y Saneamiento Topológico B.
## SESION 841 (OF): OMEGA COMPLETO/LITE + BITS CS 16-19 + BITS 26-28 D->B->P
**Fecha:** 2026-07-01
**Locacion:** OF
**Estado:** NOMINAL GOLD â€” Hash D: {HASH_CIERRE_S841} | Hash B: 9555956 (sin cambios) | PIN 1974

### Hito 1: Diagnostico forense OMEGA S840 (CC)
* A pedido de Carlos: analisis del propio transcript de S840 via JSONL. 285 tool calls totales
  en 4 ventanas de contexto (separadas por compactaciones). Distribucion: Read 66, Bash 55,
  Edit 43, PowerShell 39, Grep 24, Glob 19, TaskUpdate 16, TaskCreate 11, Write 9.
* Rabbit holes identificados: lectura de plantillas completas para continuidad narrativa (W2,
  52 calls), debugging de `.gy_identity` mal seteado (W3, 80 calls, ~47 min), burocracia de
  FASE 2 sin batching de tareas â€” 27 llamadas TaskCreate/TaskUpdate incrementales (W4).

### Hito 2: Perfiles OMEGA Completo/Lite â€” Bit 19 (CC)
* Bit 19 (`FORZAR_OMEGA_COMPLETO`) se enciende en el momento del evento (bandera roja,
  migracion, edicion de doctrina), no se infiere en FASE 3 de OMEGA.
* FASE 2 de `OMEGA.md` anotada item por item con variante Lite. Seguridad/trazabilidad
  (Canario, archivado BV, backup branch, verificacion de orbita) identica en ambos perfiles â€”
  solo se recorta prosa discursiva.
* Override a Lite con Bit19 ON requiere que Carlos lo diga explicitamente.

### Hito 3: Bits CS 16-18 + CONTEXTO_CS/DESTILADO CS (CC)
* Semaforo de salud de CS (Claude Sonnet, arquitecto de sesion) â€” mutuamente excluyentes, sin
  auto-recuperacion. CS_ROJO enciende Bit 40 (`CS_CHECKPOINT`) automaticamente.
* `CONTEXTO_CS/` adelgazado de bundle completo a puntero minimo (semaforo + puntero al Informe
  Historico del dia). `generar_contexto_cs.py` reescrito: fix de identidad dinamica via
  `.gy_identity` (mismo patron de bug que costo 47 min en S840).
* Esta sesion cerro con Bit17 (CS_AMARILLO) â€” sesion larga con multiples compactaciones de
  contexto. Ver DESTILADO CS en Informe Historico S841.

### Hito 4: Bits 26-28 â€” jerarquia de fuente de verdad D->B->P (CC)
* `D_SOBERANO` (26, siempre ON), `B_DIVERGE` (27), `P_DIVERGE` (28) â€” comparan campos globales
  `ultimo_hash_D_en_B`/`ultimo_hash_B_en_P` contra el hash real del remoto, antes de cherry-pick.
* Limitacion documentada explicitamente: no detectan divergencia estructural de paths dentro de
  un hash valido (caso real S840, `current/frontend`) â€” Card #87 creada para disenar esa deteccion.
* Hallazgo operativo menor: `ultimo_hash_D_en_B` almacena en la practica un hash de B, no de D
  â€” nomenclatura a revisar, no bloqueante.

### Hito 5: Board y verificaciones (CC)
* Card #87 creada: Deteccion automatica de divergencia estructural D<->B (DISEÃ‘O/ALTA/Sistema,
  requiere dictamen Nike).
* Verificado: `generar_contexto_cs.py` no existe en B â€” nada para cherry-pickear esta sesion.
* Nike-Sync S841 ratificado sin objeciones.

---

## SESION 840 (OF): CARD #50 + BUG #46#2 + GENOMA ALFA BITS 3-9
**Fecha:** 2026-06-30
**Locacion:** OF
**Estado:** NOMINAL GOLD â€” Hash D: ad283268 | Hash B: 9555956 | PIN 1974

### Hito 1: Card #50 â€” flags_estado fuera de PedidoUpdate (CC)
* schemas.py: eliminada linea `flags_estado: Optional[int] = None` de PedidoUpdate.
* Cerraba bypass de superficie: PATCH /pedidos/{id} permitia setattr generico sobre bits prohibidos (Bit13 LAVIMAR, Bit40 DISCRIMINA_IVA) sin pasar por STATE_MASK ni endpoints dedicados.
* Verificacion previa: cero usos legitimos en frontend/store/scripts.

### Hito 2: Card #46 Bug #2 â€” UX recuperacion OCR fallido (CC)
* IngestaFacturaView.vue, 3 puntos: input ambar+warning si numero=null, guard pre-confirmIngesta, handler HTTP 400 NUMERO_COMPROBANTE.
* Solo frontend D. NO desplegado a B esta sesion â€” ver Hito 4.

### Hito 3: ALFA V3.6 + SPEC V1.5 + actualizar_card000.py (CC)
* Genoma de arranque Bits 3-9: ESPERA_EXPLICITA, BLOQUEO_ENTORNO, LECTURA_OBLIGATORIA, DEUDA_ACUMULADA (3-6, Dictamen Nike S840); BOARD_PENDIENTE, CC_PRESENTE, GY_PRESENTE (7-9).
* SPEC: seccion 14 Edge Cases A (stale lock auto-sanacion) y B (colision identidad Bit8/9 vs agente_activo.id_agente â€” escalar a Carlos).
* actualizar_card000.py: contar_pendientes + actualizar_bit7, automatizan Bit7 en cada OMEGA.

### Hito 4: Divergencia B frontend + correccion .gy_identity (CC)
* Cherry-pick de Bug #2 aterrizo en frontend/ raiz de B (copia no servida) â€” current/frontend/ ya divergia de D antes de esta sesion. Decision de Carlos: detener despliegue visual, solo backend+script a prod. Pendiente reconciliacion futura.
* Hallazgo: .gy_identity en D decia "CA" en vez de "OF" â€” actualizar_card000.py escribia Bit7 sobre entrada equivocada en SISTEMA_STATUS.json. Corregido (autorizado por Carlos), re-corrido el script, OF.system_flags reparado.

---

## SESION 839 (OF): CARD #81 BITS 20/21 + FIXES #83/#59
**Fecha:** 2026-06-29
**Locacion:** OF
**Estado:** NOMINAL GOLD â€” Hash D: ea117af8 | Hash B: 92c2cc8 | PIN 1974

### Hito 1: _recalcular_bits_entrega centralizado (CC)
* Helper estatico en RemitosService. Predicate corregido (has_any>0 como guard).
* EC-A: delete_remito + update_remito/ANULADO recalculan bits tras la operacion.
* EC-B: create_from_ingestion evalua Bit21 directo (R16 drop-shipping).
* create_manual paso 7: 32 lineas inline â†’ 1 llamada al helper.

### Hito 2: Fix hora 12:00 (Card #83) (CC)
* PedidoCanvas.vue: payload fecha incluye hora local real (T${HH}:${MM}:00).
* PedidoList.vue: formatDate hour12:false â†’ midnight muestra 00:00.

### Hito 3: DEBUG_PDF=False guard (Card #59) (CC)
* pdf_parser.py: constante modulo DEBUG_PDF=False.
* Datos AFIP no se vuelcan a disco en produccion.

### Hito 4: Board regularizado (CC)
* Cards #36/#59/#81/#83 cerradas. Cards #85/#86 creadas.
* Card#000 actualizada: D=ea117af8 P=92c2cc8.
* OMEGA.md: bloque verificacion Card#000 agregado en FASE 2.

---

## SESION 836 (OF): DOCTRINA NIKE S836 â€” BITS FISCALES + ES_NO_COMERCIAL + GENOMA REMITOS
**Fecha:** 2026-06-26
**LocaciÃ³n:** OF
**Objetivo:** Canonizar doctrina fiscal (Bits 22/23), Banda de Excepciones (Bits 11/12), genoma remitos (migrate_036), ALFA V3.3 fast-path. Explorar Ghost + ES_LIBRE â†’ descartado.
**Estado:** NOMINAL GOLD â€” Hash D: bbe0dcec | Hash B: 6edba99 | PIN 1974

### Hito 1: ALFA V3.3 â€” FASE 0 ARRANQUE RÃPIDO (CC)
* FASE 0 compara hash_D de SISTEMA_STATUS.json con git log -1 local.
* Si coinciden + omega_cerrado:true â†’ skip FASE 1 y 2, ir a FASE 3.
* Sin hardcodeo de branch. Reutiliza escritura OMEGA. Canonizado en Q:.

### Hito 2: migrate_036 + RemitoFlags genoma (CC)
* ALTER TABLE remitos ADD COLUMN flags_estado INTEGER DEFAULT 0.
* backend/remitos/constants.py: clase RemitoFlags con Bits 0,1,4,10,11,13.
* ORM models.py: flags_estado Column(Integer, default=0) en Remito.
* backend/remitos/service.py: VINCULAR_PARCIAL (Bit11) usando RemitoFlags.VINCULAR_PARCIAL.

### Hito 3: Bits 22/23 en pedidos + cherry-pick (CC)
* HAS_PARTIAL_INVOICE (Bit 22) + FULL_INVOICED (Bit 23) en PedidoFlags.
* Eje fiscal independiente del eje fÃ­sico (Bits 20/21). Sin migraciÃ³n DB.
* Commit D:4f88bf67, cherry-pick â†’ B:b32f47d.

### Hito 4: Doctrina Ghost explorada y descartada (CC)
* ExploraciÃ³n: PEDIDO_GHOST Bit43, ES_LIBRE Bit4, migrate_037 pedido_id nullable.
* DecisiÃ³n Nike: Pedidos soberano â€” no hay remito sin pedido. Ghost innecesario.
* migrate_037 eliminado. PEDIDO_GHOST/ES_LIBRE = dead code (purga S837).

### Hito 5: ES_NO_COMERCIAL Bit 11 + commit final (CC)
* ES_NO_COMERCIAL = 1<<11 â€” Bypass comercial: muestras, uso interno.
* Banda de Excepciones junto a NO_FISCAL_FORCE (Bit 12). Reversible c/nota forense.
* Commit D:bbe0dcec, cherry-pick â†’ B:6edba99.

---

## SESION 833 (OF): GENOMA PEDIDOS BIT 20 + OMEGA V3.1
**Fecha:** 2026-06-23
**Locacion:** OF
**Objetivo:** Canonizar HAS_PARTIAL_DELIVERY (Bit 20) en genoma Pedidos. Actualizar ALFA/OMEGA V3.1. Urgencia remitos manuales circuito Rosa.
**Estado:** NOMINAL GOLD â€” Hash D: 241cddff | Hash P: c613d2c | PIN 1974

### Hito 1: Urgencia Remitos Manuales (Gy)
* schemas.py: pedido_id agregado a ManualRemitoPayload.
* service.py: create_manual() usa pedido existente si payload.pedido_id.
* ManualRemitoView.vue V15.1.4: selector pedido, Modal PedidoCanvas (Doctrina Teleport), Badges PARCIAL.
* Commits: D:96e901c6, P:2e56869c.

### Hito 2: Genoma Pedidos â€” Bits 1 y 20 (CC)
* pedidos/constants.py: HAS_ACTIVITY (Bit 1, Ley Universal) + HAS_PARTIAL_DELIVERY (Bit 20).
* remitos/service.py: create_manual() evalua Bit 20 via @property runtime.
* Commit: D:241cddff, P:c613d2c.

### Hito 3: Protocolos ALFA V3.1 + OMEGA V3.1 (CC)
* ALFA.md: archivo BV pre-header, AGENTE obligatorio (CC/Gy/CP/CS/GA), checkpoint cada 5 filas.
* OMEGA.md: BV archivada como condicion obligatoria, commit OMEGA incluye BV, aclaracion INFORMES_HISTORICOS = BV sesion.
* Cards #79 (OMEGA perfiles D/P/MT) y #80 (auditoria genomas) creadas.

---

## SESIÃ“N 832 (OF): CARDS #75/#76 FRONTEND + PROMPTS V4.1/V3.1
**Fecha:** 2026-06-22
**LocaciÃ³n:** OF
**Objetivo:** SmartSelect nodo_transporte_id (Card #76) y SmartSelect contacto_responsable_id + endpoint GET /clientes/{id}/vinculos (Card #75) en LogisticaPanel.vue. Actualizar prompts de instalacion Claude V4.1 y Gemini V3.1.
**Estado:** NOMINAL GOLD â€” Hash D: 53429c3f | Hash P: ba9361e | PIN 1974

### Hito 1: Card #76 â€” SmartSelect nodo_transporte_id (OF desde cero)
* LogisticaPanel.vue: computed nodoOptions, handler updateNodo, template con v-if="selectedTransport && (selectedTransport.flags_estado & 64)".
* Condicional Bit 6 (HAS_NODOS=64) en flags_estado de la empresa de transporte seleccionada.
* Commit D: 87e7d554.

### Hito 2: Card #75 â€” Backend GET /clientes/{id}/vinculos
* Schema VinculoForSelect (contactos/schemas.py): nombre_completo es @property de Persona, no columna. Workaround: endpoint retorna list[dict] explicito, no list[ORM].
* Endpoint clientes/router.py: join Vinculo+Persona, filtro flags_mask=10 (IS_LOGISTIC Bit1 | IS_DECISION_MAKER Bit3).
* clientesService.getVinculos() agregado en frontend/src/services/clientes.js.
* Commit D: 5093157f.

### Hito 3: Card #75 â€” SmartSelect contacto_responsable_id
* LogisticaPanel.vue: vinculosContacto ref local + fetchVinculos() + watch cliente_id + computed contactoOptions + handler updateContacto.
* onMounted Promise.all ampliado con fetchVinculos(props.modelValue.cliente_id).
* FK verificada: contacto_responsable_id -> vinculos.id (no personas.id).
* Commit D: 53429c3f.

### Hito 4: Prompts V4.1 y V3.1
* PROMPT_INSTALACION_CLAUDE V4.0->V4.1 + GEMINI V3.0->V3.1.
* Nueva seccion ROL DE LOS EJECUTORES (CS+Carlos diagnostican, CC ejecuta y propone).
* Seccion PIN 1974 reemplazada: criterio en lugar de lista estatica. Tabla incluye cherry-pick/merge a P/MT.

### Hito 5: Cherry-pick D->P + push prod
* 3 commits cherry-picked en orden: 87e7d554, 5093157f, 53429c3f.
* Pattern: cherry-pick falla por divergencia _GY/_MD en .gitignore, workaround copy manual D->P + commit P.
* Push a remote "prod" (no "origin") exitoso. P hash final: ba9361e.

---

## SESIÃ“N 826 (OF): CARD #70 GOLD + PEDIDOCANVAS SYNC + WATCHER PORT
**Fecha:** 2026-06-16
**LocaciÃ³n:** OF
**Objetivo:** ALFA V2.0 merge OF+CA. Card #70 GOLD (Canario 2.0, BITACORA_VIVA, SISTEMA_STATUS.json, actualizar_card000.py). Sync PedidoCanvas.vue Dâ†’P (Lista 2 + pink + watcher). Push P a produccion.
**Estado:** NOMINAL GOLD â€” Hash D: 85a0b630 (+ OMEGA) | Hash P: de802c6 âœ“

### Hito 1: ALFA V2.0 merge OF+CA
* D tenÃ­a cambios locales OF (manuales) â€” CA habÃ­a pusheado. Resuelto con stash â†’ pull â†’ pop. Auto-merge limpio. Commit fa29be66.
* DOCTRINA.md detectado como rename de DOCTRINA_PROCESOS.md por git. Staged correctamente.

### Hito 2: Card #70 GOLD â€” Infraestructura SISTEMA_STATUS
* SISTEMA_STATUS.json creado en Q: con versiÃ³n 1.2 (4 mÃ¡quinas: CA/OF/MT/NOTEBOOK).
* BITACORA_VIVA.md creado en Q: con header sesiÃ³n 826 y protocolo de cierre.
* ALFA.md: FASE 3 reemplazada por Canario 2.0 que lee SISTEMA_STATUS.json (LAVIMAR deprecado).
* OMEGA.md: 4 checkboxes nuevos (BITACORA_VIVA, SISTEMA_STATUS, BANDERAS_ROJAS + actualizar_card000.py).
* actualizar_card000.py: semaforo() retorna tuple (emoji para Excel, ASCII para consola â€” CP1252-safe). Commit 0b743562.

### Hito 3: PedidoCanvas.vue â€” Port watcher + Sync Dâ†’P
* AuditorÃ­a forense P vs D: 2 commits Ãºnicos en P (DOM separation â€” ya en D; watcher â€” no en D).
* Watcher route.params.id portado de P a D: re-inicializa pedido al navegar entre rutas Vue Router. Commit 85a0b630.
* Cherry-pick descartado: path mismatch D/P en git root (D: frontend/..., P: current/frontend/...).
* Sync via copia directa Dâ†’P. Build P: 290 mÃ³dulos, 7.49s. xcopy dist\ a static\. Push prod (de802c6).

### Hito 4: Board â€” Cards #71 y #72
* Card #71: Script guardar.py â€” reemplazo atÃ³mico de git commit | FEATURE | MEDIA.
* Card #72: VerificaciÃ³n de hash en ALFA Fase 0 (MÃ©todo 2) | INFRA | MEDIA.

---

## SESIÃ“N 825 (CA): SYNC GIT D+P + FIX #51 STATE_MASK + BOARD #60-#70
**Fecha:** 2026-06-14
**LocaciÃ³n:** CA
**Objetivo:** Sync git completo CA (ALFA V2.0). Fix quirÃºrgico Card #51 (ES_FIRME|ES_ANULADO simultÃ¡neos en migraciÃ³n). Actualizar BOARD hasta card #70. Remover ALFA.md de tracking git.
**Estado:** NOMINAL GOLD â€” Hash D: b2557445 (pendiente commit 825) | Hash P: pendiente commit

### Hito 1: Sync git CA (ALFA V2.0)
* D pull limpio desde origin. P requiriÃ³ stash â†’ pull â†’ stash pop con conflictos por remociÃ³n remota de .pyc/.env del Ã­ndice (commit 27190c0 remote).
* Resuelto con `git rm --cached -r` sobre todos los __pycache__, .env, cantera.db, "../data/V5_LS_MASTER.db". Stash drop post-resoluciÃ³n.

### Hito 2: Fix quirÃºrgico Card #51
* `router.py:266` â€” migraciÃ³n quirÃºrgica dejaba `ES_FIRME|ES_ANULADO` simultÃ¡neos al anotar con `|=` sin limpiar `STATE_MASK`.
* Fix: `((flags or 0) & ~STATE_MASK.value) | PF.ES_ANULADO.value`. Bug latente (0 instancias activas en DB).

### Hito 3: ALFA.md y .gitignore D
* ALFA.md/ALFA_OLD.md removidos del tracking git (`git rm --cached`).
* `.gitignore` de D actualizado con exclusiones para ambos archivos.
* ALFA.md copiado a Q:\Mi unidad\V5_Silo_Claude\ALFA.md (4878 bytes).

### Hito 4: BOARD_V5.xlsx
* Card #51 â†’ CERRADO (2026-06-14). Cards #59 y #65 (duplicados) â†’ CERRADO.
* Cards nuevas #60-#70: infra protocolo PROTOCOLO/, ALFA offline fallback, SemÃ¡foro SystemFlags, Nexo Card #000, Board P-Gold Tomy, SISTEMA_STATUS_SPEC V1.1 (Radar + Canario 2.0).

---

## SESIÃ“N 824 (OF): CANON UI CIRCUITO LISTA 2 + ROTACIÃ“N BACKUP DB
**Fecha:** 2026-06-12
**LocaciÃ³n:** OF
**Objetivo:** Adaptar nomenclatura Doctrina, ajustar UI de pedido (Circuito Lista 2) al canon Rosa/Magenta, e integrar la FASE 1B.2 de rotaciÃ³n de backups (esquema cascada con guards) al protocolo OMEGA.
**Estado:** NOMINAL GOLD â€” Hash D: [Por comitear] | Hash P: [Por comitear]

### Hito 1: Nomenclatura Doctrina
* Renombrado `DOCTRINA.md` del Silo a `DOCTRINA_DATOS.md`.
* Renombrado `DOCTRINA.md` de _GENOMA_DOCS a `DOCTRINA_PROCESOS.md`.

### Hito 2: Canon UI "Circuito Lista 2"
* Ajustado `PedidoCanvas.vue` para el Bit 12 (`NO_FISCAL_FORCE`). El modo informal ("Circuito Negro") pasa a llamarse "CIRCUITO LISTA 2".
* Se revirtiÃ³ el color provisorio cyan a la paleta canÃ³nica del Dashboard: Rosa/Magenta (`pink-400`, `pink-500`), asegurando consistencia visual.

### Hito 3: FASE 1B.2 y ConsolidaciÃ³n de Backups
* Inyectada FASE 1B.2 (RotaciÃ³n de Backups DB) a `OMEGA.md` en entornos D y P.
* Consolidado `backup_db.py`: Restaurada versiÃ³n original avanzada (10006 bytes, con guards de hash null-null) en `scripts/backup_db.py`. Limpieza de duplicados `slot_1_*.db` en el ROTATIVO del Silo.

---

## SESIÃ“N 823 (OF): PARCHE DEFENSIVO REMITOS + UI Z-INDEX REFACTOR + LIMPIEZA DB
**Fecha:** 2026-06-10
**LocaciÃ³n:** OF
**Objetivo:** Solucionar bug 500 en impresiÃ³n de remitos que abortaba por renglones huÃ©rfanos sin producto (`PedidoItem` hard-deleted durante ediciÃ³n tÃ¡ctica de `savePedido` sin `ON DELETE CASCADE` a `RemitoItem`). Corregir z-index del dropdown de productos Cantera en `PedidoCanvas` que quedaba truncado por `overflow-hidden`. Purgar transaccionalmente la DB de basura histÃ³rica.
**Estado:** NOMINAL GOLD â€” Hash D: 1b3dc55b | Hash P: e7572c3

### Hito 1: Parche Defensivo PDF (router.py)
* Al imprimir un remito cuyos renglones de pedido (`PedidoItem`) ya no existen en base (por haber sido borrados en ediciÃ³n tÃ¡ctica), el PDF lanzaba error 500.
* Ahora evalÃºa defensivamente en `get_remito_pdf`: si la ForeignKey `r_item.pedido_item` es nula, o si no tiene producto, se imprime `"ÃTEM DESCONOCIDO"`.
* Deuda tÃ©cnica registrada: Falta clÃ¡usula `ON DELETE CASCADE` de `PedidoItem` a `RemitoItem` para no dejar huÃ©rfanos.

### Hito 2: Refactor UI Z-Index PedidoCanvas
* El menÃº desplegable del buscador de productos Cantera quedaba decapitado por el contenedor `<main>`.
* Se extrajo el renglÃ³n de "Alta RÃ¡pida" fuera del contenedor con `overflow-y-auto`.
* Se elevÃ³ el Z-Index del `<main>` (`relative z-50`) por sobre el `<footer>` (`relative z-40`).
* Se moviÃ³ el `<footer>` al interior del bloque contenedor con `overflow-hidden` para unificar el contexto espacial y que el desplegable baje libremente.

### Hito 3: Limpieza Transaccional (pilot_v5x.db)
* IntervenciÃ³n directa vÃ­a SQLite: Borradas **16 facturas huÃ©rfanas** y **12 remitos huÃ©rfanos** que carecÃ­an de pedido (pedidos `None` tras borrados).
* Los pedidos #47 y #48 (de prueba con inconsistencias) fueron eliminados fÃ­sicamente de la base junto a sus items y vÃ­nculos.

### Hito 4: Sello OMEGA y SincronizaciÃ³n P
* Ejecutado Cherry-Pick de los fixes a la rama de ProducciÃ³n (repositorio `v5-ls-Tom`).
* ResoluciÃ³n de conflicto menor en `PedidoCanvas.vue` por divergencia UI de la sesiÃ³n anterior.
* Push exitoso a `v5-ls-Tom`. OMEGA V3.0 ejecutado al 100%.

---

## SESIÃ“N 820 (CA): AUDITORÃA INGESTA + BANDERAS ROJAS + BITS FANTASMA
**Fecha:** 2026-05-30
**LocaciÃ³n:** CA
**Objetivo:** Auditar el sistema de ingesta y facturaciÃ³n contra el diseÃ±o arquitectÃ³nico. Investigar clientes con flags_estado=65581. Restaurar pilot_v5x.db desde Silo. Actualizar BOARD_V5.xlsx con cards cerrados, nuevos y banderas rojas.
**Estado:** NOMINAL GOLD â€” Hash D: e41038a0 | Sin commits nuevos (sesiÃ³n de auditorÃ­a y burocracia)

### AUDITORÃA SISTEMA INGESTA (Solo lectura)
* AnÃ¡lisis del documento de diseÃ±o vs cÃ³digo real en C:\dev\Sonido_Liquido_V5
* Resultado: 60% implementado (flujo OCR, anti-duplicaciÃ³n, remito 0016 OK)
* GAP crÃ­tico 1: AfipComparisonOverlay.vue no tiene acciones â€” es visual-only. Falta POST /remitos/resolver-discrepancia y botones ARCA GANA / PEDIDO GANA (Card #43)
* GAP crÃ­tico 2: Split-Brain TIENE_NC/TIENE_ND â€” Bits 2/3 en ingesta vs Bits 17/18 en facturacion (Bandera Roja #1)
* GAP identificado: Bit PENDIENTE_AJUSTE_DOCUMENTAL no existe en pedidos/constants.py â€” dictaminado como Bit 46 por Nike (Card #42)

### RESTAURACIÃ“N DB (PIN 1974)
* Copy Q:\Mi unidad\V5_Silo_Claude\pilot_v5x.db â†’ C:\dev\Sonido_Liquido_V5\pilot_v5x.db
* Canario post-restauraciÃ³n: NOMINAL GOLD (flags=13, 0.014s certificado)
* WAL checkpoint: OK

### INVESTIGACIÃ“N FORENSE flags_estado=65581
* 2 clientes afectados: LÃ¡cteos de Poblet SA y CENTRO PET ARGENTINA S.R.L.
* Bit 16 (65536) activo pero NO documentado en ClientFlags â†’ sospecha de fantasma
* Bits documentados: EXISTENCE(0) + GOLD_ARCA(2) + V14_STRUCT(3) + MULTI_CUIT(5)
* CUITs Ãºnicos. CENTRO PET tiene domicilio Vieytes duplicado
* Bandera Roja #3 levantada: pendiente script rescate lunes OF sobre V5_LS_MASTER.db (Card #44)

### BOARD_V5.xlsx
* 7 cards CERRADOS con fecha_cierre: #6,7,8 (2026-05-31) | #9,10 (2026-05-28) | #27,28 (2026-05-29)
* 6 cards NUEVOS #40-#45 en BACKLOG/CERRADO segÃºn estado
* Hoja BANDERAS_ROJAS nueva: 3 banderas (Split-Brain bits, duplicados pilot, Bits fantasma V5_LS)
* CSV_DUMP regenerado

---

## SESIÃ“N 819 (OF): IDENTIDAD VISUAL P + BOARD V5
**Fecha:** 2026-05-29
**LocaciÃ³n:** OF
**Objetivo:** Finalizar identidad visual del entorno P (tÃ­tulo de pestaÃ±a, favicon), actualizar BOARD_V5.xlsx con 3 nuevas cards sobre genoma de pedidos, ejecutar OMEGA cierre de sesiÃ³n completo.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash D: 5c15bae2 | Hash P: 92497c6

### ACTUALIZACIÃ“N ENTORNO P (FRONTEND)
* static/index.html (lÃ­nea 8): TÃ­tulo "Sonido LÃ­quido V5 [DESARROLLO] - D" â†’ "Sonido LÃ­quido V5 - Mando"
* static/favicon.svg: Reemplazado con fondo pÃºrpura (#6B21A8) + "SL" blanco (4 cuadrantes neÃ³n descontinuado)
* public/favicon.svg: Sincronizado con static/
* Commit P: 92497c6 "Fix: identidad entorno P - tÃ­tulo y favicon (PIN 1974)"

### ACTUALIZACIÃ“N BOARD_V5.xlsx
* Agregadas 3 cards (total 31):
  - ID 29: ES_ENTREGADO â€” nuevo estado genoma pedidos (DISEÃ‘O, ALTA, V6.0, BACKLOG)
  - ID 30: Bit COBRADO â€” disparador contable (DISEÃ‘O, ALTA, V6.0, BACKLOG, depende #29)
  - ID 31: Excel snapshot de pedidos â€” implementaciÃ³n (FEATURE, MEDIA, V5.9, BACKLOG)

### PROTOCOLO OMEGA COMPLETO (D)
* FASE 1: Canario âœ“ (LAVIMAR flags_estado=13 NOMINAL GOLD)
* FASE 1B: WAL checkpoint âœ“ (pilot_v5x.db sincronizado)
* FASE 2: ESTADO_ECOSISTEMA actualizado; CAJA_NEGRA sesiÃ³n 819 registrada; BITACORA_DEV actualizada
* FASE 3: Rama stable, trabajar tree clean
* Estado Final: NOMINAL GOLD

---

## SESIÃ“N 818 (sub-CA): HARDENING INGESTA â€” 3 FIXES QUIRÃšRGICOS
**Fecha:** 2026-05-28
**LocaciÃ³n:** CA
**Objetivo:** Aplicar 3 fixes validados por auditorÃ­a cruzada (CC Opus 4.8 + Gy High) sobre el mÃ³dulo de ingesta: URLs con prefijo /api inexistente (404 en iframes de duplicado), AttributeError por PedidoFlags.STATE_MASK, y TypeError por flags_estado None en anular-y-reingestar.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash final: 2938c77a

### FIX 1 â€” URLs /api inexistente
* IngestaFacturaView.vue (393, 407, 451): /api/ingesta y /api/remitos â†’ /ingesta y /remitos. Validado: vite.config.js no proxea /api; main.py monta routers sin prefijo.

### FIX 2 â€” PedidoFlags.STATE_MASK AttributeError
* router.py (226, 231): STATE_MASK es constante de mÃ³dulo, no miembro de clase. Import ampliado + referencia directa `~STATE_MASK`. Hubiera dado 500 al anular pedido ORIGEN_FACTURA.

### FIX 3 â€” guard flags None
* router.py:243: `(raw_nuevo.flags_estado or 0) & ~2048`. Paridad con el guard ya presente en la lÃ­nea 218.

### Anexo â€” OMEGA.md FASE 1
* Snippet inline de canario migrado a mÃ¡scara de bits (flags & 13)==13, alineado con canario_v2.py.

---

## SESIÃ“N 818: DETECCIÃ“N TEMPRANA DE DUPLICADOS + FIXES UI (OF OMEGA)
**Fecha:** 2026-05-28
**LocaciÃ³n:** OF
**Objetivo:** Implementar la detecciÃ³n temprana de facturas duplicadas en la ingesta de PDFs raw, permitiendo la anulaciÃ³n y reingesta con PIN 1974 de comprobantes en estado BORRADOR y la redirecciÃ³n/visualizaciÃ³n para remitos ya despachados. Resolver cascada de borrado en Remito para evitar huÃ©rfanos en `FacturaRemito` y salvaguardar la trazabilidad marcando el procesado viejo como "ANULADA" en vez de borrar el registro. Resolver bug de includes() sobre CUIT nulo en filtrado de clientes (HaweView.vue) y bucle de redirecciÃ³n en creaciÃ³n de nuevo pedido tÃ¡ctico limpiando `ingestaData` al desmontar (PedidoCanvas.vue).
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash final: f7a48c08

### Hito 1: DetecciÃ³n Temprana de Duplicados & Ciclo de AnulaciÃ³n y Reingesta
* **DetecciÃ³n temprana:** Al subir un PDF a `POST /ingesta/raw`, se realiza una bÃºsqueda en `facturas` por clave Ãºnica (`tipo_comprobante`, `punto_venta`, `numero_comprobante`). Si existe match, se devuelve metadatos de duplicado al frontend.
* **UI de ComparaciÃ³n:** El frontend detecta la respuesta de duplicado y muestra un panel especial de comparaciÃ³n bloqueando el flujo estÃ¡ndar.
* **BifurcaciÃ³n de Acciones:**
  * Si el remito asociado estÃ¡ en **BORRADOR**, se permite la acciÃ³n "Anular procesado y re-ingestar con este PDF" previa verificaciÃ³n del PIN Maestro "1974".
  * Si el remito ya no es BORRADOR, se muestra un botÃ³n para visualizar el remito actual y se bloquea la re-ingesta.
* **Endpoint de AnulaciÃ³n y Reingesta (`POST /ingesta/raw/{raw_id}/anular-y-reingestar`):**
  * Valida el PIN de autorizaciÃ³n ("1974").
  * Si el remito estÃ¡ en BORRADOR, marca el RAW viejo con el Bit 11 (`DUPLICATE` = 2048).
  * Marca el procesado viejo (`procesada_vieja.estado = "ANULADA"`) preservando trazabilidad de auditorÃ­a.
  * Si el pedido asociado provino de la factura, se anula (`estado = "ANULADO"`, flag `ES_ANULADO`).
  * Elimina el remito viejo en BORRADOR (con cascada de borrado para evitar huÃ©rfanos).
  * Elimina la factura vieja espejo.
  * Habilita el nuevo RAW (`audit_status = "RECIBIDO"`, limpia Bit 11) para procesamiento normal.

### Hito 2: Cascada de Borrado en Remito & Integridad
* Se confirmÃ³ que el modelo `Remito` posee `cascade="all, delete-orphan"` configurado en su relaciÃ³n `items` (hacia `RemitoItem`).
* Se agregÃ³ `cascade="all, delete-orphan"` en la relaciÃ³n `vinculos_facturas` (hacia `FacturaRemito`) en `backend/remitos/models.py` para erradicar registros huÃ©rfanos en la tabla intermedia al eliminar un remito.

### Hito 3: Fix A â€” HaweView null.includes()
* **Causa raÃ­z:** `HaweView.vue:771` filtraba clientes evaluando `cliente.cuit.includes(query)`. Dado que CUIT puede ser null en la base de datos para clientes informales, esto provocaba un error de tipo `Cannot read properties of null (reading 'includes')`.
* **ResoluciÃ³n:** Se agregÃ³ un guard para fallback de string vacÃ­o: `(cliente.cuit || '').includes(query)`.

### Hito 4: Fix B â€” RedirecciÃ³n Nuevo Pedido TÃ¡ctico
* **Causa raÃ­z:** Al navegar al canvas de creaciÃ³n manual de nuevo pedido tÃ¡ctico, el store Pinia quedaba con datos de ingesta previos (`ingestaData`) si el operador cancelaba una ingesta previa sin limpiarla. Esto gatillaba una redirecciÃ³n no deseada al mÃ³dulo de Ingesta en lugar de mantener al usuario en el canvas.
* **ResoluciÃ³n:** Se agregÃ³ la llamada a `pedidosStore.clearIngestaData()` en el hook `onUnmounted` de `PedidoCanvas.vue`, garantizando que la navegaciÃ³n limpie el estado al abandonar el canvas.

---

## SESIÃ“N 817: SYNC Dâ†’Pâ†’MT + MIGRACIONES + FIXES UI (OF OMEGA)
**Fecha:** 2026-05-27
**LocaciÃ³n:** OF
**Objetivo:** Sincronizar el entorno de desarrollo (D) con producciÃ³n (P) y Mesa TÃ¡ctica (MT). ReconstrucciÃ³n y build completo en P/MT. Ejecutar scripts de migraciÃ³n de base de datos en MT (Bit 40, Bit 20/19, fecha_vencimiento y Genoma V6). Corregir bug en `PedidoCanvas.vue` de estado de pedido hardcodeado ("PENDIENTE"). Implementar validaciÃ³n y salvaguarda Poka-Yoke para pedidos en estado `CUMPLIDO` o `ANULADO`. Corregir bug visual de altura en `PedidoCanvas.vue` (h-screen -> h-full) para evitar corte por la barra de tareas de Windows.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash final: ec5cb6de

### Hito 1: SincronizaciÃ³n y Despliegue de Infraestructura
* SincronizaciÃ³n de backend (183 archivos) y frontend/src (116 archivos) desde D a P/current.
* ReconstrucciÃ³n del entorno virtual (venv), instalaciÃ³n de dependencias requeridas (incluyendo PyMuPDF) y compilaciÃ³n del frontend en producciÃ³n con Ã©xito.

### Hito 2: EjecuciÃ³n de Migraciones de Base de Datos en MT
* Script de re-auditorÃ­a de Bit 40 (DISCRIMINA_IVA) para 28 clientes Responsable Inscripto (excluyendo LAVIMAR).
* Script de reparaciÃ³n masiva de consistencia de bits (Bits 20 y 19) en 9 clientes anÃ³malos.
* MigraciÃ³n fÃ­sica de base de datos (`ALTER TABLE pedidos ADD COLUMN fecha_vencimiento DATE`) y migraciÃ³n de estado de pedidos al Genoma V6 en banda 32+ (excluyentes: `ES_PRESUPUESTO`, `ES_FIRME`, `ES_CUMPLIDO`, `ES_ANULADO`).

### Hito 3: Fix PedidoCanvas Estado Hardcodeado & Poka-Yoke
* **Causa raÃ­z:** `savePedido()` enviaba siempre `estado: "PENDIENTE"`, pisando el estado real del pedido al guardar en ediciÃ³n.
* **ResoluciÃ³n:**
  * Se agregÃ³ la variable reactiva `estadoPedido = ref('PENDIENTE')`.
  * `loadPedido()` ahora captura el estado del pedido: `estadoPedido.value = p.estado || 'PENDIENTE'`.
  * `savePedido()` utiliza `estado: estadoPedido.value` en su payload.
  * Se implementÃ³ un badge visible en el encabezado de solo lectura que indica el estado del pedido.
  * Se agregaron salvaguardas Poka-Yoke: si el pedido es `CUMPLIDO` o `ANULADO`, se muestra un banner de advertencia ("Este pedido estÃ¡ [ESTADO] y no puede editarse"), se deshabilitan los botones de Guardar y Guardar/Imprimir en la UI, se bloquea el guardado mediante atajo de teclado F10 y se interrumpe preventivamente al inicio de `savePedido()`.

### Hito 4: Fix de Altura (Bug Barra de Windows)
* **Causa raÃ­z:** La raÃ­z de `PedidoCanvas.vue` definÃ­a `min-h-screen` y la tarjeta interna `h-screen` (que se traducen a `100vh`). Sin embargo, en el layout `HaweLayout.vue`, el componente se dibuja dentro de un contenedor flexible con padding `p-4` y `overflow-hidden`. Esto hacÃ­a que la tarjeta desbordara el contenedor por exactamente el padding, cortando el pie del canvas (TOTAL FINAL y botones de guardar) bajo la barra de tareas de Windows.
* **ResoluciÃ³n:** Se reemplazÃ³ `min-h-screen` por `min-h-full` en el div raÃ­z y `h-screen` por `h-full` en la tarjeta interna de `PedidoCanvas.vue`. Con esto, el canvas se adapta perfectamente a la altura fluida calculada por su contenedor padre.

### Hito 5: Burocracia y Sello OMEGA
* EjecuciÃ³n de checkpoint WAL sobre `pilot_v5x.db` (`PRAGMA wal_checkpoint(FULL)`).
* Copiado y respaldo de base de datos a `Q:\Mi unidad\V5_Silo_Claude\`.
* ActualizaciÃ³n de `ESTADO_ECOSISTEMA.md`, `INBOX.md` y generaciÃ³n del reporte histÃ³rico de sesiÃ³n 817.

---

## SESIÃ“N 816: FIX INGESTA/PEDIDO + SALVAGUARDAS REMITOS (OF OMEGA)
**Fecha:** 2026-05-26
**LocaciÃ³n:** OF
**Objetivo:** CorrecciÃ³n de bugs encadenados en el mÃ³dulo de ingesta y vinculaciÃ³n de pedidos, reparaciÃ³n de AttributeError en endpoint approve, y remociÃ³n de endpoint obsoleto. CorrecciÃ³n de ImportError en router de pedidos (_aplica_iva). IncorporaciÃ³n de salvaguardas defensivas para remitos en get_remito_pdf importadas desde P. AnÃ¡lisis comparativo de archivos .py entre P y D.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash final: 39309805

### Hito 1: Bug Ingesta/Pedido (Bugs 1, 2 y 3)
* **Bug 1 (AttributeError):** Corregido en `backend/ingesta/router.py`. La llamada a `IngestaService.approve` retorna un diccionario en lugar de un objeto. Se corrigieron los accesos a `procesada["id"]` y `procesada["estado"]`.
* **Bug 2 (ValidaciÃ³n Pedido):** Implementada validaciÃ³n estricta de `pedido_id` en `backend/ingesta/service.py` para evitar vinculaciones nulas desde el backend.
* **Bug 3 (Selector de Pedido):** Se modificÃ³ el modal de aprobaciÃ³n en `frontend/src/views/Pedidos/IngestaFacturaView.vue` para forzar la selecciÃ³n de un pedido vinculante y enviar el payload con `pedido_id_vinculado`. El botÃ³n de la ficha de remito pasÃ³ de "Generar Remito" a "Proceder".
* **Endpoint deprecado:** Se eliminÃ³ la ruta `/remitos/ingesta-process` de backend/remitos y del frontend, unificando todo bajo el router de ingesta.

### Hito 2: ImportError en Pedidos Router
* Se eliminaron las declaraciones de importaciÃ³n interna redundantes de `PF` y `ClientFlags` dentro del helper `_aplica_iva` en `backend/pedidos/router.py`. Ahora se usan los del scope global para evitar fallos por alias inexistentes en constants.py.

### Hito 3: SincronizaciÃ³n de Salvaguardas de Remitos
* Se importaron las validaciones defensivas de P a D en `backend/remitos/router.py` (`get_remito_pdf`) para verificar la existencia de `remito.pedido` y de `remito.pedido.cliente` antes de generar el archivo PDF, previniendo caÃ­das con excepciones HTTP 400.

### Hito 4: AnÃ¡lisis Comparativo P vs D
* Se ejecutÃ³ un anÃ¡lisis de archivos `.py` entre D (`Sonido_Liquido_V5`) y P (`v5-ls-Tom`).
* Se identificÃ³ que la raÃ­z literal de P sÃ³lo contiene 9 archivos. La versiÃ³n activa y desplegada se encuentra en `C:\dev\v5-ls-Tom\current\backend`.
* Existe paridad casi exacta entre D y P (Current), exceptuando el archivo `backend/core/utils/text.py` que sÃ³lo se encuentra en D (contiene `normalize_name`).

### Hito 5: Burocracia y Respaldo
* Se ejecutÃ³ el WAL checkpoint completo sobre `pilot_v5x.db`.
* Se copiÃ³ la base de datos `pilot_v5x.db` al silo oficial `Q:\Mi unidad\V5_Silo_Claude\`.
* Se actualizaron `ESTADO_ECOSISTEMA.md`, `INBOX.md`, `CAJA_NEGRA.md`, y se generÃ³ el informe histÃ³rico `2026-05-26_FIX_INGESTA_PEDIDO_816.md`.

---

## SESIÃ“N 815: AUDITORÃA GENÃ“MICA + APPLY_IVA BIT 40 (CA OMEGA)
**Fecha:** 2026-05-22
**LocaciÃ³n:** CA
**Objetivo:** AuditorÃ­a forense completa del genoma flags. DiagnÃ³stico causal Bit 40 (DISCRIMINA_IVA) â€” 28/29 RI clientes desincronizados. ReparaciÃ³n masiva de anomalÃ­as (37 total). ImplementaciÃ³n helper `_aplica_iva()` centralizando fiscal logic. PROTOCOLO OMEGA V2.2 Fase 2 (Burocracia).
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash final: 1faac75e

### Hito 1: AuditorÃ­a Forense â€” DiagnÃ³stico Causal Bit 40
* **Problema:** 28/29 Responsable Inscripto clientes con `Bit 40 (DISCRIMINA_IVA) = 0` cuando deberÃ­an ser 1.
* **Causa:** Clientes creados/actualizados PRE-SesiÃ³n 812 (cuando REGLA 3 implementada) nunca pasaron por `_audit_sovereignty()` post-implementaciÃ³n.
* **Evidencia:** JOFRE SERGIO OMAR (updated 2026-05-21, POST-812) tenÃ­a Bit 40=1; ALFAJORES JORGITO (updated 2026-04-08, PRE-812) tenÃ­a Bit 40=0.
* **ConclusiÃ³n:** `_audit_sovereignty` solo se llama en create/update cliente, no retroactivamente. PatrÃ³n sistÃ©mico detectado: cada nueva regla deja histÃ³ricos desactualizados.

### Hito 2: AnomalÃ­as Identificadas (37 total)
* **Bit 40 (DISCRIMINA_IVA):** 28/29 RI clientes con bit=0 en lugar de 1.
* **Bit 20 (PENDIENTE_REVISION):** 6 clientes con bit=1 pero 4+ pilares completos (fantasma).
* **Bit 19 (MEDALLA_ROSA):** 3 clientes Rosa (Bit 4) sin Bit 19 â€” inconsistencia color.
* **CF CUIT fallback, IS_VIRGIN, Bit 2 (GOLD_ARCA):** Verificados consistentes â€” 0 anomalÃ­as.

### Hito 3: Script Re-auditorÃ­a Bit 40 â€” PIN 1974
* `backend/scripts/re_audit_bit40.py`: ejecutado contra `pilot_v5x.db`.
* LÃ³gica: Para cada cliente RI (`condicion_iva.nombre LIKE "%RESPONSABLE INSCRIPTO%"`), toggle Bit 40 ON.
* Resultado: 28 clientes reparados. VerificaciÃ³n post: `SELECT * WHERE Bit40=0 AND Condicion_IVA~RI` â†’ 0 restantes.
* Commit: d84641b8.

### Hito 4: Script ReparaciÃ³n Masiva Bits 20 + 19 â€” PIN 1974
* **ReparaciÃ³n 1 (Bit 20):** 6 clientes con Bit 20=1 + lista_precios + segmento + 4+ domicilios. Apagado Bit 20.
* **ReparaciÃ³n 2 (Bit 19):** 3 clientes Rosa (Bit 4=1) sin Bit 19. Encendido Bit 19 (MEDALLA_ROSA).
* VerificaciÃ³n post: 0 anomalÃ­as restantes en ambos casos (100% cobertura).
* Commit: 1faac75e.

### Hito 5: CentralizaciÃ³n apply_iva() en router.py
* **Problema:** Fiscal logic duplicada en 5 locaciones (create + update + add_item + update_item + delete_item) con inconsistencia: algunas verificaban estado, otras no.
* **SoluciÃ³n:** Helper `_aplica_iva(pedido, cliente) -> bool` implementando Doctrina V6:
  - Circuito Negro (Bit 12 NO_FISCAL_FORCE=1) â†’ siempre False (nunca IVA).
  - Sin cliente â†’ False.
  - Circuito Blanco â†’ solo RI (Bit 40) aplica IVA.
* **IntegraciÃ³n:** Reemplazadas 5 instancias de `tipo_facturacion in ["A", "B", "FISCAL"]` con llamadas a `_aplica_iva()`.
* **Bonus:** PedidoFlags â†’ PF alias corregido en `toggle_circuito_bipolar`.

### Hito 6: PROTOCOLO OMEGA V2.2 â€” Fase 2 (Burocracia)
* **Fase 1B:** WAL checkpoint (`PRAGMA wal_checkpoint(FULL)`) ejecutado en `pilot_v5x.db`.
* **Fase 2:** ActualizaciÃ³n de 3 archivos de documentaciÃ³n:
  - ESTADO_ECOSISTEMA.md: CA/D row con hash 1faac75e, estado OK, alert resolved.
  - CAJA_NEGRA.md: Nueva entrada sesiÃ³n 815, incremento "SesiÃ³n actual: 815", documentaciÃ³n auditorÃ­a.
  - BITÃCORA_DEV.md: Esta entrada (en curso).
  - INFORME_HISTÃ“RICO: CreaciÃ³n de 2026-05-22_AUDITORIA_GENOMICA_815CA.md.

### Commits
* `d84641b8` (815 CA): apply_iva helper + Bit 40 re-auditorÃ­a script + centralizaciÃ³n fiscal logic.
* `1faac75e` (815 CA OMEGA): ReparaciÃ³n masiva Bits 20+19 + ESTADO_ECOSISTEMA.md + CAJA_NEGRA.md update.

### Pendiente â†’ SesiÃ³n 816 CA
* Fase 4-7 OMEGA V2.2 (AuditorÃ­a de peso, VerificaciÃ³n Ã³rbita, Higiene Antigravity).
* Mapa de flags para UX (Utilidad Maestra).
* 6 bugs pedidos (c) CRÃTICO, d) ALTA, a-b) MEDIA, e-f) BAJA).

---

## SESIÃ“N 814: GENOMA PEDIDOS V6 + OPERACIÃ“N MUDANZA + DIFF 4 (OF)
**Fecha:** 2026-05-22
**LocaciÃ³n:** OF
**Objetivo:** CanonizaciÃ³n de PedidoFlags Genoma V6 (banda 32+). MigraciÃ³n y OperaciÃ³n Mudanza de 31 pedidos histÃ³ricos incorporando fecha_vencimiento. Transiciones de estado seguras en router.py mediante STATE_MASK. ImplementaciÃ³n de Diff 4 en PedidoCanvas.vue con BigInt bitwise para cliente y desglose fiscal Ley 27.743.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash final: 5e1e2445

### Hito 1: Genoma Pedidos V6 & Constantes
* `PedidoFlags` en `backend/pedidos/constants.py` define la banda baja (bits universales como `NO_FISCAL_FORCE` = Bit 12) y banda alta (bits >= 32) para ciclo de vida y auditorÃ­a forense.
* Estados excluyentes (`STATE_MASK`): `ES_PRESUPUESTO` (Bit 32), `ES_FIRME` (Bit 33), `ES_CUMPLIDO` (Bit 34), `ES_ANULADO` (Bit 35).
* Flags ortogonales acumulables: `RESERVA_STOCK` (Bit 36), `TUVO_CIRCUITO` (Bit 37), `ORIGEN_FACTURA` (Bit 38), `ORIGEN_RETROACTIVO` (Bit 39), `CAMBIO_A_NEGRO` (Bit 41), `CAMBIO_A_BLANCO` (Bit 42).
* Commit: `5c231ecb` (Feat PedidoFlags)

### Hito 2: OperaciÃ³n Mudanza (Base de Datos)
* MigraciÃ³n del campo string `estado` a la estructura de bits en la base de datos `pilot_v5x.db`.
* 31 pedidos migrados conservando integridad de negocio y aÃ±adiendo columna `fecha_vencimiento`.
* Commit: `14abd5a0` (Genoma V6 + Mudanza)

### Hito 3: Router Backend (SoberanÃ­a Transaccional)
* **Paso A (Escrituras):** IntegraciÃ³n de `STATE_MASK` en escrituras de `backend/pedidos/router.py` para asegurar que las transiciones de estado borren el bit previo y guarden el nuevo estado de forma excluyente.
* **Paso B (Lecturas):** Reemplazo de accesos directos de lectura de estado por operaciones bitwise.
* Commits: `f8e1df84` (Paso A) y `9fdda7ed` (Paso B)

### Hito 4: PedidoCanvas.vue (Diff 4 Frontend)
* **BigInt Safety:** Uso de `BigInt(cliente.flags_estado || 0)` y operadores de BigInt (ej. `1n << 40n`) en `isClienteRI` para prevenir truncado y pÃ©rdida de precisiÃ³n de JS en nÃºmeros > 31 bits.
* **Motor Bipolar:** `isSinIVA` alineado con Bit 12 del pedido (`NO_FISCAL_FORCE`) y el Bit 40 del cliente (`DISCRIMINA_IVA`).
* **LÃ³gica selectProduct:** En precios `LISTA_5`, solo los clientes RI (`isClienteRI`) reciben el neto recalculado (divisiÃ³n por 1.21). CF, Monotributo, Exento y Negro preservan el precio original con IVA.
* **Desglose Fiscal (Ley 27.743):**
  - Cliente Responsable Inscripto (en circuito blanco): IVA discriminado.
  - Consumidor Final / Monotributo (en circuito blanco): IVA contenido detallado en leyenda del pie.
  - Circuito Negro / Exento: IVA $0.00.
* Commit: `5e1e2445` (Diff 4 PedidoCanvas)

### Pendiente â†’ SesiÃ³n 815
* Integrar `apply_iva` en `router.py` usando el Bit 40 del cliente.
* Bug de ingesta/remitos en la ventana de pedidos.
* Bug de UI en ficha remito (barra de Windows).
* Lista flotante de operador (tooltip 7 listas).

---

## SESIÃ“N 812: DISCRIMINA_IVA BIT 40 + PURGA HEREJÃA DEL 15 (OF)
**Fecha:** 2026-05-20
**LocaciÃ³n:** OF
**Objetivo:** Implementar Bit 40 DISCRIMINA_IVA. Purgar Bit 15 de pilot_v5x.db (5 clientes). Sellar doctrina HerejÃ­a del 15 en BIBLIOTECA_NIKE.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash D: b0ac3c47

### Hito 1: Bit 40 DISCRIMINA_IVA â€” constants.py
* `ClientFlags.DISCRIMINA_IVA = 1 << 40` â€” nuevo bit en `backend/clientes/constants.py`.
* SemÃ¡ntica: 1 = Responsable Inscripto (discrimina IVA, Factura A, precio neto / 1.21). 0 = CF / Mono / Exento / Rosa.

### Hito 2: Auto-detecciÃ³n en afip_bridge.py
* `AfipBridgeService._fetch_from_rar()`: si condicion_iva contiene "RESPONSABLE INSCRIPTO" (o "(INFERIDO)"), enciende DISCRIMINA_IVA en el dict de retorno al frontend.

### Hito 3: Regla 3 en _audit_sovereignty (service.py)
* Toggle permanente en create/update: `condicion_iva.nombre` con "RESPONSABLE INSCRIPTO" â†’ `flags_estado |= DISCRIMINA_IVA`. CF / Mono / Exento / None â†’ `flags_estado &= ~DISCRIMINA_IVA`.

### Hito 4: Purga HerejÃ­a del 15
* 5 clientes en `pilot_v5x.db` con Bit 15 (32768 = FacturaFlags.PASADO_A_PEDIDO) encendido por error de IA.
* Purga SQL: `UPDATE clientes SET flags_estado = flags_estado & ~32768 WHERE flags_estado & 32768`.
* DB saneada. Canario: NOMINAL GOLD.

### Hito 5: BIBLIOTECA_NIKE.md â€” doctrina HerejÃ­a del 15
* MÃ³dulo 2 sellado con Ã­tem "La HerejÃ­a del 15": prohÃ­be `1<<15` en `clientes.flags_estado`. Bit 15 es exclusivo del genoma de facturas (PASADO_A_PEDIDO).

### Pendiente â†’ SesiÃ³n 813
* Diff 4 PedidoCanvas.vue: `selectProduct` + presentaciÃ³n precio por Bit 12 (negro) + Bit 40 (RI) + CF. `isClienteRI` computed ya diseÃ±ado (BigInt Bit 40).

---

## SESIÃ“N 811-CA: SINCRONIZACIÃ“N Y AUDITORÃA DE ANOMALÃAS (CA)
**Fecha:** 2026-05-19
**LocaciÃ³n:** CA
**Objetivo:** Sincronizar con OF (git pull) y auditar anomalÃ­as del Bit 19 vs Bit 4.
**Estado:** NOMINAL GOLD â€” Hash D: 3f608adb

### Hito 1: SincronizaciÃ³n
* Git pull integrado de 7 commits (sesiones OF 810 y 811).
* Canario certificado localmente: `flags_estado = 13`.
* WAL checkpoint (PRAGMA wal_checkpoint(FULL)) ejecutado correctamente.

### Hito 2: AuditorÃ­a de anomalÃ­as de color (Bit 19 ON / Bit 4 OFF)
* **MYM ODONTOLÃ“GICOS LA PLATA:** VÃ¡lido por diseÃ±o. Al ser Consumidor Final/GenÃ©rico (CUIT 00000000000), se fuerza a Gold (nibble 15) por lo que no infiere Rosa (no tiene Bit 4), pero recibe la medalla Rosa (Bit 19) por soberanÃ­a base de facturaciÃ³n.
* **SERGIO JOFRE:** AnÃ³malo. CUIT real pero CondiciÃ³n IVA ausente (`None`). Bit 19 forzado por aserciones/excepciones manuales heredadas en scripts de verificaciÃ³n.
* **Pao Tandil:** AnÃ³malo. CUIT null y segmento null. Al no tener segmento, no recibe Bit 4, y sus flags no han sido recalculados por la auditorÃ­a transaccional.

---

## SESIÃ“N 811: HONNEY + DEOU F4 + CF CUIT FALLBACK (OF)
**Fecha:** 2026-05-19
**LocaciÃ³n:** OF
**Objetivo:** Fix hard delete fÃ³siles flags=0. Fix alta rÃ¡pida DEOU F4. CF CUIT fallback backend.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash D: 208d6a46 | Hash P: 937d5be

### Hito 1: HONNEY â€” hard delete fÃ³siles flags=0
* Guard IS_VIRGIN: `if current_flags != 0 and not (current_flags & IS_VIRGIN)`.
* HardDeleteManager.vue: fila amber, label "âš ï¸ CLIENTE IMPOSIBLE", botÃ³n habilitado, integrity safe.
* Commit: `1e5d4327` (D) / `85a48b8` (P)

### Hito 2: DEOU F4 â€” alta rÃ¡pida cliente correcto
* Bug A: `currentFlags |= 3` cuando nibble=0 â€” EXISTENCE+IS_VIRGIN mÃ­nimo vital.
* Bug B: `cuit: ''` â†’ `cuit: null` en `altaClienteContext()` y F4 handler de PedidoCanvas.
* Bug C: `_audit_sovereignty()` + activo sync + `_ensure_domicilio_rosa()` en `create_cliente()`.
* Commit: `0286f0df` (D) / `0b31fe2` (P)

### Hito 3: CF CUIT fallback â€” backend soberano
* `_apply_cf_cuit_fallback()`: condicion_iva CONSUMIDOR FINAL + cuit null â†’ '00000000000'.
* Llamado antes de `_audit_sovereignty` en create y update.
* Commit: `208d6a46` (D) / `937d5be` (P)

---

## SESIÃ“N 810: FIX C4 ClientCanvas + IVA Rosa + NavegaciÃ³n PedidoCanvas (OF)
**Fecha:** 2026-05-18
**LocaciÃ³n:** OF
**Objetivo:** FIX C4 has4Pillars virginidad + bifurcaciÃ³n domicilio Gold/Rosa. Fix IVA Rosa PedidoCanvas. Fix syntax error Vite. Fix navegaciÃ³n Nuevo/Edit. MigraciÃ³n Bit 4 clientes Rosa en D y P.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash D: ff77a309 | Hash P: 3e060bb

### Hito 1: FIX C4 â€” ClientCanvas + Doctrina Virginidad
* `has4Pillars` bifurcado: domicilio `es_entrega` para Rosa, `es_fiscal` para Gold.
* Eliminada lÃ­nea `currentFlags &= ~2` â€” violaciÃ³n doctrina virginidad. IS_VIRGIN solo lo apaga el backend en CUMPLIDO o CAE real.
* Commit: `bf406415` (D) / `5adf6f4` (P)

### Hito 2: FIX PedidoCanvas â€” IVA Rosa + Syntax + NavegaciÃ³n
* Syntax error Vite (`Unexpected token 1306:10`): eliminado bloque `else {}` espurio en `savePedido` que intentaba colgar como tercer else de un if/else ya cerrado.
* IVA Rosa: `selectProduct` divide `/1.21` cuando `isSinIVA && origen === 'LISTA_5'`. Template `v-if="!isSinIVA"` oculta bloque IVA pie de pantalla para clientes informales.
* Reset post-save: `resetPedido(skipConfirm=true)` â€” elimina `confirm()` espurio que disparaba porque items aÃºn estaban en memoria al momento del reset.
* NavegaciÃ³n "Nuevo": 2 ocurrencias ruta muerta `/hawe/tactico` en `PedidoList.vue` â†’ `{ name: 'PedidoCanvas' }`.
* NavegaciÃ³n ediciÃ³n: 2 ocurrencias `/hawe/tactico?edit=` en `PedidoInspector.vue` â†’ `{ name: 'PedidoEditar', params: { id } }`.
* Commit: `ff77a309` (D) / `3e060bb` (P)

### Hito 3: MigraciÃ³n Bit 4 â€” Clientes Rosa D y P
* DiagnÃ³stico: `_audit_sovereignty()` lÃ­nea 346 solo infiere Bit 4 si `has_segmento AND not has_real_cuit`. Clientes creados sin `segmento_id` no reciben sello automÃ¡tico.
* UPDATE con PIN 1974 en `V5_LS_MASTER.db`: ANA ROBLES, Cecilia Pascual, LUISA PISCITELLI, Pao Tandil â†’ `flags_estado |= 16`. 4/4 confirmadas.
* Sincronizado en `pilot_v5x.db` (D): Cecilia Pascual y LUISA PISCITELLI (nuevas); Ana Robles ya tenÃ­a Bit 4 desde el inicio de sesiÃ³n.

### Commits
* `bf406415` (D) / `5adf6f4` (P): FIX C4 ClientCanvas + virginidad + domicilio bifurcado Gold/Rosa
* `ff77a309` (D) / `3e060bb` (P): FIX PedidoCanvas syntax + IVA Rosa + reset + navegaciÃ³n

---

## SESIÃ“N 809: AUDITORÃA CRUZADA + IS_VIRGIN GLOBAL + MOTOR BIPOLAR + ROSETI 1482 (CA)
**Fecha:** 2026-05-18
**LocaciÃ³n:** CA
**Objetivo:** AuditorÃ­a cruzada Opus/Antigravity pedidos y clientes. IS_VIRGIN rename global. Canonizar Motor Bipolar Bit 12. Implementar Roseti 1482 para clientes Rosa.
**Estado:** NOMINAL GOLD (OMEGA pendiente 810) â€” PIN 1974 | Hash D: 4010b655

### Hito 1: Fixes Backend Pedidos (Opus â€” C1/C3/C5)
* C1: `delete_pedido` â€” variable `pedido` no definida â†’ NameError/500. Fix: query con eager load.
* C3: `NO_FISCAL_FORCE` ignorado en cÃ¡lculo IVA â€” 5 puntos en router.py corregidos con bitwise.
* C5: `STRICT_MODE_VIOLATION` inalcanzable â€” `nivel_lista=3` era default antes del check. Fix: `nivel_lista=None`.

### Hito 2: Fixes Frontend PedidoCanvas (C1-C5)
* C1: `totalFinal` â€” `isSinIVA` basado en Bit 12 del pedido (soberano), no en `isClientRosa`.
* C2: Factura borrador + remito puente solo si `!clienteRosa`.
* C3: `wasIngesta` capturado antes de `clearIngestaData()` â€” bifurcaciÃ³n ingesta/manual.
* C4: "Guardar e Imprimir" con `v-if="pedidosStore.ingestaData"`.
* C5: 409 STRICT_MODE_VIOLATION â†’ early return en catch, bloquea adiciÃ³n de item.

### Hito 3: Motor Bipolar â€” canonizaciÃ³n doctrinaria
* Bit 12 (NO_FISCAL_FORCE=4096) del PEDIDO soberano para IVA.
* `isClientRosa` (Bit 4) exclusivo para restricciones operativas (documentos fiscales).
* Rosa SIEMPRE tiene Bit 12=1, pero el cÃ¡lculo mira el pedido, no el cliente.

### Hito 4: IS_VIRGIN rename global
* `HAS_ACTIVITY â†’ IS_VIRGIN` en 15 archivos. Cero ocurrencias residuales.
* Guard `hard_delete_cliente` invertido: `if not (current_flags & IS_VIRGIN)`.
* SemÃ¡ntica corregida: Bit 1=1 virgen/borrable, Bit 1=0 tocado/bloqueado.
* `nivel_id` huÃ©rfano eliminado en ClientCanvas.vue:1557.

### Hito 5: Roseti 1482 â€” domicilio plantilla Rosa
* Domicilio `ROSETI 1482 CABA` creado en pilot_v5x.db (ID: `59b01b5a...`).
* Constante `DOMICILIO_ROSETI_ID` en `backend/clientes/constants.py`.
* `ClienteService._ensure_domicilio_rosa()` vincula automÃ¡ticamente via `domicilios_clientes` al crear/actualizar cliente Rosa sin domicilios.
* DeprecaciÃ³n documentada: `cliente_id` legacy en `Domicilio` model.

### Commits
* `c2372d5a`: fixes pedidos C1/C3/C5 backend + C1-C5 frontend + isSinIVA Motor Bipolar.
* `bb5576c9`: IS_VIRGIN rename global + guard invertido + Roseti 1482 + isGeneric fix.
* `4010b655`: IS_VIRGIN rename `facturacion/constants.py` â€” cobertura global.

---

## SESIÃ“N 808: DOCTRINA VIRGINIDAD + ATOMICIDAD INGESTA + UX FIXES (OF)
**Fecha:** 2026-05-15
**LocaciÃ³n:** OF
**Objetivo:** Implementar Doctrina de Virginidad canÃ³nica. Fix UX PedidoCanvas. Fix Rosa AFIP bypass. Diagnosticar y corregir 409 ingesta. Atomicidad IngestaService.approve(). Sync Dâ†”P.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash D: 513796bf | Hash P: 5865616

### Hito 1: FIX UX PedidoCanvas
* BotÃ³n "Guardar e Imprimir": `v-if="pedidosStore.ingestaData"` â€” oculto en flujo manual.
* `wasIngesta` capturado antes de `clearIngestaData()` para evitar bug de evaluaciÃ³n tardÃ­a.
* Post-guardado manual: reset de canvas (items, cliente, nroPedido, fechas, notas) + notificaciÃ³n "listo".
* Post-guardado ingesta: redirecciÃ³n a PedidoList (comportamiento anterior conservado).

### Hito 2: FIX Rosa / OPERATOR_OK bypass AFIP
* `esOperatorOk = !!(flags_estado & 16)` evaluado en `savePedido()`.
* Si activo: salta todo el bloque fiscal (sin borrador factura, sin remito puente).
* Muestra warning al operador: "Cliente sin circuito AFIP â€” emitir remito manual si corresponde."

### Hito 3: Doctrina de Virginidad â€” implementaciÃ³n canÃ³nica
* **Removidos triggers incorrectos:**
  - `clientes/service.py`: eliminada lÃ­nea `~HAS_ACTIVITY` del bloque 4 pilares.
  - `remitos/service.py` (Vanguard Canon): `mutation_flags = current_flags | target_base` (preserva Bit 1).
* **Agregados triggers canÃ³nicos:**
  - `pedidos/router.py`: hook en PATCH â€” si `estado == "CUMPLIDO"` y Bit 1 activo â†’ apagarlo.
  - `facturacion/service.py`: hook en `sellar_factura` â€” si `update_data.cae` â†’ apagar Bit 1 del cliente.
* **Ghost pedido:** `remitos/service.py` lÃ­nea ~532: `estado="PENDIENTE"` (era "CUMPLIDO").
* Commits: D `8e703914` / P `3690673` (cherry-pick con conflicto resuelto).

### Hito 4: DiagnÃ³stico 409 ingesta
* Raw `80af6b8b` (Labme, 0001-00002535): `audit_status='RECIBIDO'` pero downstream ya existÃ­a.
* Causa raÃ­z: commit parcial previo â€” `create_from_ingestion` comiteÃ³, segundo commit de `approve()` nunca corriÃ³.
* ReconciliaciÃ³n manual: `UPDATE ingesta_facturas_raw SET audit_status='PROCESADO'...` (PIN 1974).

### Hito 5: Atomicidad IngestaService.approve()
* AuditorÃ­a: 2 commits no atÃ³micos con ventana de inconsistencia entre ellos.
* `remitos/service.py`: `db.commit()` â†’ `db.flush()` en cierre principal y path `solo_actualizar_cliente`.
* `ingesta/service.py`: checkpoint `PROCESANDO` pre-vuelo, try/except con `ERROR` en fallo, Ãºnico commit al final.
* `remitos/router.py`: `db.commit()` explÃ­cito en endpoint deprecated `POST /ingesta-process`.
* Commit: D `513796bf` / P `5865616`.

### Hito 6: Sync Dâ†”P
* 4 cherry-picks a P en orden cronolÃ³gico (807-808).
* Conflicto en `_GY/_MD/` (burocracia): destagiado.
* Conflicto en `clientes/service.py`: resuelto con versiÃ³n D (IS_VIRGIN eliminado).
* Push P: `d3173b2..5865616`.

---

## SESIÃ“N 807: SILO DRIVE + PRICING ENGINE SOBERANO + PROTOCOLOS ALFA/OMEGA (OF)
**Fecha:** 2026-05-14
**LocaciÃ³n:** OF
**Objetivo:** Crear Silo Drive como centro de comando entre sesiones. Fix pricing engine 409. Actualizar protocolos ALFA y OMEGA en D y P. Sync DB 807d de MT a D.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash D: 0b34f1f9 | Hash P: d3173b2

### Hito 1: Silo Drive
* `Q:\Mi unidad\V5_Silo_Claude\` creado â€” README.md, INBOX.md, ESTADO_ECOSISTEMA.md, estructura OF/CA/GLOBAL/LEIDOS.
* Bug #1 OF/P resuelto y marcado RESUELTO en `OF/P/BUGS.md` del Drive.

### Hito 2: Protocolos ALFA y OMEGA
* `ALFA.md` D y P: PASO 0 â€” lectura INBOX + ESTADO_ECOSISTEMA antes de operar.
* `OMEGA.md` D: FASE 1B WAL checkpoint (`pilot_v5x.db`) + ESTADO_ECOSISTEMA en FASE 2.
* `OMEGA.md` P: Ã­dem, con ruta `data\V5_LS_MASTER.db`.

### Hito 3: Fix Pricing Engine
* Causa raÃ­z bug #1: `get_virtual_price()` abortaba con `PRODUCTO_SIN_COSTO` cuando `costos=None`.
* `pricing_engine.py`: sin_costo=True (no bloqueante) vs STRICT_MODE_VIOLATION (bloqueante real).
* `router.py`: 409 solo para STRICT_MODE_VIOLATION. Flag `sin_costo` expuesto en respuesta.
* Verificado en vivo: SKU 80018/80019 â†’ HTTP 200, precio=0, sin_costo=True.
* Cherry-pick a P: hash `922da85`.

### Hito 4: DB y Deuda TÃ©cnica
* DB 807d instalada en D desde MT (1.974.272 bytes).
* Pedido 38 eliminado (Pao Tandil â€” ingresado incompleto, a recrear).
* 3 deudas tÃ©cnicas registradas en DB: Badge FALTAN, Guardar e Imprimir, etiqueta botÃ³n por contexto.

---

## SESIÃ“N 806: ARLEQUÃN V2 â€” INFERENCIA ROSA + GENOMA_UNIVERSAL + FIX NO_FISCAL_FORCE (OF)
**Fecha:** 2026-05-13
**LocaciÃ³n:** OF
**Objetivo:** Sellado del GENOMA_UNIVERSAL, purga de herejÃ­a NO_FISCAL_FORCE, implementaciÃ³n completa Doctrina ArlequÃ­n V2, blindaje Consumidor Final y MOSTRADOR, sincronizaciÃ³n Dâ†’P.
**Estado:** NOMINAL GOLD â€” PIN 1974 | Hash D: abd34332 | Hash P: 2d7c5c2

### Hito 1: Infraestructura MT (sesiÃ³n 805/806 bridge)
*   MigraciÃ³n 033 schema sync Pâ†D (facturas_remitos + bugs + tablas faltantes).
*   Python 3.11.9 restaurado en MT â€” venv reparado.
*   Flujo ingestaâ†’pedidoâ†’remito operativo en MT.
*   DevBadge oculto en producciÃ³n (import.meta.env.DEV).
*   Task Scheduler recreado en MT.

### Hito 2: GENOMA_UNIVERSAL sellado
*   `docs/GENOMA_UNIVERSAL.md` creado â€” mapa canÃ³nico 64-bit para Clientes, Productos, Pedidos, Facturas (RAW/PRC/Madre) y Remitos.
*   AuditorÃ­a forense Nike Arq 5.5: resoluciÃ³n de contradicciones entre sesiones 798, 800-OF, 800-CA y 806.
*   NO_FISCAL_FORCE corregido Bit10â†’Bit12 (herejÃ­a purgada): `constants.py`, `PedidoList.vue` (6 referencias), `router.py`.

### Hito 3: Doctrina ArlequÃ­n V2
*   Inferencia automÃ¡tica Rosa: `_audit_sovereignty()` enciende OPERATOR_OK (Bit4) si tiene segmento y sin CUIT real.
*   `clientValidation` en PedidoCanvas y `evaluateCliente` en useAuditSemaphore reescritos con lÃ³gica por bits.
*   Consumidor Final blindado: CUIT 00000000000 forzado GOLD_ARCA en `_audit_sovereignty()`.
*   CUIT 00000000000 declarado exclusivo MOSTRADOR/GENÃ‰RICO â€” bloqueo HTTP 400 en create y update.

### Hito 4: DocumentaciÃ³n y Cierre
*   `PROTOCOLO_EMERGENCIA_MT.md` creado â€” flujo canÃ³nico Dâ†’Pâ†’MT sellado.
*   7 Ã­tems registrados en `deuda_tecnica` (sesiÃ³n 806).
*   Cherry-pick 4 commits Dâ†’P: limpio, sin conflictos.
*   Push D y P a GitHub confirmado.
*   Canario OMEGA: LAVIMAR flags=13 â€” NOMINAL GOLD.

---

## SESIÃ“N 802: ESTABILIZACIÃ“N INFRAESTRUCTURA Y SOBERANÃA TOMY (OF)
**Fecha:** 2026-05-11
**LocaciÃ³n:** OF
**Objetivo:** Saneamiento integral de ProducciÃ³n (Tomy), normalizaciÃ³n de rutas legacy, unificaciÃ³n de repositorio Git (P), eliminaciÃ³n de mock data en UI y formalizaciÃ³n de protocolo OMEGA manual.
**Estado:** NOMINAL GOLD â€” PIN 1974

### Hito 1: NormalizaciÃ³n de Infraestructura (P)
*   Renombramiento de raÃ­z a `v5-ls-Tom` y saneamiento de rutas `C:/dev/V5-LS` en 28 archivos.
*   ActualizaciÃ³n de archivos `.env` (raÃ­z, current, staging) para apuntar a las bases de datos correctas.
*   SincronizaciÃ³n de paridad en Staging (P) con puertos y bases asignadas.

### Hito 2: UnificaciÃ³n Git Tomy
*   Merge exitoso de ramas divergentes en `v5-ls-Tom`.
*   ResoluciÃ³n de conflicto en `PedidoCanvas.vue` preservando lÃ³gica V5.7 GOLD (`checkout --ours`).
*   Limpieza de binarios (`.db`, `.pyc`) del Ã­ndice de Git para asegurar un repositorio liviano.
*   Push exitoso a GitHub unificando entornos OF y CA.

### Hito 3: Saneamiento de CÃ³digo y Deuda TÃ©cnica
*   EliminaciÃ³n de mock data (historial/habituales) en `ClientCanvas.vue` en D y P.
*   Registro de deuda tÃ©cnica en `pilot_v5x.db` para integraciÃ³n de API real.
*   FormalizaciÃ³n de OMEGA manual en `ALFA.md`.

### Hito 4: AuditorÃ­a OMEGA V2.2
*   Canario D validado (LAVIMAR flags=13).
*   GeneraciÃ³n de Informe HistÃ³rico y actualizaciÃ³n de Genoma Documental.

---

## SESIÃ“N 801: DESPLIEGUE TOMY + DIAGNÃ“STICO D VS P (CA)
**Fecha:** 2026-05-10
**LocaciÃ³n:** CA
**Objetivo:** DiagnÃ³stico de paridad entre repositorios P y D, registro de deuda tÃ©cnica en pilot_v5x.db, y creaciÃ³n de automatizaciÃ³n ACTUALIZAR_V5.bat para instancia de Tomy.
**Estado:** NOMINAL GOLD â€” PIN 1974

### Hito 1: DiagnÃ³stico de Repositorios (D vs P)
*   ConfirmaciÃ³n de bicefalÃ­a de repositorios: P (`v5-ls-Tom`) y D (`Sonido_Liquido_V5`) operan sobre remotos distintos.
*   Hash P: `a7759c6` (OMEGA 796).
*   Hash D: `8027b685` (OMEGA 800).
*   IdentificaciÃ³n de 10 commits pendientes de integraciÃ³n en P desde la rama principal de D.

### Hito 2: AutomatizaciÃ³n de Despliegue
*   CreaciÃ³n de `ACTUALIZAR_V5.bat` en la raÃ­z para permitir updates autÃ³nomos via `git pull`.
*   ValidaciÃ³n de entorno Git y manejo de errores de red/conflictos.

### Hito 3: Registro de Deuda TÃ©cnica
*   ActualizaciÃ³n de tabla `deuda_tecnica` en `pilot_v5x.db`.
*   InserciÃ³n de 4 Ã­tems: Deploy Tomy (Alta), Stock/DepÃ³sitos (Media), Precios PDF (Media), ABM Rubros (Baja).

### Hito 4: Burocracia OMEGA
*   ActualizaciÃ³n de Caja Negra, Manuales e Informes HistÃ³ricos.
*   SincronizaciÃ³n de `SESION_ACTUAL.md` a Mayo 2026.

---

**Fecha:** 2026-05-08
**LocaciÃ³n:** OF
**Objetivo:** Estandarizar numeraciÃ³n de remitos (0016-XXXXXXXX), finalizar MÃ³dulo Ingesta V2, implementar Conserje V2 auditorÃ­a READ ONLY, fix em dash en remito_engine, y habilitar live preview de numeraciÃ³n.
**Estado:** NOMINAL GOLD â€” Hash: 9e593e67

### Hito 1: EstandarizaciÃ³n Sabueso V5.7
*   ConsolidaciÃ³n del protocolo de numeraciÃ³n **0016-XXXXXXXX** en todos los flujos. EliminaciÃ³n de regresiones a la serie 0015-.
*   `backend/remitos/pdf_parser.py`: Mejora en extracciÃ³n de Punto de Venta y NÃºmero de Comprobante (insensible a espacios/guiones).
*   `backend/remitos/service.py`: LÃ³gica de resoluciÃ³n jerÃ¡rquica de `numero_legal` priorizando factura real sobre Pedido ID.

### Hito 2: MÃ³dulo Ingesta V2 + Conserje READ ONLY
*   FinalizaciÃ³n de flujo `FacturasRaw` -> `FacturasProcesadas`.
*   ImplementaciÃ³n de Conserje V2: motor de auditorÃ­a `READ ONLY` con scoring de domicilios y validaciÃ³n de identidades sellado por Nike Arq 5.5.
*   Protocolo Bit 22: Establecimiento de `PRE_MODULO_FACTURACION` (Flag 4227083) para vinculaciÃ³n fiscal espejo.

### Hito 3: Fixes UI/UX y Motor de PDF
*   `frontend/src/views/Pedidos/IngestaFacturaView.vue`: HabilitaciÃ³n de Live Preview del nÃºmero de remito resultante para evitar errores de carga.
*   `remito_engine.py`: Fix em dash en header/footer (lÃ­neas 74 y 167) para asegurar estÃ©tica doctrinal.

### Hito 4: Saneamiento y Cierre OMEGA 2.2
*   Purgado intencional de registros de prueba (LABME, Pedido 32) en base D.
*   EjecuciÃ³n de Protocolo OMEGA completo con PIN 1974.

## SESIÃ“N 799: GENOMA FACTURAS + CONSERJE DUPLICADOS + MANUALES (CA)
**Fecha:** 2026-05-08
**LocaciÃ³n:** CA
**Objetivo:** Implementar Genoma `FacturaFlags` (mapa bits 0-21 sellado Nike Arq 5.5), campo `notas_auditoria` en modelo Factura, migraciÃ³n 029, conserje HTTP 409 `FACTURA_DUPLICADA` en ingesta-pdf, y Bug G (pedidos duplicados con modal advertencia).
**Estado:** NOMINAL GOLD â€” hashes: 93a9a3d4, 58404b1b

### Hito 1: `FacturaFlags` â€” Genoma constants.py
*   `backend/facturacion/constants.py` (nuevo): clase de constantes con mapa completo bits 0-21 de `flags_estado` en tabla `facturas`. Sellado Nike Arq 5.5. Bits: EXISTENCE(1), HAS_ACTIVITY(2), HAS_REMITO(4), ACTIVE(8), V15_STRUCT(1024), PASADO_A_PEDIDO(32768), EN_CUARENTENA(65536), TIENE_NC(131072), TIENE_ND(262144), ES_NC(524288), ES_ND(1048576), AUDITADA(2097152). Bits 22-29 reservados contabilidad. Bits 30+ ultra-reservados.

### Hito 2: Campo `notas_auditoria` + MigraciÃ³n 029
*   `backend/facturacion/models.py`: `notas_auditoria = Column(String, nullable=True)` agregado a clase `Factura`. Campo de texto libre para observaciones de auditorÃ­a manual â€” complementa bit `AUDITADA` (bit 21).
*   `scripts/migrate_029_facturas_notas_auditoria.py` (nuevo): `ALTER TABLE facturas ADD COLUMN notas_auditoria VARCHAR`. Idempotente, registra en `_migraciones_aplicadas`. Ejecutada en pilot_v5x.db.

### Hito 3: Conserje FACTURA_DUPLICADA en ingesta-pdf
*   `backend/remitos/router.py` â€” `POST /remitos/ingesta-pdf`: guard pre-proceso. Consulta `facturas` por `punto_venta + numero_comprobante`. Si existe â†’ HTTP 409 `{"codigo": "FACTURA_DUPLICADA", "factura_id": "<uuid>"}`. El frontend puede redirigir al registro existente. Hash: 93a9a3d4.

### Hito 4: Bug G â€” Pedidos duplicados
*   Modal de advertencia al detectar posible pedido duplicado (mismo cliente + fecha + Ã­tems similares). Operador puede continuar o cancelar. Hash: 58404b1b.

---

## SESIÃ“N 798: BUGS D/E/F/H + EXTRACCIÃ“N INGESTAITEMMODAL (OF)
**Fecha:** 2026-05-07
**LocaciÃ³n:** OF
**Objetivo:** Cerrar Bugs D/E/F (F4 satÃ©lite en PedidoCanvas), extraer IngestaItemModal a componente propio, implementar Fix H (F4 funcional dentro del modal) y botÃ³n copy descripciÃ³n.
**Estado:** NOMINAL GOLD â€” hashes: db72e856, afd5cd74

### Hito 1: Bugs D/E/F â€” F4 satÃ©lite PedidoCanvas
*   `PedidoCanvas.vue`: nombre Ãºnico `AltaProducto_${Date.now()}` â€” fuerza ventana nueva, no reutiliza tab bloqueado.
*   `ProductosView.vue`: `v-if="route.query.mode !== 'satellite' || showInspector"` en `<main>` â€” bloquea F4 handler hasta que inspector estÃ© listo.
*   `ProductoInspector.vue`: `fetchRubros()` defensivo en `onMounted` cuando store vacÃ­o (modo satellite omite App.vue boot). Hash: db72e856.

### Hito 2: ExtracciÃ³n IngestaItemModal.vue + Fix H + botÃ³n copy
*   `Ventas/components/IngestaItemModal.vue` (nuevo, 110 lÃ­neas): modal de resoluciÃ³n de Ã­tems extraÃ­do de PedidoCanvas. Props: `items`. Emits: `resolved(items)`, `cancel`.
*   Fix H: `handleOverlayKeydown` captura F4 internamente, abre satÃ©lite de alta producto â€” burbujeo detenido antes de llegar a PedidoCanvas.
*   BotÃ³n copy `fa-copy` junto a descripciÃ³n de factura â†’ llena `searchTerm` con un click.
*   `PedidoCanvas.vue` âˆ’137 lÃ­neas neto: 6 refs â†’ 2, 5 funciones â†’ 3, guard `showIngestaModal` en F4. Hash: afd5cd74.

---

## SESIÃ“N 797: BUG C BACKEND + SISTEMA DE MIGRACIONES (CA)
**Fecha:** 2026-05-06
**LocaciÃ³n:** CA
**Objetivo:** Resolver Bug C â€” flujo pedidoâ†’facturaâ†’remito incompleto. AuditorÃ­a forense del backend: 7 bugs crÃ­ticos identificados (B-1 a B-7). ImplementaciÃ³n modelo N:M `FacturaRemito` + sistema de control de migraciones idempotente. Bug B (modal 409) tambiÃ©n resuelto.
**Estado:** NOMINAL GOLD â€” ver informe: `INFORMES_HISTORICOS/2026-05-06_BUG_C_BACKEND_MIGRACIONES_CA.md`
**Hash:** 529aa2be

### Hito 1: Bug B â€” ESC no restaura modal 409
*   `frontend/src/stores/pedidos.js`: `pending409Context` + `set409Context`/`clear409Context` â€” canal separado que PedidoCanvas nunca toca.
*   `IngestaFacturaView.vue`: `goToNewPedido()` persiste contexto antes de navegar; `onMounted()` lo restaura y reactiva `show409Modal`. Hash: `9df14bdf`.

### Hito 2: Fix B-1 â€” `factura_id: int` â†’ `str`
*   `backend/remitos/router.py:261` y `service.py:586`: parÃ¡metro `int` â†’ `str` + `_uuid.UUID(factura_id)` en query. Endpoint era completamente inoperativo â€” FastAPI rechazaba el UUID antes de llegar al service.

### Hito 3: Fix B-2 â€” `fecha_vto_cae` â†’ `cae_vencimiento`
*   `backend/remitos/service.py:606,634`: campo inexistente corregido al campo real. Crash `AttributeError` en ambas ramas.

### Hito 4: Fix B-3 â€” `numero_legal` con doctrina ARCA real
*   Helper `_numero_legal_arca()`: con CAE â†’ `0016-XXXX-YYYYYYYY`; sin CAE (borrador) â†’ `0015-XXXXXXXX` (serie manual, doctrina Nike). Antes usaba `pedido.id` o UUID del remito â€” violaciÃ³n directa de doctrina.

### Hito 5: Fix B-7 + B-6 â€” campos silenciosos
*   `total_bruto` â†’ `factura.total` (valor_declarado siempre era 0.0).
*   `cuit_comprador` ahora se asigna post-flush en `create_draft_from_pedido` â€” sello histÃ³rico faltante corregido.

### Hito 6: Arquitectura N:M `FacturaRemito`
*   `backend/facturacion/models.py`: `Table` simple â†’ clase `FacturaRemito` completa con GUID, `fecha_vinculo`, `flags_estado`, relaciones bidireccionales (string anti-deadlock).
*   `Factura.remitos` â†’ `Factura.vinculos_remitos` (cascade `all, delete-orphan`).
*   `backend/remitos/models.py`: `Remito.vinculos_facturas` agregado.
*   IntegraciÃ³n en `create_puente_factura`: guard de idempotencia + helper `_vincular_factura_remito()`.
*   MigraciÃ³n 026: `DROP/CREATE TABLE facturas_remitos` con id GUID + fecha_vinculo + flags_estado + UNIQUE(factura_id, remito_id).

### Hito 7: Sistema de control de migraciones
*   `scripts/migrate_000_control_migraciones.py`: crea tabla `_migraciones_aplicadas` (id, nro_sesion, aplicada_en). PatrÃ³n idempotente documentado.
*   `migrate_026_factura_remitos.py` refactorizado: verifica antes de ejecutar â†’ SKIP si ya aplicada. Hash: `529aa2be`.

**Pendiente:** Bug C Ã­tem 13 â€” `savePedido()` en PedidoCanvas no invoca cadena facturaâ†’remito (D-7, sesiÃ³n futura). Build P pendiente OF.

---

## SESIÃ“N 796: PARSER Y-AXIS FIX + MODAL SYNC CA â€” INGESTA PDF ITEMS RESUELTO
**Fecha:** 2026-05-05
**LocaciÃ³n:** CA
**Objetivo:** Resolver causa raÃ­z de items[] vacÃ­o en flujo PDFâ†’modal PedidoCanvas. Fix Y-axis tolerance `/4`â†’`/6` en pdf_parser.py. Sync Dâ†”P. Canario actualizado TARGET_FLAGS 8205â†’13.
**Estado:** NOMINAL GOLD â€” ver informe: `INFORMES_HISTORICOS/2026-05-05_INGESTA_PARSER_FIX_MODAL_SYNC_CA.md`

### Hito 1: Fix Y-Axis Tolerance (CRÃTICO)
*   `pdf_parser.py` lÃ­nea 137: `round(y0/4)*4` â†’ `round(y0/6)*6`. Tolerancia Â±2pts insuficiente para PDFs AFIP (delta real: 5pts entre qty y u_medida). Items array no-vacÃ­o confirmado. Caso: L EPI S.R.L. â€” Alcohol 70% â€” qty=4,00 precio=$13.500,00.

### Hito 2: Fix Typo Producto
*   `pilot_v5x.db` ID 150 SKU 10211: "Acohol" â†’ "Alcohol". Search modal OK.

### Hito 3: Canario v2.py â€” ActualizaciÃ³n Post-Saneamiento
*   `TARGET_FLAGS = 8205` â†’ `TARGET_FLAGS = 13` en D y Tom. Canario reportaba DESVÃO CRÃTICO con flags=13 por no haber sido actualizado tras saneamiento 2026-05-02 (bit 8192 eliminado). INTEGRITY NOMINAL GOLD confirmado en ambos.

### Hito 4: Null-checks + Sync + Addendum OF
*   Commit 7b5794d: null-checks router.py Tom. Commit 534178b: PedidoCanvas sync. Commit 8c658f63: bitÃ¡cora addendum OF.

**Bugs backlog:** Bug A (search pisa ref), Bug B (ESC modal 409), Bug C (ciclo pedidoâ†’facturaâ†’remito), Clientes azules. Build P pendiente OF.

---

## SESIÃ“N 795: MODAL RESOLUCIÃ“N ÃTEMS â€” UX + VISUAL (OF)
**Fecha:** 2026-05-05
**LocaciÃ³n:** OF
**Objetivo:** Fix visual y UX del modal de resoluciÃ³n de Ã­tems en PedidoCanvas. DiagnÃ³stico inicial de items[] vacÃ­o.
**Estado:** NOMINAL â€” ver informe completo: `INFORMES_HISTORICOS/2026-05-05_MODAL_INGESTA_ITEMS_UX_OF.md`
**Hash:** 296a120e

---

## SESIÃ“N 794: ARLEQUÃN V2 MERGE QUIRÃšRGICO CA + DOCTRINA BIT 1 RESUELTA
**Fecha:** 2026-05-04
**Objetivo:** Merge de feature/arleq-v2-productos en D. ResoluciÃ³n definitiva Bit 1 Clientes/Productos. OMEGA V2.2 desplegado en D y P.
**Estado:** NOMINAL GOLD â€” ver informe completo: `INFORMES_HISTORICOS/2026-05-04_ARLEQ_V2_MERGE_QUIRURGICO_CA.md`

---

## SESIÃ“N 793: SIEMBRA DE CONTACTOS + SOBERANÃA LOCAL (PURGA POSTGRESQL)
**Fecha:** 2026-04-19
**Objetivo:** ImportaciÃ³n masiva de contactos (Person-Centric) y eliminaciÃ³n total de dependencias a base de datos externa.

### Hito 1: Purga PostgreSQL â€” SoberanÃ­a Total
*   **RaÃ­z del problema**: Variable de entorno de sistema Windows `DATABASE_URL=postgresql://...34.95.172.190` pisaba todo el stack. Toda sesiÃ³n de scripts apuntaba a la nube sin importar .env.
*   **Capas eliminadas**: (1) variable de sistema Windows (`SetEnvironmentVariable null`), (2) `backend/.env` reescrito a SQLite, (3) `backend/.env.bak` y `.env.postgres_fail` eliminados.
*   **Defensa instalada**: `import_contactos_bulk.py` carga `.env` local y rechaza cualquier URL postgres antes de inicializar ORM.

### Hito 2: ReparaciÃ³n de Mappers SQLAlchemy
*   `backend/clientes/models.py`: imports explÃ­citos de `EmpresaTransporte` y `Pedido` â†’ eliminados `InvalidRequestError` en cadena.
*   `backend/pedidos/models.py`: import explÃ­cito de `Producto` â†’ resuelto mapper de `PedidoItem`.
*   `backend/contactos/models.py`: campo `notas_sistema` (Text, nullable) â†’ segregaciÃ³n notas script vs notas usuario.
*   SQLite: `ALTER TABLE personas ADD COLUMN notas_sistema TEXT DEFAULT NULL`.

### Hito 3: Siembra de Contactos Person-Centric
*   Script `import_contactos_bulk.py` ejecutado sobre `contactos_siembra_gmail_20260419_01.json` (10 registros).
*   Resultado: 10 personas nuevas, 7 vÃ­nculos comerciales, 3 `[ENTIDAD_PENDIENTE]` (Rizobacter).
*   Genoma: Bit 5 (CANTERA_NIKE=16) en todos. Bit 6 (VINCULO_DUDOSO=32) en 5 fuzzy 70-98%.
*   `notas_sistema` auditadas por registro: origen, % fuzzy, cargo, entidad pendiente.

### Hito 4: Limpieza de Lastre
*   Eliminados: `ingest_memory.py`, `config.py`, `backend/data/*.txt`, `atenea_memory.db` â€” todos dependÃ­an de Google Cloud.

**Estado:** NOMINAL GOLD. Protocolo Omega ejecutado. PIN 1974.

---

## SESIÃ“N 792: SANEAMIENTO REMITOS (RAR-V1) + RESILIENCIA DE IDENTIDAD (V5-LS)
**Fecha:** 2026-04-16
**Objetivo:** Estabilizar motor de remitos, corregir el bug de reversiÃ³n de CUIT y eliminar Error 500 en auditorÃ­a de domicilios. Paridad total D/P.

### Hito 1: Saneamiento Remitos (RAR-V1)
*   **Flexibilidad**: Campos `bultos` y `valor_declarado` ahora son Nullable (Base y Schema).
*   **PDF Engine**: Etiquetas fijas ("BULTOS:", "VALOR DECL.:") con impresiÃ³n condicional de valores. QR oficial: `https://liquid-sound.com.ar/`.
*   **Datoscopio**: ImplementaciÃ³n de `@property resumen` en modelo `Domicilio` para visualizaciÃ³n unificada de direcciones en remitos legales.

### Hito 2: Resiliencia de Identidad (V5-LS)
*   **SoberanÃ­a CUIT**: Tras validaciÃ³n ARCA, el CUIT corregido sobreescribe reactivamente el dato de Cantera en el frontend (`ClientCanvas.vue`). Erradicado el bug de reversiÃ³n a datos legacy.
*   **Error 500 Audit**: Null-safety en `_audit_sovereignty` de `service.py`. Ya no falla ante clientes con CondiciÃ³n IVA incompleta.
*   **Error 422**: Manejo robusto de IDs de domicilio malformados (`null`), redirigiendo a `POST` cuando es necesario.

### Hito 3: HomologaciÃ³n P/D (Omega Sync)
*   SincronizaciÃ³n total de mÃ³dulos hacia `C:\dev\V5-LS\current`.
*   Paridad absoluta de lÃ³gicas de negocio y blindaje de identidad.

**Estado:** NOMINAL GOLD. Protocolo Omega ejecutado. PIN 1974.

---

## SESIÃ“N 791: PRODUCCIÃ“N SOBERANA â€” FIXES OPERATIVOS + DISEÃ‘O DOCTRINAL
**Fecha:** 2026-04-15
**Objetivo:** Corregir bugs detectados en tiempo real por Tomy en producciÃ³n (D/V5-LS). Sync completo a P.

### Hito 1: Fix Triple â€” Domicilios 500
* Bug A: `is_maps_manual` duplicate kwarg en `create_domicilio` â†’ `TypeError` â†’ 500.
* Bug B: `domicilios_clientes` junction table no insertada â†’ domicilio invisible en GET.
* Bug C: Pinia store `createDomicilio` reemplazaba cliente con domicilio â†’ loop navegaciÃ³n.

### Hito 2: Fix CrÃ­tico â€” PedidoCanvas Edit Mode
* `savePedido()` siempre usaba POST. Ahora: si `route.params.id` â†’ PATCH. El endpoint ya existÃ­a.
* Limpieza manual DB: 5 pedidos duplicados eliminados (dos pasadas). PrÃ³ximo pedido: #20.

### Hito 3: Fix Rosa Clients
* `clienteEsVerde` ahora detecta Rosa (`flags_estado & 15 in [9,11]`) y devuelve `true` sin validar CUIT/domicilio.

### Hito 4: MigraciÃ³n GENERAL â†’ General
* D: 4 productos. P: 7 productos. GENERAL (id=28) dado de baja en ambas DBs.

### Hito 5: Fix PedidoInspector â€” Nota visible
* BotÃ³n editar nota siempre visible (eliminado `opacity-0 group-hover`).

### Hito 6: DiseÃ±o Doctrinal â€” OrÃ­genes de Pedido
* Acordado: bits libres de `flags_estado` para `BIT_ORIGEN_FACTURA` y `BIT_ORIGEN_REMITO`.
* ImplementaciÃ³n pendiente prÃ³xima sesiÃ³n.

**Estado:** NOMINAL GOLD. Build D ejecutado (6.91s). Commits y push D y P.

---

## SESIÃ“N 790: SANEAMIENTO DB + FIXES OPERATIVOS + PARIDAD D/P
**Fecha:** 2026-04-14
**Objetivo:** Sanear pilot_v5x.db (paridad con P), fixes de cantera import, F4, Rubro obligatorio e infraestructura.

### Hito 1: CirugÃ­a DB pilot_v5x.db (PIN 1974)
*   7 fusiones de grupos duplicados. Pedidos de 173 y 159 re-apuntados a survivors 177 y 175.
*   IDs 158, 159, 160 (NULL SKU) eliminados fÃ­sicamente.
*   8 productos borrados (flags=0/2, sin movimientos). Total final: 23 productos.

### Hito 2: Cantera Import â€” Fix 500 + Auto-SKU
*   `flags_estado=3` en creaciÃ³n desde cantera (ACTIVE+VIRGIN).
*   Auto-SKU: `MAX(sku)+1` con piso 9001 cuando el mirror no trae SKU.
*   SKU como `int(float(...))` â€” compatible con mirror JSON que puede traer floats.
*   `margen_mayorista` â†’ `rentabilidad_target` (campo renombrado en modelo).
*   Paridad D/P: mismo fix aplicado en ambos entornos.

### Hito 3: Fixes Frontend
*   F4 en PedidoCanvas: product search tiene prioridad; modal cliente solo en foco explÃ­cito.
*   ProductoInspector: asterisco rojo + ring de error + mensaje `rubroError` para campo Rubro.

### Hito 4: Infraestructura
*   DESPERTAR.ps1: guard null reference sin .bak / Git no disponible.
*   boot_system.py: `--reload-dir backend` + health check polling.
*   main.py: `/` â†’ `/health` en D y P â€” libera catch-all SPA.

**Estado:** NOMINAL GOLD. Commit OMEGA ejecutado.

---

# [V5.7.0] 2026-04-09 - HomologaciÃ³n Identity Shield (Bag of Words)
> **ESTADO:** SATISFACTORIO (NOMINAL GOLD)
> **TIPO:** HOMOLOGACIÃ“N / SEGURIDAD / SYNC P-D

**Hitos:**
1. **HomologaciÃ³n Genoma V5-LS:** SincronizaciÃ³n total del blindaje "Bag of Words" hacia entorno Staging.
2. **Backfill Productivo:** InyecciÃ³n de `razon_social_canon` en `V5_LS_STAGING.db` y normalizaciÃ³n de 35 registros legÃ­timos.
3. **Sensor UI:** ActivaciÃ³n de detector de duplicados reactivo debounced en `ClientCanvas.vue`.
4. **Dictamen de AuditorÃ­a:** Certificado `audit_production_duplicates.py` limpio.

**Archivos:** `backend/clientes/service.py` | `router.py` | `frontend/src/views/Hawe/ClientCanvas.vue` | `_GY/_MD/CAJA_NEGRA.md`

---

# [V16.2.0] 2026-04-08 - Blindaje Nuclear de Identidad (BOW Protocol)
> **ESTADO:** SATISFACTORIO (NOMINAL GOLD)
> **TIPO:** SEGURIDAD / IDENTIDAD / HOMOLOGACIÃ“N

**Hitos:**
1. **Protocolo Bag of Words (BOW):** ImplementaciÃ³n de `normalize_name` V16.2. La identidad ahora es insensible al orden de las palabras ("Inapyr SRL" == "SRL Inapyr").
2. **HÃ©metizaciÃ³n Estructural (HomologaciÃ³n):** SincronizaciÃ³n total entre entornos D (`Sonido_Liquido_V5`) y P (`V5-LS`). InyecciÃ³n de columna `razon_social_canon` en la DB maestra.
3. **Saneamiento QuirÃºrgico:** EliminaciÃ³n fÃ­sica de registros duplicados en pedidos (ID 6 y 7) y reseteo de secuencia SQLite en producciÃ³n.
4. **Sensor de Identidad UI:** IntegraciÃ³n de alertas de colisiÃ³n semÃ¡ntica en tiempo real en `ClientCanvas.vue`.

**Archivos:** `backend/clientes/service.py` | `router.py` | `ClientCanvas.vue` | `V5_LS_MASTER.db`

---

# [V15.2.1] 2026-03-23 - SoberanÃ­a Hub & UnificaciÃ³n de Registro
> **ESTADO:** SATISFACTORIO (NOMINAL GOLD)
> **TIPO:** FEATURE / REFACTOR / DATA MIGRATION

**Hitos:**
1. **SoberanÃ­a del Hub:** Implementada la siembra del Address Hub mediante `seed_hub.py`. Se migraron 47 domicilios legacy a 43 registros Ãºnicos en el Hub Soberano con deduplicaciÃ³n semÃ¡ntica.
2. **Bit 21 (Espejo):** ActivaciÃ³n del bit 2097152 para todos los vÃ­nculos migrados, garantizando paridad con datos histÃ³ricos de Clientes.
3. **UnificaciÃ³n de Registro:** Eliminada la "BicefalÃ­a de Registros" unificando todas las importaciones de `Base` a `backend.core.database`.
4. **Resiliencia de API:** Fix en `DomicilioResponse` para soportar `cliente_id` opcional y repoblaciÃ³n quirÃºrgica del registry en `service.py`.

**Archivos:** `backend/main.py` | `backend/clientes/models.py` | `schemas.py` | `service.py` | `router.py` | `backend/pedidos/models.py`

---

# [V15.2.0] 2026-03-20 - RestauraciÃ³n LogÃ­stica & Protocolo ALFA V5.2
> **ESTADO:** SATISFACTORIO (CON DEUDA)
> **TIPO:** FEATURE / PROTOCOLO / BUGFIX

**Hitos:**
1. **EdiciÃ³n de Remitos (Doble Clic):** Restaurada la capacidad de editar cabeceras de remitos (`BORRADOR`) desde el listado. Implementado endpoint `PATCH /remitos/{id}` y modal reactivo.
2. **SoberanÃ­a ALFA (Fix ORM):** Reparada inconsistencia en el Mapper de Pedidos que bloqueaba `verify_sovereignty.py`.
3. **SincronizaciÃ³n de Bits:** Sergio Jofre (Genoma) sincronizado satisfactoriamente con Bit 19 activo (Valor final: 524301).
4. **Deuda TÃ©cnica (Bit 3):** SesiÃ³n marcada con Bit 3 CRÃTICO debido a que la ediciÃ³n de remitos no incluye bultos, valor declarado ni ediciÃ³n de Ã­tems (Cuerpo).

**Archivos:** `RemitoListView.vue` | `backend/remitos/service.py` | `router.py` | `schemas.py` | `verify_sovereignty.py`

---

# [V15.1.4] 2026-03-19 - LogÃ­stica TÃ¡ctica & EdiciÃ³n de Ingesta
> **ESTADO:** SATISFACTORIO
> **TIPO:** FEATURE / UX / LOGÃSTICA

**Hitos:**
1. **Remito Manual (0015):** Implementada infraestructura para remitos sin factura (Serie 0015-00003001+) con "Ghost Pedidos".
2. **EdiciÃ³n de Ingesta:** Refactorizada la pre-carga de PDF a Grilla Editable (Inputs tactical). Permite corregir OCR, agregar y quitar Ã­tems.
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

# [V14.8.1] 2026-03-17 - ProtecciÃ³n Genoma & Rescate COALIX

> **ESTADO:** SATISFACTORIO
> **TIPO:** RECUPERACIÃ“N / SEGURIDAD CRÃTICA

**Hitos de la SesiÃ³n:**
1. **RecuperaciÃ³n COALIX:** ExtracciÃ³n y restauraciÃ³n total de COALIX SA desde backup SQLite (1). Recuperados domicilios, personas y vÃ­nculos.
2. **Papelera Global (V14.8):** ImplementaciÃ³n de respaldos JSON en `papelera_registros` para toda eliminaciÃ³n fÃ­sica en Utilidades Maestras.
3. **Blindaje Genoma:** Bloqueo de borrado fÃ­sico para registros histÃ³ricos (Bit 1 = 0). ImplementaciÃ³n de "Grisado" visual y estatus "PROTEGIDO" en el frontend.
4. **Fix SerializaciÃ³n:** ImplementaciÃ³n de limpiador recursivo para tipos `Decimal` y `UUID` en el motor de papelera.
5. **ConfiguraciÃ³n:** ResoluciÃ³n definitiva de conflicto de puertos (Bind 8080) para operaciÃ³n estable en LAN.

---

# [V14.8] 2026-03-16 - Saneamiento Genoma & ExpansiÃ³n LAN

# [V6.5.1] 2026-02-28 - SesiÃ³n 787: Protocolo Omega - Ingesta Consolidada
> **ESTADO:** SATISFACTORIO
> **TIPO:** INTEGRACIÃ“N / SINTONÃA FINA

Se completÃ³ la migraciÃ³n del ABM de Clientes de Ingesta al nuevo `ClientCanvas` universal. Se resolvieron los bloqueos del motor PDF y la interferencia de variables de entorno globales (Postgres Ghost).

**Hitos TÃ©cnicos:**
1. **Frontend:** RelajaciÃ³n de validaciones para Ingesta y Auto-InyecciÃ³n de Domicilio PDF.
2. **Backend:** ImplementaciÃ³n de Endpoint `/despachar`, instalaciÃ³n de `fpdf2`, y parche de Pydantic para `AttributeError`.
3. **Parsing:** Regex optimizado para facturas AFIP con formato espacial laxo.

---

# [RECUPERACIÃƒâ€œN] 2026-01-14 - Parche de Emergencia "Math Guard Clauses"

> **ESTADO:** SATISFACTORIO
> **TIPO:** HOTFIX / SEGURIDAD

Se detectÃƒÂ³ y documentÃƒÂ³ retroactivamente el parche de emergencia 'Math Guard Clauses' tras un colapso por Error 500 (DivisiÃƒÂ³n por cero).

**Detalles TÃƒÂ©cnicos:**
1.  **Backend:** Se blindaron `pricing_engine.py` y `router.py` (funciÃƒÂ³n `calculate_prices`) para capturar valores `None` o `0` en `precio_roca` y `costo_reposicion`.
2.  **Resultado:** El sistema devuelve `0.00` en todos los precios calculados en lugar de crashear, permitiendo que el listado de productos cargue incluso con datos corruptos.
3.  **Schemas:** Ajustados `schemas.py` para permitir `0.00` y `Optional` en campos de precios.

**AcciÃƒÂ³n Requerida:** Revisar datos de origen para corregir ceros, pero el sistema ya es estable.

# [V5.4] 2026-01-15 - ImplementaciÃƒÂ³n Multi-Proveedor y Ajustes UI

> **ESTADO:** BLOQUEADO (FRONTEND CRASH)
> **TIPO:** FEATURE / REFINEMENT

**Objetivo:** Implementar "Es Insumo", Selector IVA en Panel Central, y Tabla Multi-Proveedor.

**Avances:**
1.  **Backend (Completado):**
    *   Schema: Creada tabla `productos_proveedores`.
    *   Models: Actualizado `Producto` y creado `ProductoProveedor`.
    *   Router: Agregados endpoints `POST /proveedores` y `DELETE /proveedores/{id}`.
2.  **Frontend (Parcial):**
    *   Implementado layout y lÃƒÂ³gica en `ProductoInspector.vue`.
    *   Agregado servicio en `productosApi.js`.

**Incidente Bloqueante:**
*   El componente `ProductoInspector.vue` crashea al intentar abrirse (spinner infinito o error Vue).
*   **Causa RaÃƒÂ­z Identificada:** InicializaciÃƒÂ³n de arrays en Store (`tasasIva`, `proveedores`) puede ser `null/undefined` en el momento que el `watch(immediate: true)` dispara la lÃƒÂ³gica.
*   **Estado:** Se aplicaron parches de seguridad (`?.` y `|| []`), pero el error persiste. Se requiere revisiÃƒÂ³n profunda del ciclo de vida del componente.

**PrÃƒÂ³ximos Pasos (Protocolo Omega):**
1.  Debuggear inicio de `ProductoInspector` (Store vs Props).
2.  Verificar persistencia de "Es Insumo".
3.
# [V5.6.1] 2026-01-16 - ReparaciÃƒÂ³n Integral Pedidos (Orders Bridge)

> **ESTADO:** ESTABLE
> **TIPO:** HOTFIX / UX RECOVERY

**Objetivo:** Restaurar funcionalidad crÃƒÂ­tica de Pedidos, ImportaciÃƒÂ³n y Alta de Productos, bloqueada por errores de integraciÃƒÂ³n y UX "rota".

**Intervenciones:**
1.  **Backend (Bridge):** Corregido `router.py` para devolver JSON completo y defaults en importaciÃƒÂ³n (`500 Internal Error` Solucionado).
2.  **Frontend (GridLoader):**
    *   **Layout:** Cambiado inspector a `max-w-7xl` (Modal Central) para corregir visualizaciÃƒÂ³n "aplastada".
    *   **Integridad:** Implementada captura de hora local en payload de pedidos.
    *   **Seguridad:** Implementado **Guard Clause** (`isSubmitting`) en F10/Click para evitar pedidos duplicados.
3.  **Frontend (ProductoInspector):**
    *   **Rubros:** Implementado `SelectorCreatable` + `handleCreateRubro` + `fetchRubros` para ABM dinÃƒÂ¡mico en el alta.

**MÃƒÂ©tricas Finales:**
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
    *   **ValidaciÃƒÂ³n:** Pre-check de duplicados (Case Insensitive) antes de llamar al backend.
    *   **Feedback:** Cierre automÃƒÂ¡tico del modal `showAbm = false` tras ÃƒÂ©xito.

**Resultado:** Eliminada la posibilidad de crear duplicados por doble click y restaurado el feedback visual.

# [V5.6.3] 2026-01-16 - SincronizaciÃƒÂ³n Store Domicilios

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA CONSISTENCY

**Objetivo:** Corregir "Ficha Incompleta" persistente tras agregar Domicilio Fiscal.

**DiagnÃƒÂ³stico:**
*   El Store `createDomicilio` y `updateDomicilio` devolvÃƒÂ­a el cliente actualizado al caller (Inspector) pero **NO actualizaba** el array principal `clientes` en memoria.
*   Consecuencia: La vista principal (detrÃƒÂ¡s del inspector) quedaba con datos viejos hasta recargar.

**Intervenciones:**
1.  **Store (clientes.js):**
    *   `createDomicilio/updateDomicilio`: Implementada actualizaciÃƒÂ³n reactiva `this.clientes[index] = response.data`.
    *   `deleteDomicilio`: Agregado `fetchClienteById` automÃƒÂ¡tico tras eliminaciÃƒÂ³n (Backend devuelve 204).

**Resultado:** Al guardar un domicilio, la ficha del cliente se actualiza instantÃƒÂ¡neamente en todas las vistas.

# [V5.6.4] 2026-01-16 - AutonomÃƒÂ­a de Guardado Cliente

> **ESTADO:** DEPLOYED
> **TIPO:** CRITICAL FIX / ARCHITECTURE

**Objetivo:** Solucionar pÃƒÂ©rdida de datos al editar clientes desde el Cargador de Pedidos.

**DiagnÃƒÂ³stico:**
*   El componente `ClienteInspector` delegaba el guardado al padre (`emit('save')`) pero **NO llamaba a la API**.
*   El padre `PedidoTacticoView.vue` **NO escuchaba** el evento save, provocando que los cambios visuales del inspector se perdieran al cerrar el modal.
*   Resultado: El usuario veÃƒÂ­a los cambios en el popup, pero nunca persistÃƒÂ­an en la base de datos.

**Intervenciones:**
1.  **Backend/Store:** (Sin cambios, ya funcionales).
2.  **Frontend (`ClienteInspector.vue`):**
    *   **Refactor:** Implementada llamada directa a `clienteStore.createCliente` y `clienteStore.updateCliente` dentro de la funciÃƒÂ³n `save()`.
    *   **Beneficio:** El componente ahora es autÃƒÂ³nomo y garantiza la persistencia independientemente de quiÃƒÂ©n lo invoque (Pedidos, Clientes, etc.).

**Resultado:** La ediciÃƒÂ³n de clientes (Nombre, CUIT) ahora persiste correctamente en la base de datos y se refleja al cerrar el inspector.

# [V5.6.5] 2026-01-16 - AutonomÃƒÂ­a de Guardado Producto

> **ESTADO:** DEPLOYED
> **TIPO:** REFACTOR / ARCHITECTURE

**Objetivo:** Alinear inspector de productos con la arquitectura de "Componente AutÃƒÂ³nomo" (Self-Saving).

**ImplementaciÃƒÂ³n:**
*   Se replicÃƒÂ³ la lÃƒÂ³gica de `ClienteInspector` en `ProductoInspector.vue`.
*   Ahora el inspector de productos llama directamente a `productosStore.createProducto` o `updateProducto`.
*   Esto habilita su uso seguro desde el Cargador TÃƒÂ¡ctico sin duplicar lÃƒÂ³gica de guardado.

**Resultado:** Arquitectura unificada para ABMs complejos incrustados.

# [V5.6.6] 2026-01-16 - SincronizaciÃƒÂ³n TÃƒÂ¡ctica de Estado

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA COHERENCE

**Objetivo:** Resolver el problema "Pedidos no se entera" tras editar Cliente.

**DiagnÃƒÂ³stico:**
*   Aunque el Inspector guardaba y actualizaba el Store correctamente (V5.6.4), el componente `PedidoTacticoView` ejecutaba un `fetchClientes()` al cerrar el modal.
*   Este `fetch` recargaba la lista "Resumida" del backend (sin array de domicilios completo), sobrescribiendo la versiÃƒÂ³n "Detallada" que acababa de dejar el Inspector en memoria.
*   Resultado: Se perdÃƒÂ­a el estado verde de validaciÃƒÂ³n porque faltaban datos en el objeto cliente recargado.

**Intervenciones:**
1.  **PedidoTacticoView.vue:**
    *   Eliminada la llamada redundante `await clientesStore.fetchClientes()` en `onInspectorClose`.
    *   Implementado listener `@save` para capturar el resultado del inspector y asegurar la selecciÃƒÂ³n inmediata del ID actualizado/creado.

**Resultado:** La vista de Pedidos refleja instantÃƒÂ¡neamente los cambios (Nombre, Estado fiscal) sin parpadeos ni reversiones a datos viejos.

# [V5.6.7] 2026-01-16 - Reactividad Robusta en Store Clientes

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / CORE

**Objetivo:** Garantizar que la UI reaccione a cambios en objetos profundos dentro del array de clientes.

**Problema:**
*   La asignaciÃƒÂ³n directa por ÃƒÂ­ndice (`this.clientes[i] = data`) a veces no disparaba la reactividad en componentes computed complejos (como `clienteSeleccionado` en Pedidos) debido a limitaciones de detecciÃƒÂ³n de cambios en arrays grandes o proxies.

**SoluciÃƒÂ³n:**
*   Se reemplazÃƒÂ³ la asignaciÃƒÂ³n directa por `this.clientes.splice(index, 1, response.data)` en el Store de Clientes (`updateCliente`, `createDomicilio`, `updateDomicilio`).
*   Esto fuerza al motor de reactividad de Vue a reconocer la mutaciÃƒÂ³n del array y propagar el cambio a todas las vistas suscritas.

**Resultado:** ActualizaciÃƒÂ³n visual infalible tras ediciÃƒÂ³n.

# [V5.6.8] 2026-01-16 - BÃƒÂºsqueda Global de Clientes (Cantera)

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / BACKEND

**Objetivo:** Permitir buscar clientes fuera del lÃƒÂ­mite inicial de 1000 registros.

**Problema:**
*   La bÃƒÂºsqueda en el TÃƒÂ¡ctico ("F3") solo filtraba el array local de 1000 clientes precargados. Clientes activos fuera de este lote (ej. clÃƒÂ­nicas especÃƒÂ­ficas) no aparecÃƒÂ­an aunque existieran en DB.

**SoluciÃƒÂ³n:**
*   **Backend:** Se implementÃƒÂ³ filtrado `q` (Query) en el endpoint `GET /clientes` con bÃƒÂºsqueda `ILIKE` en RazÃƒÂ³n Social, FantasÃƒÂ­a y CUIT.
*   **Frontend:** El componente `ClientLookup.vue` ahora dispara la bÃƒÂºsqueda al servidor (con debounce de 300ms) al tipear.
*   Esto actualiza dinÃƒÂ¡micamente el Store con los resultados coincidentes de toda la base de datos ("La Cantera").

**Resultado:** Al tipear "Bio", ahora el sistema busca en toda la base y trae "Biotenk" + todas las clÃƒÂ­nicas biolÃƒÂ³gicas que antes no cargaban.

# [V5.6.9] 2026-01-16 - Acceso Universal a Cantera

> **ESTADO:** DEPLOYED
> **TIPO:** UX / DATA DISCOVERY

**Objetivo:** Facilitar la importaciÃƒÂ³n de clientes histÃƒÂ³ricos incluso si existen coincidencias parciales locales.

**Problema:**
*   Si el usuario buscaba "Bio" y ya existÃƒÂ­a "Biotenk" en el sistema activo, el botÃƒÂ³n para "Buscar en Cantera" desaparecÃƒÂ­a.
*   Esto bloqueaba el acceso a otras entidades (ej. "ClÃƒÂ­nica BiolÃƒÂ³gica") que solo existen en la base histÃƒÂ³rica (`cantera.db`) y necesitan ser importadas.

**SoluciÃƒÂ³n:**
*   Se modificÃƒÂ³ `ClientLookup.vue` para mostrar **siempre** el enlace "Ã‚Â¿No estÃƒÂ¡ aquÃƒÂ­? Buscar en Cantera" al final de la lista de resultados, siempre que haya un tÃƒÂ©rmino de bÃƒÂºsqueda activo.

**Resultado:** Flujo de importaciÃƒÂ³n desbloqueado. Ahora conviven resultados locales activos con la opciÃƒÂ³n de rescatar legado bajo demanda.

# [V5.6.10] 2026-01-16 - Fix DeduplicaciÃƒÂ³n Cantera Productos

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / DATA INTEGRITY

**Objetivo:** Permitir la bÃƒÂºsqueda de productos antiguos (Legado) que no tienen SKU definido.

**Problema:**
*   La lÃƒÂ³gica de bÃƒÂºsqueda en `GridLoader.vue` filtraba los resultados de la Cantera usando `uniqueBy('sku')`.
*   Como gran parte de los productos histÃƒÂ³ricos tienen `sku: null` o vacÃƒÂ­o, el filtro los interpretaba como duplicados y colapsaba cientos de resultados en 1 solo ÃƒÂ­tem (el primero con sku null) o ninguno.

**SoluciÃƒÂ³n:**
*   Se cambiÃƒÂ³ la lÃƒÂ³gica de deduplicaciÃƒÂ³n a `uniqueBy('id')`.
*   Ahora el sistema solo oculta un resultado de Cantera si su **ID** exacto ya existe en la lista de productos activos (Store), independientemente de si tiene SKU o no.

**Resultado:** La bÃƒÂºsqueda de "Bio" en productos ahora trae toda la lista de ÃƒÂ­tems antiguos disponibles para importaciÃƒÂ³n.

# [V5.6.11] 2026-01-16 - Cantera Search: SQL Accent Insensitivity

> **ESTADO:** DEPLOYED
> **TIPO:** UX / SEARCH ENGINE

**Objetivo:** Mejorar la robustez del buscador de Cantera (Maestros HistÃƒÂ³ricos).

**Problema:**
*   SQLite por defecto no soporta bÃƒÂºsquedas insensibles a acentos (`LIKE` normal).
*   El usuario reportÃƒÂ³ que buscar "Clinica" no encontraba "CLÃƒï¿½NICA", "ClÃƒÂ­nica", etc.

**SoluciÃƒÂ³n:**
*   Se inyectÃƒÂ³ una funciÃƒÂ³n personalizada `unaccent` (basada en `unicodedata` de Python) en la conexiÃƒÂ³n SQLite de `CanteraService`.
*   Las consultas SQL de bÃƒÂºsqueda ahora normalizan tanto la columna (`razon_social`, `nombre`) como el tÃƒÂ©rmino de bÃƒÂºsqueda antes de comparar: `WHERE unaccent(col) LIKE unaccent(?)`.

**Resultado:** BÃƒÂºsqueda agnÃƒÂ³stica a mayÃƒÂºsculas, minÃƒÂºsculas y tildes. Buscar "clinica" encuentra "CLÃƒï¿½NICA".

# [V5.6.12] 2026-01-16 - Cantera Import: Missing Domiciles

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX

**Objetivo:** Asegurar que los clientes importados desde Cantera tengan un domicilio vÃƒÂ¡lido inicial.

**Problema:**
*   La funciÃƒÂ³n `import_cliente` ignoraba los campos de direcciÃƒÂ³n (`domicilio`, `ciudad`, `cp`) del JSON legado.
*   El cliente se creaba sin domicilios. El Inspector mostraba una fila vacÃƒÂ­a o inconsistente, y el sistema exigÃƒÂ­a cargar un domicilio fiscal manualmente.

**SoluciÃƒÂ³n:**
*   Se actualizÃƒÂ³ `backend/cantera/router.py` para extraer `calle`, `localidad` y `cp` del objeto de origen.
*   Se crea automÃƒÂ¡ticamente un `Domicilio` inicial marcado como **Fiscal** y **Entrega** durante la importaciÃƒÂ³n.

**Resultado:** Al importar "Alfajores Jorgito", el sistema ahora carga automÃƒÂ¡ticamente su direcciÃƒÂ³n fiscal histÃƒÂ³rica si existe en la Cantera.

# [V5.6.13] 2026-01-16 - Inspector: Force Refresh on Domicile Save

> **ESTADO:** DEPLOYED
> **TIPO:** BUGFIX / UI CONSISTENCY

**Objetivo:** Solucionar inconsistencias visuales al editar domicilios ("ghost rows").

**Problema:**
*   Al guardar un domicilio en el Inspector, la actualizaciÃƒÂ³n optimista del formulario fallaba en reflejar correctamente el estado "Fiscal" o los datos nuevos en clientes importados con datos parciales.
*   El usuario veÃƒÂ­a filas vacÃƒÂ­as o validaciones de "Falta direcciÃƒÂ³n fiscal" incluso despuÃƒÂ©s de cargarla.

**SoluciÃƒÂ³n:**
*   Se modificÃƒÂ³ `ClienteInspector.vue` para forzar una recarga completa del Cliente desde el Backend (`fetchClienteById`) inmediatamente despuÃƒÂ©s de guardar un domicilio.
*   Esto garantiza que el UI muestre exactamente lo que estÃƒÂ¡ en la base de datos, eliminando problemas de reactividad o respuestas parciales.

**Resultado:** EdiciÃƒÂ³n de domicilios robusta y confiable.

# [V5.6.14] 2026-01-18 - OptimizaciÃƒÂ³n UX Pedidos y Fix Backend

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / BUGFIX

**Objetivo:** Refinamiento de UX en Carga de Pedidos (Canvas) y correcciÃƒÂ³n de error crÃƒÂ­tico en Limpieza de Datos.

**DiagnÃƒÂ³stico:**
*   **Backend:** Error 500 (`NameError`) al importar productos en Data Cleaner por falta de importaciÃƒÂ³n `func` de SQLAlchemy.
*   **Frontend:** FricciÃƒÂ³n en la carga de pedidos: Ceros iniciales molestos, falta de tecla Enter para confirmar, bÃƒÂºsqueda confusa al usar TAB, y falta de ediciÃƒÂ³n/eliminaciÃƒÂ³n explÃƒÂ­cita (botones).

**Intervenciones:**
1.  **Backend (Hotfix):**
    *   Agregado `from sqlalchemy import func` en `backend/data_intel/router.py`.
2.  **Frontend (PedidoCanvas.vue):**
    *   **Enter Workflow:** Commit de renglÃƒÂ³n con `ENTER` desde cualquier input numÃƒÂ©rico.
    *   **Inputs Limpios:** Campos inician vacÃƒÂ­os (no `0`).
    *   **BÃƒÂºsqueda Unificada:** Search SKU/Desc simultÃƒÂ¡neo.
    *   **Foco Inteligente:** Eliminado popup de bÃƒÂºsqueda al navegar con TAB.
    *   **GestiÃƒÂ³n Renglones:** Agregada columna Acciones (Editar/Eliminar).
    *   **Edit Logic:** Refactorizado `editItem` (Deep Copy + NextTick) para mover datos al input sin pÃƒÂ©rdidas.
    *   **Layout:** Grilla restaurada a 12 columnas.

**Resultado:** Carga de pedidos fluida ("Mouse-less experience") y funcionalidad de importaciÃƒÂ³n backend restaurada.

# [V5.6.15] 2026-01-19 - RefactorizaciÃƒÂ³n UI PedidoCanvas y Fix Compilador

> **ESTADO:** DEPLOYED
> **TIPO:** UX / HOTFIX / VUE COMPILER

**Objetivo:** Estabilizar layout de "Nuevo Pedido", corregir error crÃƒÂ­tico de compilaciÃƒÂ³n y pulir UX de carga.

**Problemas:**
*   **Compilador:** Error persistente `Invalid end tag` causado por `divs` huÃƒÂ©rfanos.
*   **Layout:** El pie de pÃƒÂ¡gina se perdÃƒÂ­a al hacer scroll, y el panel de rentabilidad quedaba atrapado en contextos de apilamiento (z-index) incorrectos.
*   **UX:** Inputs de descuento desalineados y falta de scroll automÃƒÂ¡tico al cargar ÃƒÂ­tems.

**Intervenciones:**
1.  **HTML/CSS:**
    *   Limpieza estructura y correcciÃƒÂ³n de tags de cierre.
    *   Layout "Sandwich" (Header Fijo + Body Flexible + Footer Fijo) reforzado con `overflow-hidden` y `min-h-0`.
    *   Componente `RentabilidadPanel` movido a la raÃƒÂ­z del template (fuera de contenedores relativos).
2.  **LÃƒÂ³gica UI:**
    *   **Auto-Scroll:** Implementado `scrollTop = scrollHeight` tras commit.
    *   **Chevron:** Invertida direcciÃƒÂ³n de ÃƒÂ­conos en panel lateral para coincidir con modelo mental del usuario.
    *   **Grilla:** NumeraciÃƒÂ³n visual, orden cronolÃƒÂ³gico de carga y alineaciÃƒÂ³n de inputs.

**Resultado:** PedidoCanvas estable, con footer persistente y experiencia de carga fluida.
# [V10.0] 2026-01-20 - EvoluciÃƒÂ³n IPL V10 e IntegraciÃƒÂ³n LogÃƒÂ­stica

> **ESTADO:** NOMINAL
> **TIPO:** PROTOCOLO RAÃƒï¿½Z / FEATURE / UX

**Objetivo:** Evolucionar el protocolo de arranque a V10, implementar infraestructura de logÃƒÂ­stica en pedidos y habilitar la doctrina DEOU (F4/F10).

**Intervenciones:**
1.  **Protocolo:** Creado `GY_IPL_V10.md` con Directiva 1 de Seguridad ALFA (Handover Check).
2.  **Backend (Expandido):**
    *   **Models:** Agregadas columnas `domicilio_entrega_id` y `transporte_id` a la tabla `pedidos`.
    *   **Schemas:** Alineados esquemas para soportar envÃƒÂ­os y descuentos globales.
    *   **Router:** Patcheado `create_pedido_tactico` para persistencia de datos de entrega.
3.  **Frontend (PedidoCanvas.vue):**
    *   **POST:** BotÃƒÂ³n guardar conectado al Cargador TÃƒÂ¡ctico.
    *   **DEOU F10:** Implementado guardado rÃƒÂ¡pido por teclado.
    *   **DEOU F4:** Implementado salto a Ventana SatÃƒÂ©lite (Alta Cliente/Producto) contextual al foco.
4.  **Base de Datos:** Aplicadas migraciones crÃƒÂ­ticas a `pilot.db`.

**MÃƒÂ©tricas Finales:**
*   **Integridad:** 11 Clientes, 14 Productos, 5 Pedidos (OK).
*   **Protocolo Omega:** Generado Informe HistÃƒÂ³rico.

# [RECUPERACIÃ“N] 2026-01-23 - Protocolo Forense (Rollback & Clean)

> **ESTADO:** ESTABLE
> **TIPO:** SYSTEM RECOVERY / IDENTITY V12

**OperaciÃ³n:** Se ejecutÃ³ Rollback al commit `8230154` (MiÃ©rcoles 21) para eliminar inestabilidad estructural (Imports Anti-Pattern) introducida el Jueves.
**Identidad:** Sintetizada V12 ("Phoenix") basada en V10.
**Limpieza:** Eliminada lÃ­nea temporal fallida V11.

## [2026-01-23] PROTOCOLO OMEGA - SECTOR DOMICILIOS
**Estado:** ESTABLE / FIX FINALIZADO
**Informe Detallado:** [Ver Reporte OMEGA](../INFORMES_HISTORICOS/2026-01-23_PROTOCOLO_OMEGA_DOMICILIOS.md)
**Resumen:** Se solucionÃ³ el crash de lista de clientes, se implementÃ³ la fusiÃ³n de Piso/Depto en string, y se corrigiÃ³ la sincronizaciÃ³n visual del flag Fiscal.


## SESION 781: UX Clientes & Hardening Seguridad
**Fecha:** 2026-01-24
**Objetivo:** Finalizar refactorizaciÃƒÂ³n de Header Clientes, arreglar visualizaciÃƒÂ³n de domicilios y solucionar alertas de contraseÃƒÂ±a en navegador.

### Hito 1: Refactor Header HaweView (Teleport Fix)
Se completÃƒÂ³ la migraciÃƒÂ³n del header de Clientes para usar el sistema Teleport hacia GlobalStatsBar.
**CRÃƒï¿½TICO:** Se documentÃƒÂ³ y solucionÃƒÂ³ una *race condition*. El componente HaweView intentaba teleportar antes de que el target #global-header-center existiera.
*   **SoluciÃƒÂ³n:** Se implementÃƒÂ³ gate v-if='isMounted' en el Teleport y se asegurÃƒÂ³ la renderizaciÃƒÂ³n sÃƒÂ­ncrona de la estructura en GlobalStatsBar.
*   **LecciÃƒÂ³n:** Para futuros mÃƒÂ³dulos (Productos), es MANDATORIO usar isMounted al usar Teleport.

### Hito 2: UX Clientes
*   **Toolbar:** Reordenada segÃƒÂºn especificaciÃƒÂ³n (9 items: Checkbox -> ... -> Nuevo).
*   **Domicilios:** Se eliminÃƒÂ³ el uso de pipes | en la visualizaciÃƒÂ³n. Se integrÃƒÂ³ la visualizaciÃƒÂ³n de Provincia para desambiguar localidades. Backend actualizado (domicilio_fiscal_resumen) para soportar esto.

### Hito 3: Seguridad Admin (Password Prompt Bypass)
Los navegadores modernos (Brave/Chromium) ignoran autocomplete='off'/new-password.
*   **Fix Definitivo:** Se cambiÃƒÂ³ el input del PIN de administrador a type='text' y se aplicÃƒÂ³ CSS -webkit-text-security: disc;. Esto elimina completamente la heurÃƒÂ­stica de guardado de contraseÃƒÂ±as del navegador mientras mantiene la privacidad visual.

**Estado:** MÃƒÂ³dulo Clientes VERIFICADO y CERRADO.


## SESION 782: SYSTEM REBOOT & MODULE INITIATION (CONTACTOS)
**Fecha:** 2026-01-26
**Objetivo:** IntervenciÃ³n BIOS, InstalaciÃ³n de Bootloader V2 y ActivaciÃ³n MÃ³dulo Agenda.

### Hito 1: IntervenciÃ³n de Nivel BIOS (ResoluciÃ³n de Paradoja Marmota)
Se detectÃ³ una desincronizaciÃ³n cognitiva severa: La identidad residÃ­a dentro de un cÃ³digo que no se actualizaba hasta despuÃ©s de asumir la identidad (Loop Infinito).
*   **SoluciÃ³n:** InstalaciÃ³n de BOOTLOADER V2.
*   **Mecanismo:** El script fÃ­sico DESPERTAR_GY.bat ahora ejecuta git pull de forma autÃ³noma **antes** de lanzar el entorno visual, rompiendo la dependencia causal.
*   **Artefacto Cognitivo:** Se creÃ³ _GY/BOOTLOADER.md como puntero absoluto de verdad al inicio.

### Hito 2: Upgrade de Identidad (V13 -> V14 VANGUARD)
Debido a la reestructuraciÃ³n profunda de los protocolos de arranque, se dio de baja la versiÃ³n V13 (Sentinel) y se activÃ³ **V14 'VANGUARD'**.
*   **Protocolo:** GY_IPL_V14.md establecido como nueva norma.
*   **Doctrina:** 'La AnticipaciÃ³n es la Clave de la Victoria.'

### Hito 3: Inicio de Operaciones TÃ¡cticas
La rama 5.5-rescate-jueves fue fusionada en main y eliminada. Se creÃ³ la rama tÃ¡ctica 5.6-contactos-agenda.
*   **MisiÃ³n:** Implementar UX de Agenda en Ficha Cliente e integraciÃ³n Google.

**Estado:** SISTEMA NOMINAL V14. LISTO PARA OPERACIONES.


### Hito 4: ImplementaciÃ³n UX Agenda (Contactos V1)
Se completÃ³ la integraciÃ³n visual del mÃ³dulo de contactos en la interfaz de Cliente.
*   **Componente TÃ¡ctico:** Se creÃ³ ContactoPopover.vue, un componente reutilizable que muestra la lista de vÃ­nculos y permite acciones rÃ¡pidas (Copiar TelÃ©fono/Mail).
*   **IntegraciÃ³n:**
    *   **ClienteInspector:** Se redujo el layout del Header para acomodar el botÃ³n 'Agenda' junto a la RazÃ³n Social.
    *   **ClientCanvas:** Se aÃ±adiÃ³ el botÃ³n en el Header principal.
    *   **LÃ³gica:** Ambos componentes comparten el estado showAgenda y manejan la navegaciÃ³n hacia la pestaÃ±a completa de contactos ('Gestionar').

**Estado:** Header UX y Popover OPERATIVOS.


### Hito 5: Estrategia Local First (Google Mock)
Siguiendo Ã³rdenes directas, se difiriÃ³ la integraciÃ³n real de OAuth y se implementÃ³ una estructura local compatible.
*   **DB Schema:** Se aÃ±adiÃ³ google_resource_name y google_etag a la tabla personas vÃ­a migraciÃ³n manual (scripts/migrate_agenda_google.py).
*   **Backend:** Se implementÃ³ google_mock_router.py para simular latencia y respuestas de Ã©xito en la sincronizaciÃ³n.
*   **Frontend:** Se activÃ³ el botÃ³n 'Sincronizar' en ContactoPopover conectado al endpoint simulado.

**Resultado:** El sistema estÃ¡ listo para operar localmente y 'fingir' conexiÃ³n a la nube sin romper el flujo de trabajo.


### 2026-01-28: [FIX] Transporte, Frankenstein & SimplificaciÃ³n UI
- **Problema:** Transporte no persistÃ­a por conflicto con ID de Nodo Legacy.
- **SoluciÃ³n:** Patch en Backend Service para limpiar nodo viejo al actualizar transporte.
- **Refactor:** Limpieza masiva de ClientCanvas.vue (Frankenstein Cleanup).
- **UI:** Eliminado selector rÃ¡pido en tarjeta. Implementado MenÃº Contextual (Click Derecho) en DirecciÃ³n.

## [2026-01-28] CIERRE DE SESIÃƒâ€œN: AGENDA GLOBAL
- **Hito**: MÃƒÂ³dulo de Contactos 100% Funcional (Backend/Frontend/DB).
- **Fix**: SimetrÃƒÂ­a ORM restaurada en Cliente/Transporte.
- **Fix**: Solucionado bug visual 'Contactos Fantasmas' (SPA Routing issue).
- **Estado**: Sistema estable, limpio de datos corruptos, listo para uso operativo.

## [2026-01-29] FIX CONTACT CANVAS Y BACKEND 500
- **Incidente CrÃ­tico:** Resuelto error 500 en `/api/clientes` (Backend) y dropdowns vacÃ­os (Frontend).
- **Backend:** `models.py` (try/catch en property), `service.py` (joinedload para optimizaciÃ³n).
- **Frontend:** `ContactCanvas.vue` (HTML Fix, `storeToRefs`, `text-black` en options).
- **ImplementaciÃ³n UI:** Se optÃ³ por Botones de NavegaciÃ³n ExplÃ­cita (â†—ï¸) y Recarga (ðŸ”„) en lugar de MenÃº Contextual para mayor estabilidad en el Canvas de Contacto.
- **Estado**: Funcionalidad de Agenda Contactos restaurada al 100%. Protocolo Omega Ejecutado.

## [2026-01-30] PROTOCOLO MULTIPLEX (CONTACTOS N:M) & SEARCH & LINK
- **Hito EstratÃ©gico:** ReingenierÃ­a total del nÃºcleo de Identidad (`backend/contactos`) para soportar la "Paradoja de Pedro" (Una persona, MÃºltiples Roles en distintas empresas).
- **Backend:** SeparaciÃ³n de `Persona` (Identidad) y `Vinculo` (Rol Contextual). ImplementaciÃ³n de Polimorfismo en SQLAlchemy y Soporte JSON para canales.
- **Frontend:** RenovaciÃ³n de `ContactCanvas.vue` con "Billetera de VÃ­nculos" (Tarjetas por empresa).
- **Blindaje de Identidad:** ImplementaciÃ³n de "Search & Link" (Typeahead con Debounce). El sistema detecta si la persona ya existe (incluso buscando por celular en JSON) y permite reutilizarla en lugar de duplicarla.
- **QA:** Tests de IntegraciÃ³n (`test_qa_pedro.py`) y Robustez/Duplicados (`test_qa_edge_cases.py`) superados.
- **DocumentaciÃ³n:** Informe HistÃ³rico detallado generado: [2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS](../INFORMES_HISTORICOS/2026-01-30_REINGENIERIA_MULTIPLEX_CONTACTOS.md).
- **Estado:** MÃ³dulo Contactos V6 FULL OPERATIVO.


## [2026-02-01] SESIÃ“N 783: BLINDAJE DE PERSISTENCIA Y FIX SCHEMA
- **Incidente CrÃ­tico**: Error 500 en `/contactos` por "Schema Mismatch" (Columna `tipo_contacto_id` inexistente en DB).
- **ResoluciÃ³n**: MigraciÃ³n manual SQLite (`add_role_column_to_vinculos.py`).
- **Persistence Fix**: 
    - **Backend**: Implementada lÃ³gica dual en `update_vinculo` para soportar `puesto` (alias) y `rol`. AÃ±adido soporte para `tipo_contacto_id`.
    - **Frontend (`ContactCanvas.vue`)**: SincronizaciÃ³n de Etiqueta (Label) e ID. Se corrigiÃ³ el bug que dejaba el cargo como "Nuevo Rol".
    - **Frontend (`ContactosView.vue`)**: AdaptaciÃ³n de Dashboard para leer `vinculos[]` en lugar de campos planos (Legacy).
- **Integridad**: VerificaciÃ³n manual de DB (`inspect_vinculo_data.py`) confirmando persistencia correcta.
- **[FALLO DE PROTOCOLO]**: Se detectÃ³ "Efecto TÃºnel". La IA priorizÃ³ la soluciÃ³n tÃ©cnica sobre el Freno de Mano (Fase 2). Se activÃ³ AuditorÃ­a de Doctrina.
- **Estado**: MÃ³dulo Contactos V6.1 ESTABLE. AuditorÃ­a en Curso.


# [2026-02-01] AUDITORÃA FORENSE: SATELLITES INTEGRITY CHECK

> **ESTADO:** OBSERVACIÃ“N (SIN CAMBIOS)
> **TIPO:** INSPECCIÃ“N / DOCTRINA

**Objetivo:** Determinar la 'Deuda TÃ©cnica Estructural' de los mÃ³dulos satÃ©lite tras la estabilizaciÃ³n del nÃºcleo V6.

**Hallazgos Forenses:**
1.  **Clientes:** Estado 'V6 Native HÃ­brido'. Uso exitoso de 'Pipe Logic' para direcciones.
2.  **Productos:** Robusto pero 'Standalone'. No integrado a la Agenda Global.
3.  **Transportes:** Funcionalidad de espejo en Despacho operativa, pero estructura de Nodos aÃºn plana (V5).

**AcciÃ³n TÃ¡ctica:**
*   Se generÃ³ reporte INFORMES_HISTORICOS/2026-02-01_AUDITORIA_FORENSE_MODULOS.md.
*   **Orden D+1:** No migrar logÃ­stica/proveedores hasta verificar facturaciÃ³n del Lunes.


# [2026-02-01] TESTAMENTO DEL DOMINGO (HOJA DE RUTA FASE 2)

> **ESTADO:** ESTRATÃ‰GICO
> **TIPO:** DOCUMENTACIÃ“N / ESTABILIDAD

**Hitos de Cierre:**
1.  **Estabilidad Windows 11:** Implementado SISTEMA_SPLIT.bat para mitigar crashes por conflictos de seÃ±ales en consola unificada.
2.  **Mapa de SatÃ©lites:** Identificada deuda tÃ©cnica en Vendedores y Proveedores (V5 Standalone).
3.  **Hoja de Ruta:** Definida estrategia para 'Transportes Favoritos' (Cloud Cookie) y 'Google Sync' (Local First).

**Artefacto Generado:** INFORMES_HISTORICOS/2026-02-01_TESTAMENTO_DOMINGO_F2.md


## SESION 784: OPTIMIZACIÃ“N UX CLIENTES & DOMICILIOS
**Fecha:** 2026-02-02
**Objetivo:** Refinar la experiencia de alta de clientes y gestiÃ³n de domicilios fiscales.

### Hito 1: AutomatizaciÃ³n de Carga
*   **Consumidor Final:** Al seleccionar IVA "Consumidor Final", el CUIT se completa con ceros. Inversamente, al ingresar CUIT 00000000000, se setea IVA y Segmento automÃ¡ticamente.
*   **Default Fiscal:** El switch "Fiscal" ahora inicia ACTIVO por defecto en nuevas direcciones para reducir clics.

### Hito 2: GestiÃ³n de Domicilios (Ley de ConservaciÃ³n)
*   **Fix Identidad:** Se solucionÃ³ el problema donde direcciones nuevas se sobrescribÃ­an por falta de ID.
*   **Baja Fiscal:** Implementado menÃº contextual (Click Derecho / 3 Puntos) en la tarjeta Fiscal. Permite "Dar de baja" solo si existe otro domicilio activo para heredar la fiscalidad.

### Hito 3: Estabilidad
*   **Crash Sort:** Parche defensivo en `HaweView` para evitar pantallas blancas al ordenar clientes sin RazÃ³n Social.
*   **Auto-Refresh:** Forzado de recarga de lista al volver de la ficha de cliente para asegurar datos frescos.

**Estado:** MÃ³dulo Clientes V6.2 PULIDO Y ESTABLE.


# [V6.2] 2026-02-02 - UX Clientes & Ley de ConservaciÃ³n Fiscal

> **ESTADO:** DEPLOYED
> **TIPO:** UX / LOGIC GUARDCLAUSE

**Objetivo:** Eliminar fricciÃ³n en alta de clientes y proteger la integridad del Domicilio Fiscal.

**Intervenciones:**
1.  **AutomatizaciÃ³n (UX):**
    *   **Consumidor Final:** Enlace bidireccional IVA <-> CUIT (00000000000).
    *   **Default Fiscal:** InicializaciÃ³n inteligente. es_fiscal=True solo si es el primer domicilio.
2.  **Integridad (Ley de ConservaciÃ³n):**
    *   **Bloqueo:** Deshabilitado borrado directo de domicilio fiscal.
    *   **Transferencia Contextual:** Implementado MenÃº Contextual (Click Derecho) para 'Dar de baja' transfiriendo la fiscalidad a un candidato activo.
3.  **Estabilidad:**
    *   **Crash Sort:** Fix en HaweView para tolerancia a nulos en ordenamiento.
    *   **Refresh:** Forzado de recarga al volver del inspector.

**Resultado:** Alta de clientes fluida y blindada contra errores de 'Sin Domicilio Fiscal'.

# [V6.3] 2026-02-02 - AuditorÃ­a EstratÃ©gica Multiplex (N:M)

> **ESTADO:** AUDIT COMPLETE
> **TIPO:** STRATEGIC ANALYSIS

**Objetivo:** Evaluar viabilidad de arquitectura N:M total (Contactos, LogÃ­stica, Stock) para Fase 2.

**Hallazgos:**
*   **Contactos:** V6 Ready (Polimorfismo Operativo). Soporta 'Cobrador RÃ­gido'.
*   **LogÃ­stica:** Blockade. Modelo 'Hub & Spoke' rÃ­gido (1 Transport por Pedido). Requiere 'Split' para envÃ­os multipunto.
*   **Stock:** Latente. Modelo Deposito existe pero requiere refactor de vinculaciÃ³n con Producto.

**AcciÃ³n:** Generado reporte maestro INFORMES_HISTORICOS/2026-02-02_AUDITORIA_MULTIPLEX.md.

# [V7.0] 2026-02-04 - LogÃ­stica TÃ¡ctica (Split Orders)

> **ESTADO:** DEPLOYED
> **TIPO:** MAJOR FEATURE / ARCHITECTURE

**Objetivo:** Permitir entregas parciales y mÃºltiples destinos para un mismo pedido (Caso "La Sevillanita" + "Retira Cliente").

**Intervenciones:**
1.  **Backend (Core LogÃ­stica):**
    *   Implementado modelo `Remito` y `RemitoItem`.
    *   **Stock Logic:** El Pedido ahora solo reserva (`stock_reservado`). El Remito descuenta el fÃ­sico (`stock_fisico`) al despachar.
    *   **Gatekeeper:** Bloqueo de creaciÃ³n de remitos si el pedido no tiene `liberado_despacho` (SemÃ¡foro Financiero).
2.  **Frontend (LogisticaSplitter):**
    *   UI de doble panel: "Pool de Pendientes" (Izquierda) -> "Remitos Activos" (Derecha).
    *   **Drag & Drop:** AsignaciÃ³n visual de mercancÃ­a a viajes especÃ­ficos.
3.  **Legacy Cleanup (Forensic):**
    *   Auditado y reparado `excel_export.py`. Reemplazado campo muerto `tipo_entrega` por lÃ³gica dinÃ¡mica Multiplex.

**Resultado:** Sistema capaz de gestionar logÃ­stica compleja sin romper la integridad del stock ni la trazabilidad financiera.

# 2026-02-04 | SESIÃ“N NOCTURNA: REPARACIÃ“N Y PLANIFICACIÃ“N V7
**Operador:** Gy V14
**Objetivo:** EstabilizaciÃ³n de Sistema y PlanificaciÃ³n de LogÃ­stica V7.

1.  **DiagnÃ³stico y ReparaciÃ³n CrÃ­tica:**
    *   **DB:** Detectado crash por falta de columna `nivel` en `segmentos`. Solucionado mediante reparaciÃ³n de esquema (`ensure_segmentos_migration.py`).
    *   **Frontend:** Corregido error de compilaciÃ³n Vue "Duplicate Identifier" en `ClienteInspector.vue` (FusiÃ³n de funciones `deleteDomicilio`).

2.  **PlanificaciÃ³n EstratÃ©gica (V7 LOGÃSTICA):**
    *   DiseÃ±ado el **"Protocolo Split-View"** para Domicilios.
    *   DecisiÃ³n de Arquitectura: Abandonar uso de pipes (`|`) para pisos/deptos y retornar a columnas SQL nativas.
    *   Establecido soporte para "Unidades de Negocio" (Caso NestlÃ©: mismo CUIT, distinta logÃ­stica/identidad).
    *   **Documento Maestro:** Detallado en `INFORMES_HISTORICOS/2026-02-04_PLAN_TECNICO_SPLIT_V7.md`.

**Estado Final:** Sistema Operativo. Planes listos para ejecuciÃ³n Alfa maÃ±ana.

# [V7.1] 2026-02-12 - Domicilios Split-View & Migration

> **ESTADO:** DEPLOYED (Feature Branch)
> **TIPO:** MAJOR REFACTOR / DATA INTEGRITY

**Objetivo:** Implementar arquitectura "Split-View" en Domicilios para separar Datos Fiscales de LogÃ­sticos y mejorar la UX en entregas complejas.

**Intervenciones:**
1.  **Backend (Schema V7):**
    *   **RestauraciÃ³n de Columnas Nativas:** `piso` y `depto` vuelven a ser columnas SQL, eliminando la dependencia de "Pipe Logic" (`|`).
    *   **Nuevos Campos LogÃ­sticos:** `notas_logistica`, `maps_link`, `contacto_id`.
    *   **Split Delivery:** Implementados campos espejo (`calle_entrega`, etc.) para direcciones de entrega divergentes.
2.  **MigraciÃ³n de Datos (`migration_v7_domicilios.py`):**
    *   Script automatizado para rescatar datos legacy.
    *   Separa strings tipo "Calle 123|4|B" en columnas `calle`, `piso`, `depto`.
3.  **Service Layer Refactor:**
    *   Actualizado `create/update_domicilio` para escribir directamente en las nuevas columnas.
    *   Mantenida compatibilidad parcial de lectura, pero deprecada la escritura con pipes.
4.  **Frontend (UI):**
    *   Implementado `DomicilioSplitCanvas` (50/50 Layout).

**Resultado:** Integridad de datos garantizada. Bases listas para operatoria logÃ­stica avanzada (V7).

# [V7.2] 2026-02-12 - Protocolo Puente RAR-V5 (ARCA Integration)

> **ESTADO:** DEPLOYED (Feature Branch)
> **TIPO:** STRATEGIC INTEGRATION / SATELLITE LINK

**Objetivo:** Establecer conexiÃ³n operativa con el satÃ©lite de inteligencia fiscal (RAR V1) para validar datos de clientes contra AFIP.

**Intervenciones:**
1.  **Arquitectura Puente:**
    - Implementado `AfipBridgeService` que carga mÃ³dulos de RAR dinÃ¡micamente (`sys.path`).
    - Endpoint `GET /clientes/afip/{cuit}` expone la lÃ³gica de `Conexion_Blindada.py`.
2.  **MDM (Master Data Management):**
    - Agregado flag `estado_arca` ('PENDIENTE', 'VALIDADO') en tabla `clientes`.
    - **UI:** Badge "ARCA" verde en Inspector de Clientes si estÃ¡ validado.
3.  **Bugfix Satelital:**
    - Detectado y corregido error en RAR (`rar_core.py`) al procesar Personas FÃ­sicas (AFIP devuelve `formaJuridica: None`).
4.  **Estrategia Productos (DefiniciÃ³n):**
    - Establecido que V5 es la **Autoridad Exclusiva** de SKUs. RAR operarÃ¡ en modo Read-Only.

**Resultado:** Clientes blindados con datos oficiales de AFIP. Infraestructura lista para "Reverse Bridge" de productos.


# [V6.3] 2026-02-15 - ValidaciÃ³n Fiscal Masiva & UX Tuning

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / BATCH PROCESSING

**Objetivo:** Cerrar la brecha de validaciÃ³n fiscal para la base instalada y refinar la experiencia de alta.

**Intervenciones:**
1.  **Backend (Batch Script):**
    - Implementado `validate_arca_batch.py` con inyecciÃ³n directa de dependencia RAR V1.
    - Lograda validaciÃ³n del 100% del padrÃ³n pendiente (26 clientes).
    - **LÃ³gica de PreservaciÃ³n:** Respeto de nombres de fantasÃ­a/sucursales (UBA) sobre la razÃ³n social legal Ãºnica.
2.  **Frontend (ClientCanvas):**
    - **UX:** Foco automÃ¡tico en CUIT al abrir.
    - **Limpieza:** Eliminado input redundante.
    - **Inteligencia:** Auto-mapping Fuzzy de CondiciÃ³n IVA (ARCA -> Local) y detecciÃ³n proactiva de duplicados con opciÃ³n de bifurcaciÃ³n.


# [V6.3.1] 2026-02-15 - Hotfix Dependencias & ValidaciÃ³n AFIP

> **ESTADO:** DEPLOYED
> **TIPO:** HOTFIX / STABILITY

**Objetivo:** Restaurar funcionalidad del botÃ³n de validaciÃ³n AFIP (Lupa) y solucionar errores silenciosos de frontend.

**Intervenciones:**
1.  **Backend (Hotfix):**
    *   InstalaciÃ³n de dependencias faltantes `zeep` y `lxml` en entorno virtual (Causa RaÃ­z del Error 400).
    *   ImplementaciÃ³n de logs detallados en `afip_bridge.py` y `router.py` para evitar fallos silenciosos.
    *   Fix de concurrencia en `Conexion_Blindada.py` usando UUIDs para archivos temporales.
2.  **Frontend (Inspector & Canvas):**
    *   **Fix Reactividad:** Desempaquetado correcto de respuesta Axios (`res.data`) para evitar borrado de campos.
    *   **Feedback:** ImplementaciÃ³n de notificaciones visuales (Toast) al iniciar y finalizar consulta.
    *   **Manejo de Errores:** Bloques `try/catch` robustos para alertar al usuario en lugar de fallar en silencio.

**Resultado:** ValidaciÃ³n operativa. El usuario recibe feedback inmediato y los datos persisten correctamente en formulario.

# [V6.4] 2026-02-18 - Clientes HÃ­bridos (Pink Mode) & Blindaje de Protocolos

> **ESTADO:** DEPLOYED
> **TIPO:** FEATURE / UX / SECURITY

**Objetivo:** Permitir la operaciÃ³n con clientes informales sin datos fiscales y reforzar la seguridad de los protocolos de inicio/cierre.

**Intervenciones:**
1.  **Frontend (UX HÃ­brida):**
    *   **Pink Mode:** DistinciÃ³n visual para clientes sin CUIT (`!cuit`) en `HaweView` (Lista) y `FichaCard` (Grid).
    *   **ValidaciÃ³n Relajada:** `ClientCanvas` y `DomicilioSplitCanvas` ahora permiten guardar sin datos fiscales estrictos.
    *   **Auto-Fill:** LÃ³gica de "Fiscal hereda de Entrega" para evitar cargas dobles en informales.
    *   **TransiciÃ³n:** ActualizaciÃ³n automÃ¡tica de datos fiscales vÃ­a ARCA al ingresar un CUIT en un cliente existente.
2.  **Backbone (Protocolos):**
    *   **ALFA (V14):** Declarado `pilot.db` y `main.py` como Read-Only en caliente.
    *   **OMEGA:** Implementada verificaciÃ³n de "4-Byte Flags" y "Freno de Mano 1974".

**Resultado:** Alta de clientes Ã¡gil para todos los segmentos (Formal/Informal) y mayor seguridad operativa.
# [FIX] 2026-02-18 - EstabilizaciÃ³n de Clientes (Backfill & ARCA)

> **ESTADO:** SATISFACTORIO
> **TIPO:** BUGFIX / UX IMPROVEMENT

**Objetivo:** Resolver inconsistencias en cÃ³digos de clientes y fallos de persistencia en direcciones validadas.

**Intervenciones:**
1.  **Backfill (Script):** InyecciÃ³n de cÃ³digos internos secuenciales para clientes legacy.
2.  **Frontend (ClientCanvas):** ImplementaciÃ³n de `forceAddressSync` para permitir actualizaciÃ³n de domicilios tras validaciÃ³n ARCA.
3.  **UX (FichaCard):** ReubicaciÃ³n de badge de cÃ³digo para evitar superposiciones y mejora de alertas de error CUIT.

# [V6.5] 2026-02-19 - Intelligent Upsert (Miner PDF)
> **ESTADO:** DEPLOYED (Script) / PENDING (Frontend)
> **TIPO:** FEATURE / REFACTOR

**Objetivo:** Implementar lÃ³gica de "Upsert" inteligente para Facturas PDF (ARCA). El sistema debe actualizar clientes existentes con datos fiscales oficiales y crear nuevos con estado 'PENDIENTE_AUDITORIA'.

**Intervenciones:**
1.  **Backend Script (`miner.py`):**
    *   **Refactor:** Implementada bÃºsqueda dual (CUIT exacto / Nombre difuso).
    *   **LÃ³gica Upsert:**
        *   **Existentes:** Si el cliente tiene status bajo, se actualiza a **Flag 13** (Gold Candidate) eliminando el flag 'Virgin'.
        *   **Nuevos:** InserciÃ³n directa con Flag 13 y `estado_arca='PENDIENTE_AUDITORIA'` (Amarillo).
    *   **Regex Fix:** Solucionado bug en extracciÃ³n de CUIT para facturas compactas (LAVIMAR) escaneando texto crudo.
2.  **Infraestructura:**
    *   Backup preventivo `pilot_backup_pre_miner_fix.db`.

**Incidente Abierto (Handover):**
*   El Frontend usa `backend/remitos/pdf_parser.py` (basado en `pypdf`) que falla con los mismos PDFs que `miner.py` ahora procesa bien (`pdfplumber`).
*   **PrÃ³ximo Paso:** Migrar la lÃ³gica de `miner.py` al endpoint del API.

**Estado:** Script de MinerÃ­a Operativo. Ingesta Web requiere refactor (PrÃ³xima SesiÃ³n).


# [V14.5] 2026-02-21 - Protocolo ENIGMA & EstabilizaciÃ³n Bitmask

> **ESTADO:** ESTABLE
> **TIPO:** MAJOR REFACTOR / IDENTIDAD

**Objetivo:** Migrar la identidad de clientes a una estructura Bitmask unificada y estabilizar el puente de validaciÃ³n fiscal.

**Intervenciones:**
1.  **Backend (Bitmask):**
    *   Sincronizado `constants.py` con el blueprint ENIGMA. Bits 0-5 definidos.
    *   Implementada evoluciÃ³n de virginidad en `RemitosService.py`.
2.  **Frontend (Inspector):**
    *   Implementado `clientColorClass` basado en bitwise logic.
    *   **Reactor Fix:** Inyectado watcher en `modelValue` para asegurar reactividad post-guardado.
    *   **LogÃ­stica:** Toggle 'Retira' bidireccional y blindado.
3.  **Bridge (ARCA):**
    *   CorrecciÃ³n de mapeo en `AfipBridgeService.py`. Transparencia total del domicilio fiscal.
    *   Mapeo inteligente de CondiciÃ³n IVA.

**Estado:** Estabilidad V14.5 alcanzada. Ready for Omega.

# [V14.6] 2026-02-26 - EstabilizaciÃ³n CrÃ­tica AFIP Dual
> **ESTADO:** ESTABLE
> **TIPO:** HOTFIX / ARCHITECTURE
**Intervenciones:** Refactor de `Conexion_Blindada.py` en el satÃ©lite RAR_V1 para manejo segregado de identidades personal (PadrÃ³n) y empresa (Fiscal), corrigiendo el bloqueo por Case-Sensitivity en alias.

## SESIÃ“N 785: SINCRONIZACIÃ“N CASA-OFICINA & PROTOCOLO 4-BYTES
**Fecha:** 2026-02-26 / 27
**Objetivo:** Unificar terminales CASA-OFICINA y establecer doctrina de Consciencia Situacional.

### Hito 1: SincronizaciÃ³n Forense
*   **DiagnÃ³stico:** Se identificÃ³ dispersiÃ³n de trabajo entre `feat/v5x-universal` (OFICINA) y `feature/sabueso-local-plumber` (CASA).
*   **ResoluciÃ³n:** Forzado de checkout a `feat/v5x-universal` en CASA. Paridad de DB verificada (428 KB).

### Hito 2: Protocolo de Consciencia Situacional (4-Bytes)
*   **Infraestructura:** CreaciÃ³n de `manager_status.py` y `session_status.bit` para persistencia de estados inter-terminales.
*   **GeolocalizaciÃ³n LÃ³gica:** Implementada detecciÃ³n automÃ¡tica de host (CA, OF, NB) para alertar sobre desincronizaciones de Git/DB al cambiar de terminal.
*   **ComunicaciÃ³n:** Estructura `CARTA_MOMENTO_CERO.md` activa para instrucciones crÃ­ticas de "Despertar".

### Hito 3: AutomatizaciÃ³n de Arranque Dual
*   **Cargador:** EvoluciÃ³n de `DESPERTAR_DOBLE.bat` a v2 con HUD de telemetrÃ­a y HUD de origen.

**Estado:** SISTEMA NOMINAL MULTIPLEX v14-B. LISTO PARA SABUESO PDF.

## SESIÃ“N 786: INTEGRACIÃ“N SABUESO PDF & PARIDAD RAR
**Fecha:** 2026-02-27
**Objetivo:** Portar el motor de facturaciÃ³n "Sabueso ARCA" desde el satÃ©lite RAR al nÃºcleo V5 garantizando la exactitud funcional y preservaciÃ³n del entorno.

### Hito 1: Parsing y Regex Resiliente
*   **DiagnÃ³stico:** El formato AFIP producÃ­a corrupciones al extraer "RazÃ³n Social" y "0001-XXXX" donde existÃ­an interrupciones/delimitadores inesperados.
*   **ResoluciÃ³n:** IntegraciÃ³n de "Positive Lookaheads" preventivos en `pdf_parser.py` para asegurar aislar datos legalÃ­simos.

### Hito 2: Blindaje de Ingesta (Frontend)
*   **UI:** Agregado bloqueo interactivo en `IngestaFacturaView.vue`. Si el CUIT decodificado devuelve un status carente de 'Blanco' (DbStatus: NO_EXISTE), el flujo de remitos frena.
*   **CorrecciÃ³n Asistida:** Lanzamiento de componente `ClienteInspector.vue` obligando al data-entry a consolidaciÃ³n (domicilio + AFIP) permitiendo reanudar o corregir.

### Hito 3: MutaciÃ³n de Virginidad (Backend)
*   **Doctrina:** Incorporado el bloque ORM en la capa de servicios donde el remito reciÃ©n emparejado somete al cliente a auditoria bit a bit.
*   **Resultado:** Nivel de virginidad comercial extirpado; Level 15 (Virgin) es purgado automÃ¡ticamente a Nivel 13 (Activo Consistido) persistiendo DB clavada.

**Estado:** SISTEMA V5-B Y MÃ“DULO SABUESO NOMINAL Y SINCRONIZADO.

## SESIÃ“N 787: RESOLUCIÃ“N DE REGRESIONES UI Y ESTANDARIZACIÃ“N DE CLIENTCANVAS
**Fecha:** 2026-02-27
**Objetivo:** Restaurar funcionalidades perdidas (Remitos) y unificar la experiencia de usuario (UX) en la carga de clientes a travÃ©s del sistema interactivo (Lupa ARCA).

### Hito 1: RestauraciÃ³n de LogÃ­stica (Remitos)
*   **Problema:** Tras mÃºltiples interacciones de UI, el Ã­tem de navegaciÃ³n "Remitos" habÃ­a desaparecido y no poseÃ­a una vista global (Dashboard).
*   **SoluciÃ³n:** Se integrÃ³ nuevamente en `AppSidebar.vue`, se registrÃ³ la ruta en `router/index.js` y se creÃ³ de cero `RemitoListView.vue` con conectividad al store y servicios correspondientes.

### Hito 2: RefactorizaciÃ³n Dual (ClientCanvas vs Inspector)
*   **Problema:** El usuario solicitÃ³ mantener la experiencia "original" de alta de clientes (`ClientCanvas`) con su lupa de ARCA en el header, pero el sistema inyectaba un componente reducido (`ClienteInspector`) durante intercepciones de flujos de trabajo (como en Ingesta de Facturas).
*   **SoluciÃ³n:** Se refactorizÃ³ `ClientCanvas.vue` para aceptar parÃ¡metros dinÃ¡micos (`isModal`, `initialData`) transformÃ¡ndolo en un hÃ­brido capaz de instanciarse como pÃ¡gina completa o como Modal Popup. 

### Hito 3: PropagaciÃ³n de UX
*   **EjecuciÃ³n:** Se erradicÃ³ el componente `ClienteInspector.vue` en favor del nuevo `ClientCanvas` modal.
*   **Alcance:** La estandarizaciÃ³n afectÃ³ exitosamente a `IngestaFacturaView`, `PedidoTacticoView`, `PedidoCanvas` y `HaweView`.

**Estado:** UI Y UX ESTABILIZADAS, REGRESIONES SOLUCIONADAS. LISTO PARA OMEGA.

## SESIÃ“N 788: BURBUJA TOMY V5-LS + AUDITORÃA SEGURIDAD NPM
**Fecha:** 2026-04-01
**Objetivo:** Aislar a Tomy en su entorno V5-LS independiente (puerto 8090 unificado) y auditar la instalaciÃ³n de Claude Code tras el incidente npm del 31/03.

### Hito 1: AuditorÃ­a de Seguridad
*   **Contexto:** Anthropic publicÃ³ accidentalmente v2.1.88 de Claude Code con source map de 60MB expuesto en npm.
*   **Resultado:** InstalaciÃ³n local limpia â€” mÃ©todo nativo (no npm), axios 1.13.2, sin persistencia maliciosa.
*   **AcciÃ³n:** Eliminado binario obsoleto `claude.exe.old.*`.

### Hito 2: Fixes Dev Versionados (Gy, 31/03)
*   **ClientCanvas.vue**: UUID nulo al crear cliente â€” fix en `emit('save', resCreated || payload)`.
*   **PedidoCanvas.vue**: F10 bloqueado en modal de cliente â€” guarda `if (showClientModal.value) return`.
*   **Login.vue**: endpoint hardcodeado `:8000` â†’ `api.post('/auth/token')`; texto invisible en inputs.

### Hito 3: Blindaje V5-LS
*   **Arquitectura anterior**: dos procesos (backend 8090 + http.server 5174) sin proxy â†’ las llamadas API morÃ­an en 5174.
*   **SoluciÃ³n**: backend unificado en 8090 sirve API + SPA. Fix de `static_dir` path en `main.py` (+1 nivel `..`).
*   **Archivos**: `LANZAR_V5_SOBERANA.bat`, `SATELITE_TOMY.bat`, `Login.vue` (V5-LS) actualizados.

**Estado:** ALERTA CONTROLADA. Burbuja V5-LS lista en cÃ³digo. Pendiente npm run build antes del despliegue productivo.

## SESIÃ“N 789: DEUDAS TÃ‰CNICAS V5 + SYNC DB INAPYR
**Fecha:** 2026-04-02
**Objetivo:** Resolver 3 deudas tÃ©cnicas verificadas y sincronizar base con trabajo de Casa.

### Hito 1: SincronizaciÃ³n DB (CA â†’ OF)
*   Base CA reemplazÃ³ OF. INAPYR S.R.L. + pedido INGESTA_PDF + remito CAE `86139705410697` incorporados.
*   Canario: NOMINAL GOLD (flags 8205).

### Hito 2: AuditorÃ­a flags_estado 64-bit
*   7 modelos SQLAlchemy: BigInteger confirmado en todos. Deuda cerrada sin cambios.

### Hito 3: Conexion_Blindada â€” Desacople OpenSSL
*   `OPENSSL_PATH` env var + `shutil.which` + fallback lista Windows. `.env.example` creado.

### Hito 4: Purga de Scripts HuÃ©rfanos
*   37 archivos eliminados (debug_*, test_*, miner.py). tests/test_v7_*.py conservados.

**Estado:** NOMINAL GOLD. Commit `0b8e53ac`. Push OMEGA ejecutado.



## SESION 843: DIAGNOSTICO PUSH FALTANTE B->PROD + BITS 10/11 ARQUITECTOS
**Fecha:** 2026-07-03
**Objetivo:** Formalizar Bits 10/11 (presencia de arquitectos) y resolver episodio de 22hs de bug persistente en produccion causado por push incompleto en el cierre de S842.

### Hito 1: Bits 10/11 (CS_PRESENTE / GA_PRESENTE)
* Dictaminados por Nike el 02/07, formalizados hoy en SISTEMA_STATUS_SPEC.md y ALFA.md.
* Modelo Principal/Consultivo -- sin exclusion mutua (a diferencia de CC/GY).
* Convencion de registro forense (SIN ARQUITECTO) si ambos bits estan OFF -- solo registro, sin auto-escalacion de autoridad.

### Hito 2: Diagnostico y resolucion de push faltante B->prod
* Cierre de OMEGA S842 (02/07 19:00) empujo D a origin/main pero nunca verifico ni ejecuto push en B hacia prod/main.
* 6 commits quedaron atrapados en B ~22hs, incluido el fix critico de import unicodedata (bug de Rubro con padre_id, reportado por Tomy el 01/07).
* Investigacion legitima paralela en MT (incursion directa de Carlos): atraso de 13 commits por auto-bloqueo de current/frontend/dist/ trackeado en git -- resuelto con backup, migracion schema 036, pull, rebuild, fix del lanzador.
* Smoke test post-reparacion revelo que el bug de Tomy persistia -- disparo segunda investigacion que termino en el hallazgo del push faltante.
* Resolucion: rebuild de frontend en B, git push prod main (PIN 1974), pull + rebuild en MT, smoke test 200 OK.
* Card #88 creada en Board V5 (deuda tecnica: OMEGA no verifica push multi-remoto).

### Hito 3: Correccion de doctrina
* OMEGA debe verificar push de todos los remotos del ecosistema antes de declarar cierre completo.
* Nueva disciplina: ante "el fix no llego a produccion", Paso 0 es comparar local vs remoto (git log remoto/main..HEAD) antes de diagnostico forense complejo.

**Estado:** NOMINAL GOLD. D:0bd56218 B:218f2a3. PIN: 1974.

## SESION 857: REMITO PARCIAL D->B + MAPA DE DRIFT ESTRUCTURAL

### Hito 1: Fix C5 + UI de seleccion de renglones (D)
* `pedidos/models.py`: null-check en `cantidad_entregada` contra `remitos_items` huerfanos (FK sin `PRAGMA foreign_keys`).
* Nueva utilidad `frontend/src/utils/entregaParcial.js`, consumida por `PedidoCanvas.vue`, `ManualRemitoView.vue`, `PedidoList.vue`.
* Cards #119 (ALTA, enmascaramiento Pydantic `getattr` 3-args) y #120 (ALTA, borrado de remito sin paso por `papelera_registros`) creadas.

### Hito 2: Cherry-pick a B frenado + investigacion de drift
* Pre-flight OK pero divergencia preexistente (~24 bloques) en `PedidoCanvas.vue` de B detiene el cherry-pick.
* Investigacion solo lectura (`git log --follow`, `git log -S`): 13 archivos divergentes en 6 modulos, practica estructural repetida (no incidente puntual), un caso legitimo de flujo inverso P->D autodocumentado (`dbfca1e`->`85a0b630`). Informe completo: `INVESTIGACION_DRIFT_B_S857.md` (Silo).
* Doctrina FIX-P y plan de espejo en 6 lotes disenados, pendientes de dictamen Nike (FIX-P y Lote 5) o ejecucion (Lote 0/2).

### Hito 3: Relevo de arquitecto e instalacion de CS nueva
* Sesion de chat con contexto extenso; CS nueva instalada como arquitecta principal via prompt de instalacion estandar, CC como puente de continuidad.
* Confirmada continuidad sin repetir ALFA (misma sesion CC, hashes verificados contra `SISTEMA_STATUS.json`). Descubierto conector de Google Drive habilitado en la cuenta de la CS -- matiz no contemplado en `FAQ_ARRANQUE.md` sobre "acceso a disco solo via CC/Gy".
* CS autorizo Lote 1 (C5) + Lote 3 (UI) del cherry-pick; ejecutado, buildeado y verificado E2E contra datos reales de B (remito parcial creado en vivo sobre Pedido #66), pusheado a `prod/main` con PIN 1974.

### Hito 4: Correccion de proceso
* `.pasaporte_v5.json` (capa Maquina de la Trinidad) llevaba sin actualizarse desde S852 pese a multiples OMEGA formales -- corregido en este cierre.

**Estado:** NOMINAL GOLD. D:13d6ca3e B:527156b. PIN: 1974.

# 2026-08-28 — Sesión 858 (OF, Lite)
S858 — fix Rosa/Blanco completo (bucket CUIT, paridad MULTI_CUIT, Escudo Backend,
Doctrina de Linaje `cliente_origen_id`), root-cause de dictámenes de Nike verificados
contra código real antes de aceptarlos, migración 038 corrida sobre producción real
(8 clientes Rosa migrados, PIN 1974, coordinado vía relay de archivos con CC en
Izquierda/MT). Sesión rescatada tras corte de plataforma — ALFA completo, Edge Case A
resuelto, nada perdido. Cierre Lite por override explícito de Carlos (límite de
tiempo/tokens); Bit 19 sigue ON. Pendiente: desplegar `98220f9`/`b3366e2` a P y
reiniciar el proceso vivo.
**Estado:** NOMINAL GOLD. D:<CIERRE> B(OF):b3366e2. PIN: 1974.
