Sesion actual: 859

# CAJA NEGRA: OMEGA Completo - cierre real de la saga Rosa/Blanco en P + auto_migrar.py - S859 (2026-09-02)

Sesion 859 OF. Hash D: <CIERRE> | Hash B: <CIERRE_B>. Estado: NOMINAL GOLD. Semaforo CS: AMARILLO. Agentes: CC, Carlos, CC-en-P (Izquierda/MT).
- Retomando el pendiente critico de S858 (deploy del fix Rosa/Blanco a P nunca completado por bloqueo de permisos): diagnostico confirmo que P seguia en 527156b -- el pull nunca habia traido b3366e2, ni con el proceso reiniciado. Coordinado via relay de archivos Silo/B/CC_en_D y CC_en_P.
- PIN 1974 en vivo en la sesion de CC-en-P (no alcanzaba con aprobacion en este chat -- regla explicita). Causa confirmada por git status: current/static/index.html modificado sin commitear bloqueaba el pull en silencio. Descartado, reintentado -- nuevo conflicto con el script suelto migrate_038 (copiado a mano el 28/08) colisionando con el mismo archivo del merge; verificado byte-identico antes de sacarlo del medio. Pull fast-forward limpio a b3366e2, confirmado por hash Y por contenido real (solicita_baja presente en service.py).
- Incidente de produccion real: al reiniciar con el codigo nuevo, la app completa cayo con 500 en clientes/pedidos/dashboard. Diagnostico propio de CC-en-P sin que nadie lo pidiera: la migracion 037 (cliente_origen_id) nunca se habia corrido contra la base real de P -- el codigo ya asumia la columna, el dato no la tenia. PIN 1974 en vivo, backup previo, migracion 037 corrida sobre produccion real (57 clientes backfilled). App recuperada, verificado sin 500.
- Confirmacion final end-to-end por Carlos en la UI real: MYM dado de baja logica, luego borrado fisico correcto desde Utilidades Maestras (sin hijos, IS_VIRGIN habilitaba el borrado). Cierra la saga completa iniciada el 28/08.
- Prevencion de fondo disenada y construida: scripts/auto_migrar.py -- detecta migraciones pendientes por MIGRATION_ID (sin ejecutar), backup automatico solo si hay algo pendiente, corre en orden, frena limpio sin arrancar el servidor si una falla. Analogia explicita de Carlos con actualizaciones de OS (silenciosas, sin exponer al operador). Un bug propio encontrado y corregido antes de integrarlo (regex tomaba el MIGRATION_ID de ejemplo del docstring de migrate_000 en vez del real). Probado con 3 casos reales en sandbox aislado antes de tocar produccion: nada pendiente (silencioso), migracion rota simulada (frena limpio, backup, no sigue), y de paso encontro y aplico dos migraciones reales que estaban huerfanas (030 en D, 030+038 en la copia local de prueba de B) -- ambas aditivas, sin riesgo.
- Integrado en ARRANQUE_V5.bat de B como paso 1.5. Cherry-pick de _env_db.py a current/scripts/ (nunca habia llegado ahi). Card #123 creada y cerrada con evidencia de las 3 pruebas. Commits D: b4d900da. Commit B: d176b59, pusheado a prod/main.
- P/Izquierda queda en b3366e2 (un commit detras de prod/main, solo trae auto_migrar.py sin cambio de schema -- bajo riesgo, sin apuro).
- D:<CIERRE> B(OF):<CIERRE_B> | PIN: 1974

---

Sesion 858 — 2026-08-28 — OF (referencia historica preservada abajo)

# CAJA NEGRA: OMEGA Lite - fix Rosa/Blanco (CUIT bucket, MULTI_CUIT edicion, Doctrina de Linaje) + migracion 038 en produccion real - S858 (2026-08-28)

Sesion 858 OF. Hash D: b798ac09 | Hash B (OF): b3366e2. Estado: NOMINAL GOLD. Semaforo CS: AMARILLO. Agentes: CC, Carlos, Nike, CS (relevo), CC-en-P (Izquierda/MT).
- Root-cause de bug real de produccion (400 al dar de baja cliente Rosa MYM/M&M): CUIT '00000000000' (reservado a Mostrador/Generico) compartido con 8 clientes Rosa + Escudo Backend pisando la baja logica. Reproducido con evidencia real en copia aislada de P antes de tocar nada.
- Serie de dictamenes/enmiendas de Nike (bocetados por CC, corregidos dos veces tras verificar contra codigo real antes de aceptarlos): Bit 1 = IS_VIRGIN universal salvo Remitos (por 'estado', no CAE); MULTI_CUIT paridad alta/edicion + propagacion excluyendo GENERIC_CUITS; Doctrina de Linaje de Identidad Rosa->Blanco via 'cliente_origen_id' (auto-referencial).
- Implementados y verificados en D con evidencia real (navegador + API, no solo lectura): (1) bucket CUIT Rosa 11111111119 en vez de '00000000000'; (2) MULTI_CUIT en edicion (409/200 segun Bit5, propagacion a hermanos, exclusion de GENERIC_CUITS); (3) Escudo Backend ya no pisa baja logica explicita; (4) 'cliente_origen_id' + flujo de formalizacion Rosa->Blanco en frontend. Card #122 creada (delete_pedido no verifica remitos).
- Commits D: b872da72 (items 1/2/4 + Escudo) y 54555ded (migracion 038, script de datos). Cherry-pick a B: 98220f9 y b3366e2, ambos en prod/main.
- Sesion se corto por interrupciones de plataforma justo antes del handoff a Izquierda/MT -- rescatada en una sesion nueva, ALFA corrido de cero (no fast-path), Edge Case A (stale lock, timeout doctrinal) resuelto, estado verificado contra disco real (nada se perdio ni se ejecuto de mas durante el corte).
- Coordinacion con CC-en-P (Izquierda) vía relay de archivos en Silo/B/CC_en_P y CC_en_D: migracion 038 corrida sobre V5_LS_MASTER.db real con backup previo verificado -- 8 clientes Rosa migrados a 11111111119, Mostrador/Generico real intacto (verificado dos veces). CC-en-P detecto por su cuenta que el pull completo traeria tambien 98220f9 (fuera del alcance autorizado ese paso puntual) y opto por copiar solo el script -- decision correcta, deja pendiente el deploy del fix del Escudo a P.
- Diagnostico Soberana: `.build_hash` en P SI persistio correctamente hoy (527156b, 10:08) -- la corrida de esta manana de Tomy simplemente fue antes de que existiera el codigo nuevo (pusheado a las 16:52). No hay evidencia de lanzador roto en esta instancia. El escenario de static/index.html modificado bloqueando un pull real sigue sin probarse -- el pull posterior quedo bloqueado por el clasificador de permisos de esa sesion, pendiente aprobacion en vivo.
- Hallazgo operativo nuevo: hay un proceso vivo en P (puerto 8090) sirviendo produccion ahora mismo -- traer codigo nuevo a disco no alcanza, hace falta reiniciar el proceso para que sirva el fix.
- Cierre Lite por decision explicita de Carlos (override de Bit 19, que sigue ON) dado limite de tiempo/tokens de esta sesion rescatada -- retomar Completo en el proximo cierre real.
- D:b798ac09 B(OF):b3366e2 | PIN: 1974

---

Sesion 857 OF. Hash D: 13d6ca3e | Hash B: 527156b. Estado: NOMINAL GOLD. Semaforo CS: AMARILLO. Agentes: CC, Carlos, CS.

Sesion 857 OF. Hash D: 13d6ca3e | Hash B: 527156b. Estado: NOMINAL GOLD. Semaforo CS: AMARILLO. Agentes: CC, Carlos, CS.
- Fix C5 (null-check remitos_items huerfano) + UI de seleccion de renglones/OC/resumen de deuda en remito parcial, construidos y verificados en D (4 commits). Cards #119/#120 (ALTA) creadas.
- Cherry-pick a B frenado al detectar ~24 bloques de divergencia preexistente en PedidoCanvas.vue. Investigacion solo lectura (git log --follow/-S) confirmo 13 archivos divergentes en 6 modulos: practica estructural repetida (cherry-picks quirurgicos no arrastran features adyacentes de D), no incidente puntual. Un caso legitimo de flujo inverso P->D autodocumentado (dbfca1e->85a0b630). Informe completo: INVESTIGACION_DRIFT_B_S857.md (Silo).
- Doctrina FIX-P (marca de emergencia para fixes directos en B/P) y plan de espejo D->B en 6 lotes disenados, pendientes de dictamen Nike (doctrina y Lote 5) segun exige FAQ_ARRANQUE.md sin excepcion.
- Relevo de arquitecto: CS nueva instalada como arquitecta principal (prompt de instalacion estandar), CC como puente de continuidad. Confirmada continuidad con evidencia real (hashes contra SISTEMA_STATUS.json) sin repetir ALFA -- misma sesion CC ininterrumpida. Descubierto que la cuenta de la CS tiene conector de Google Drive habilitado sobre el mismo Silo (autorizado por Carlos para otro uso) -- matiz no contemplado en FAQ_ARRANQUE.md sobre acceso a disco exclusivo via CC/Gy.
- CS autorizo Lote 1 (C5) + Lote 3 (UI propia) del cherry-pick, Zona Verde. Card #92 verificado sin divergencia oculta. Ejecutado: build limpio en B, verificacion E2E contra datos reales (remito parcial genuino creado sobre Pedido #66, guard de sobre-entrega confirmado por atributo HTML real, preview con marca PARCIAL). Push a prod/main con PIN 1974 (527156b).
- Correccion de proceso: .pasaporte_v5.json no se actualizaba desde S852 (24/07) pese a multiples OMEGA de por medio -- corregido.
- D:13d6ca3e B:527156b | PIN: 1974

---

Sesion 856 OF. Hash D: 29e2bf0b | Hash B: a732e6c (sin cambios). Estado: NOMINAL GOLD. Semaforo CS: [pendiente confirmar]. Agentes: CC, Carlos, CS.
- ALFA completo corrido antes de tocar nada (a pedido explicito de Carlos/CS). Canario NOMINAL GOLD, rama main en D y B, sin bits bloqueantes, FAQ_ARRANQUE sin cambios.
- Detectado al preguntar por la fecha real: el reloj del sistema decia 2026-08-24, diez dias despues de lo que toda la documentacion de la sesion anterior asumia como "hoy" (2026-08-14). Verificacion cruzada (git fetch, mtimes reales de archivos, API de Google Drive) confirmo que hubo una Sesion 855 en CA el 2026-08-15, mas moderna que la nuestra y nunca cerrada con OMEGA.
- Sesion 855 (CA) hizo trabajo real: pull a los hashes de cierre de S854, arreglo de Card #93 en el disco de CA (sin commitear), recorrido completo del Board (17 escrituras, cards #106-115 creadas, duplicados resueltos, Card #21 reabierta por cierre prematuro sobre cobertura futura), canonizacion de 4 entradas en BIBLIOTECA_NIKE.md (21->26 encabezados, verificado independientemente). Hallazgo central de esa sesion: de 5 decisiones que se iban a canonizar como dictamen, 3 no tenian respaldo en disco (dictamen Nike Genoma Cliente 30/07 inexistente, C2/C3 nunca elevado a Nike, "Regla A/B" nomenclatura de chat) -- venian de memoria de CS, descartadas por falta de fuente antes de escribirlas como canon.
- Cierre retroactivo ejecutado hoy desde OF, no desde CA -- marcado explicitamente como tal en el Informe Historico, sin simular que ocurrio el 15/08. Dos cosas NO se corrigieron a ciegas: el bloque de CA en SISTEMA_STATUS.json (sigue con datos de S844, agente_activo:null, pese al pull real) y el fix de update_board.py en el disco de CA (sigue sin commitear alli) -- ambas quedan como pendiente explicito para la proxima sesion fisica en CA.
- Fix real de Card #93 aplicado y commiteado desde OF: scripts/update_board.py linea 6 wb.active -> wb['Board V5'] explicito, mas verificacion de relectura post-guardado. Probado con escritura inocua (fila de prueba en Board V5, confirmado que no toco CSV_DUMP_ARCHIVADO, luego borrada) antes de usarlo para las cards nuevas.
- 3 cards nuevas (#116/#117/#118), halladas por CS releyendo ALFA.md/OMEGA.md el 15/08: checkbox de Manuales en OMEGA permite vaciar contenido real con "sin cambios esta sesion" (verificado hoy: Manuales de esta misma sesion NO se tildaron asi, se dejo constancia explicita de que Bit1/Cap27 y Bit6/Caps13-24 no se revisaron); fast-path de ALFA usa hash de codigo como proxy de integridad de datos, sin detectar drift de schema (incidente real: CA con hash perfecto y 3 migraciones faltantes, 500 reales); canario de OMEGA FASE 1 hardcodeado a pilot_v5x.db -- confirmado hoy que C:\dev\v5-ls-Tom\OMEGA.md tambien lo tiene hardcodeado (lineas 35 y 66), mismo patron que mato el backend real de Tomy en S851.
- Manuales: Sesion 856 NO se tildo "sin cambios" -- se declaro explicitamente que la revision de contenido no se hizo, con las secciones pendientes nombradas (Cap 27, Caps 13/24 del Manual Tecnico). Decision de Carlos, para no cumplir el checkbox del mismo modo que la propia Card #116 denuncia.
- D:29e2bf0b B:a732e6c | PIN: 1974

---

# CAJA NEGRA: OMEGA Completo - BR#8 cerrada por evidencia de hash (precedente), Board reconciliado (Card #102 recuperada, #103/#104/#105 creadas), diagnostico remito parcial sin fix - S854 (2026-08-14)

Sesion 854 OF (un dia). Hash D: f65e8048 | Hash B: a732e6c (sin cambios). Estado: NOMINAL GOLD. Semaforo CS: VERDE. Agentes: CC, Carlos, CS.
- Etapa 1 de arranque: verificacion de si hubo OMEGA real de S853 (Carlos creia recordar haberlo cerrado desde otro chat, sin rastro en el Silo). Cruzados 5 indicadores (informe historico, session_counter.json, BITACORA_VIVA archivada, SISTEMA_STATUS.json, Board BANDERAS_ROJAS) -- veredicto: SI hubo OMEGA formal el 10/08, pero la Bandera Roja (BR#8) quedo abierta a proposito, no por descuido.
- BR#8 cerrada por evidencia de hash, no por su criterio literal (hash Y arbol limpio) -- estructuralmente incumplible porque MT rebuildea en cada arranque y current/static/index.html esta trackeado. Ademas el criterio media la cosa equivocada: BR#8 investiga un fix de backend, el unico archivo trackeado sucio es un artefacto de frontend. Primera vez en el Silo que se cierra una bandera con evidencia distinta a la que su criterio pide -- precedente sentado con fundamento completo en el comentario de cierre (BOARD_V5.xlsx, BANDERAS_ROJAS fila 8).
- Investigacion documental previa: el dictamen de BR#4/Card #87 (dist/, S850) fue puntual, no general -- static/ se excluyo a proposito porque es lo que FastAPI sirve. El precedente pesaba en contra de destrackear static/, no a favor.
- Board: Card #102 (creada S853, contradiccion Bit1 en GENOMA_UNIVERSAL.md) nunca habia llegado a BOARD_V5.xlsx -- segunda perdida de registro confirmada por el bug de wb.active (Card #93, ahora en ALTA). Escrita con texto verbatim. Cards #103 (angostar arbol_limpio), #104 (por que MT rebuildea si ya recibe el build por git -- Nike) y #105 (dictamenes de Nike sin canonizar) creadas.
- Diagnostico del remito parcial completo, sin fix: cantidad_entregada se expone correctamente (confirmado con JSON real de Pedido #63: 100/50, Bit20 ON). El bug es de frontend -- ManualRemitoView.vue auto-completa todos los renglones con saldo sin paso de seleccion; PedidoList.vue (tablero) ya recibe cantidad_entregada y oc y no los renderiza por renglon.
- Hallazgo no buscado: PedidoInspector.vue tiene logica de aviso "FALTA REFERENCIA OC" condicionada a cliente.oc_required, campo que el backend nunca envia (0 matches en backend/**/*.py) -- inerte desde que se escribio. Bit 6 de Cliente confirmado muerto en las dos lecturas (OC_REQUIRED codigo / TRUSTED_MANUAL doctrina), con comentario en clientes/constants.py que afirma falsamente su uso en router.py.
- Decision de Carlos: no se importa produccion a D (Etapa 2 cancelada) -- el diagnostico es de frontend y Pedido #63 ya da el caso real necesario.
- Housekeeping: session_counter.json aparecio pisado a 0 (mismo sintoma que el fix de S853, cuyos causantes -- fix_status.py/_PELIGRO_ -- ya no existen en disco, confirmado por busqueda). Descartado y corregido a 854 en este cierre.
- Sin cambios de codigo funcional en D ni en B. Commit de cierre bookkeeping (Board via Excel en el Silo, no via git).
- D:f65e8048 B:a732e6c | PIN: 1974

---

# CAJA NEGRA: OMEGA Completo - correccion de hashes stale, callejon del share de MT, reporte automatico de estado, BR#8 - S853 (2026-08-10)

Sesion 853 OF (la mas larga del proyecto: 16 dias, 3 maquinas, dos bloques concurrentes que numeraron en paralelo). Hash B: a732e6c (sin cambios). Estado: NOMINAL GOLD. Semaforo CS: AMARILLO. Agentes: CC, CS.
- ALFA: fast-path denegado (hash local 5a3677d6 != hash_D registrado b43647f0). SISTEMA_STATUS.json.OF tenia hash_D/hash_P stale desde los push del 05/08 -- mismo patron exacto que causo la crisis de identidad de CA del 03/08, repetido siete dias despues en otra maquina. Corregido contra disco. Edge Case A: stale lock de 6d16h saneado. timeout_minutos sigue sin escribirse en el JSON (segundo arranque consecutivo que lo detecta).
- Acceso de red a MT: tres intentos, abandonado con causa raiz. El share existe y responde (TCP 445 abierto, nombre resuelto), pero la reinstalacion de Win11 del 31/07 vacio las credenciales y la cuenta de MT no tiene contrasena: Windows rechaza SMB por politica de cuentas con clave en blanco. Destrabarlo exigiria desactivar esa politica en produccion para una consulta de solo lectura. WinRM sigue bloqueado (TrustedHosts ni existe en la maquina reinstalada).
- Solucion estructural: espejo_mt.py (Silo, fuera de git, fuera del flujo D->B->MT) ahora escribe ESPEJO_MT/estado_mt.json con hash, rama, ultimo commit, arbol limpio y hostname de MT en cada corrida de su tarea programada. Solo lectura, envuelto en try/except total, colocado antes del backup a proposito. Cierra el hueco de que el estado de produccion solo se podia averiguar yendo fisicamente (Card #96: .build_hash nunca persiste alli). Riesgo detectado y no resuelto: el script no tiene guarda de maquina.
- Hallazgo en FASE 2: BR#7 fue cerrada el 05/08 17:41 reportando pull a a732e6c y E2E completo en MT real, pero NO tiene fila en BITACORA_VIVA. El Bit 7 (BOARD_PENDIENTE) estaba encendido desde entonces y se reporto como dato decodificado sin ir a mirar el Board, que tenia la respuesta a la pregunta que ocupo el dia. Evidencia corroborante hallada en disco: backup de la base real de MT escrito a las 17:51 (75/54/31, mismo linaje que el espejo) y ultima_actualizacion del JSON a las 17:41.
- BR#8 abierta (unica activa): estado del codigo de MT sin confirmacion directa. Cierra sola con el primer estado_mt.json que reporte a732e6c o posterior. ultimo_hash_B_en_P se dejo deliberadamente en edaf219 -- actualizarlo habria sido dar por confirmado justo lo que la bandera declara no confirmado.
- Card #101 reclasificada de BAJA a real: ARRANQUE_V5.bat:7 y ARRANCAR_TOMY.bat:17 abortan si falta data\V5_LS_MASTER.db, aunque el backend lea current/. Borrar el huerfano tumbaria los tres lanzadores.
- Housekeeping con causa: fix_status.py (y su copia _PELIGRO_) no era un suelto inerte sino un script de S842 que sobrescribe SISTEMA_STATUS.json con valores hardcodeados de julio -- correrlo habria revertido la correccion de hashes de esta misma sesion. Borrado. session_counter.json corregido de 1 a 853.
- Sin cambios de codigo funcional en D ni en B. Commit de cierre solo bookkeeping.

# CAJA NEGRA: OMEGA administrativo — Card #100, diagnostico WinRM bloqueado, certificacion OMEGA/MT por otra via — S852 (2026-07-24)

Sesion 852 OF. Hash D: 6bcf1057 (sin commit de codigo nuevo en D esta sesion) | Hash B: edaf219. Estado: NOMINAL GOLD. Agentes: CC.
- Card #100 creada (BOARD_V5.xlsx, MEJORA, MEDIA): diseno de mecanismo de actualizacion periodica del Espejo Excel/copia offline de MT para consulta sin conexion. Dos caminos evaluados (app en vivo por HTTP vs copia periodica en Drive), direccion elegida es copia periodica con checkpoint cada ~30 min via Task Scheduler, descartando copiar en cada movimiento A/B/M por riesgo real de inconsistencia WAL/locking. Pendiente investigar si backup_db.py ya usa la API de backup online de SQLite antes de inventar mecanismo nuevo. Confirmado #99 como ultimo ID antes de numerar.
- Tarea 1 (pedido de Carlos): cerrar el OMEGA de MT (Bit19, deuda desde S846) via WinRM remoto desde OF (Invoke-Command contra 192.168.1.2). Test-WSMan respondio OK (servicio WinRM activo), pero Invoke-Command fallo -- este cliente (OF) no tiene 192.168.1.2 en TrustedHosts, requerido porque ambas maquinas estan en workgroup (no dominio). Configurar TrustedHosts es un cambio de configuracion de seguridad del sistema -- CC no lo ejecuto sin la mano de Carlos, reporto el comando exacto (`Set-Item WSMan:\localhost\Client\TrustedHosts -Value "192.168.1.2" -Concatenate -Force`) y pidio definicion de credenciales. No se toco Bit19 ni omega_cerrado de MT en ese momento.
- La certificacion de MT se completo igual, por otra via (S852-MT, ver entrada propia de MT en SISTEMA_STATUS.json): canario NOMINAL GOLD, WAL checkpoint OK (con uvicorn real corriendo, sin tocarlo), backup_db.py corrido -- encontro y corrigio un bug real (FUENTES["MAESTRO"] apuntaba a una copia en el Silo que nunca existio ahi, ni en MT ni en OF; fix con el mismo patron _env_db que ya usa canario_v2.py), hash de git edaf219 confirmado. Bit19 de MT apagado, omega_cerrado:true, fecha_ultimo_omega:2026-07-24. Deuda abierta desde S846 saldada.
- Verificacion pedida por Carlos antes de cerrar: git status en D y B confirmado limpio (sin commits ni cambios sin pushear de la sesion) -- unicos hallazgos: 3 archivos sueltos sin trackear en D, todos preexistentes de S851 (documentados en Card #98), ninguno nuevo de hoy.
- FASE 1/1B/1B.2/1C corridas: canario NOMINAL GOLD (0.031s), WAL checkpoint OK, backup_db.py (DESARROLLO rotado nuevo dia sin cambios; MAESTRO sobrescrito mismo dia -- resuelto via checkout local de B en OF que resuelve a entorno TOM), Espejo Excel DEV regenerado (42 pedidos, 73 items).
- Sesion administrativa: sin ALTER TABLE, sin alta/baja de BANDERAS_ROJAS en OF, sin edicion de ALFA.md/OMEGA.md/SISTEMA_STATUS_SPEC.md -- ningun gatillo mecanico de Bit19 (OF) se disparo esta sesion. Perfil de cierre evaluado junto a Carlos considerando el peso real del evento (cierre de deuda de MT de varias semanas, aunque en otra maquina).
- `banderas_rojas_activas` en SISTEMA_STATUS.json: 0 (sin cambios, ya estaba en 0).
- D:6bcf1057 B:edaf219 | PIN: (pendiente FASE 3)

---

# CAJA NEGRA: OMEGA Completo — Cierre BR#5/BR#6, causa raiz backend Tomy caido, investigacion Pedido/Remito — S851 (2026-07-23)

Sesion 851 OF. Hash D: 42857e8f | Hash B: edaf219. Estado: NOMINAL GOLD. Agentes: CC, Carlos (incursion directa en MT).
- Cierre de las dos Banderas Rojas abiertas desde S850. BR#5 (fork Bit 20 Clientes): propagacion a MT confirmada por pull (LANZAR_V5_SOBERANA.bat, corrido por Carlos) y reparacion de datos verificada con SELECT directo sobre V5_LS_MASTER.db real: Bit20 ON 7->1, unico caso genuino restante "Cecilia Pascual" (sin domicilio vinculado). Reparacion corrida con PIN 1974 + backup previo confirmado (data\V5_LS_MASTER_backup_pre_BIT20_MT_20260723_124953.db) + dry-run, autorizado por Carlos en chat -- no fue migrate_pin1974.py (intacto desde 27/05) sino un script ad-hoc nuevo, descartado tras cumplir su funcion puntual (decision: no versionar). BR#6 (auto-push MT): confirmada resuelta, MT en edaf219 incluye el commit del veto (58c5d49).
- HALLAZGO Y FIX DE CAUSA RAIZ: backend de Tomy cayo dos veces hoy en produccion real. Causa: current/scripts/canario_v2.py en B era un duplicado legacy (ultimo commit 2037bee, 2026-05-29) hardcodeado a la ruta de D (C:\dev\Sonido_Liquido_V5\pilot_v5x.db) -- en MT esa ruta no existe, calibracion_constitucional() fallaba siempre, radar_electrico() encontraba "uvicorn" en el commandline del backend real, espolon_defensivo() lo mataba con taskkill /F. Eliminado el duplicado; D y B (scripts/canario_v2.py, la copia viva) migrados a scripts/_env_db.detectar_entorno_db() (Card #93-bis) en vez de mantener una tercera logica de deteccion de entorno en paralelo. Ademas: IP muerta 192.168.0.34 (subred vieja) en scripts/ARRANQUE_V5.bat corregida a localhost; chequeo de existencia de DB agregado (antes arrancaba a ciegas); banner de modo emergencia agregado a ARRANCAR_TOMY.bat (fallback real usado hoy mientras se investigaba, pero no actualiza codigo ni rebuildea frontend).
- Preflight B_DIVERGE disparo tecnicamente antes del push (ultimo_hash_D_en_B=32f630a vs prod/main real=58c5d49) -- confirmado bookkeeping stale de cierre de S850 (el campo nunca se actualizo tras ese push), no divergencia real. Corregido.
- LANZAR_V5_SOBERANA.bat corrido en MT por Carlos (sesion propia, no CC) -- verificado en produccion real: cargo actualizaciones (edaf219, confirmado por Carlos con git log directo) y abrio el sistema sin colgarse. Maquina apagada despues por Carlos -- CC no pudo re-verificar por red (MT offline al intentar el chequeo de solo lectura). Toda confirmacion de estado de MT en esta sesion se apoya en lectura directa de Carlos, no de CC.
- CASI-ERROR ATRAPADO ANTES DE EJECUTAR: antes de disparar Invoke-Command remoto contra MT para correr LANZAR_V5_SOBERANA.bat sin supervision, CC freno y pidio confirmacion explicita -- precedente documentado en S850 (misma pregunta, misma respuesta: no sin supervision) + riesgo tecnico real (el script tiene `pause` interactivo y abre consola via `start`, ninguno de los dos disenado para correr bajo una sesion WinRM no interactiva). Carlos ya la habia corrido el mismo, de forma fisica/propia.
- Investigacion de modelo (sin fix, a pedido explicito de Carlos, caso real: pedido cargado con 6 E2 en vez de 9 E2, ya facturado y remitado, Remito #16): confirmado con evidencia de codigo que Pedido->Remito/Factura soporta 1:N real en el schema (sin unique constraint) y que FacturaRemito es una tabla puente N:M disenada explicitamente para "split de pedidos, consolidaciones, re-facturacion" (docstring propio). cantidad_entregada + Bits 20/21 (HAS_PARTIAL_DELIVERY/FULL_DELIVERED) estan vivos y conectados en create_manual. Bits 22/23 (facturacion parcial) reservados en el genoma sin logica general detras. HALLAZGO REAL: PATCH /pedidos/{id} con items (usado por PedidoCanvas.vue, la pantalla estandar) borra y recrea PedidoItem, cascadeando DELETE sobre RemitoItem vinculados ([CASCADE FIX] explicito en el codigo para no violar la FK) -- destruye la traza de entregas parciales al corregir un pedido. Existe una via no-destructiva ya en el codigo (PATCH /pedidos/items/{item_id}, modifica in-place) pero no conectada al flujo de guardado principal. Card #99 creada (DEUDA, MEDIA) -- proximo ID confirmado leyendo BOARD_V5.xlsx real (ultimo usado: #98), sesion confirmada via esta misma Caja Negra antes de numerar.
- HALLAZGO DE PROCESO: S850 nunca commiteo su propia burocracia de cierre OMEGA -- CAJA_NEGRA.md, ambos Manuales, BITACORA_DEV.md, .pasaporte_v5.json y session_counter.json quedaron editados en disco (FASE 2 corrida) pero jamas se agregaron a un commit; el unico commit de aquel cierre (775216e1) fue el de codigo. Contenido verificado correcto contra la narrativa ya conocida de S850, conservado y sumado (no descartado) en el commit de cierre de esta sesion.
- Bit 19 (FORZAR_OMEGA_COMPLETO) no se encendio en tiempo real al cerrar las filas 5/6 de BANDERAS_ROJAS en el Board pese al trigger documentado en ALFA.md -- mismo patron de gap que S843/S850, sin impacto en el resultado (perfil Completo de todos modos, decidido por Carlos desde el pedido).
- 3 archivos sueltos sin trackear en D detectados y NO stageados: audit_results.txt/audit_results_utf8.txt (dumps viejos irrelevantes) y fix_status.py (script de revert de ~S842, con datos de esa epoca -- peligroso si se corriera hoy por error).
- `banderas_rojas_activas` en SISTEMA_STATUS.json: 2 -> 0. `ultimo_hash_D_en_B` y `ultimo_hash_B_en_P`: ambos -> edaf219. `OF.hash_P` y `MT.hash_P`: -> edaf219.
- D:42857e8f B:edaf219 | PIN: 1974

---

# CAJA NEGRA: OMEGA Completo — Fork de doctrina Bit 20 Clientes, acceso de red a MT — S850 (2026-07-20/22)

Sesion 850 OF (abierta 20/07, cerrada 22/07 tras pausa sin OMEGA de por medio). Hash D: 775216e1 | Hash B: 32f630a. Estado: NOMINAL GOLD. Agentes: CC.
- Housekeeping de arranque: lock fantasma de MT limpiado (Bit8/agente_activo, sin tocar Bit19). OC editable agregada al modal de Remito, deployada D->B con PIN 1974.
- Primer acceso de red directo OF->MT habilitado (share `C:\dev`, tras resolver perfil de red Publico->Privado, sesion SMB de invitado sin permisos, y Windows reusando credenciales viejas). Permitio verificar por lectura directa que `ARRANQUE_V5.bat` coincide con lo versionado y que el auto-push de MT a `prod/main` es una feature deliberada (commit 7e608a1/a9ebe18) que contradice la doctrina, sin resolver.
- HALLAZGO CRITICO: catalogando archivos sueltos en MT aparecio `migrate_pin1974.py`, que revelo un fork de doctrina de 4 meses en el Bit 20 de Clientes — dos significados opuestos (`PENDIENTE_REVISION` V14 vs `ARCA_OK` V15.1 "Paz Binaria") activos simultaneamente en produccion desde el 18/03, nunca detectado. Cliente real mal clasificado confirmado en D y MT ("Cecilia Pascual"). Nike dictamino unificar a `PENDIENTE_REVISION`. Purga ejecutada en un solo commit (doctrina+backend+frontend) en D y B, con correccion de un error de cherry-pick que aterrizo 3/7 archivos en arboles legacy de B (`frontend/` raiz, `staging/`) en vez de `current/` — detectado y corregido antes de pushear (`git show --stat` + verificacion de que `ARRANQUE_V5.bat` sirve desde `current/`).
- Falta propagar el commit a MT (PIN 1974, maquina apagada) y correr script de reparacion de datos de clientes (separado del commit de codigo, D sin PIN, MT con PIN).
- Numeracion de sesion reconstruida con evidencia (git log D/B cruzado con BITACORA_VIVA/INFORMES_HISTORICOS) antes de descubrir que esta misma CAJA_NEGRA.md ya tenia "Sesion actual: 850" desde el cierre de S849 — coincidio, pero la reconstruccion fue innecesaria. `session_counter.json` (archivo distinto, sin ningun consumidor real encontrado en el repo) reparado de `{count:0}` a `{count:850}`.
- Auditoria retroactiva del propio cierre contra OMEGA.md V3.3: Canario/WAL/backup_db.py/Espejo Excel nunca corridos, BITACORA_VIVA sin filas de checkpoint ni fila de cierre formal, CONTEXTO_CS/Bits16-18 sin tocar, Bits 20-25/27-28 de system_flags sin recalcular, `actualizar_card000.py` sin correr, `.pasaporte_v5.json` estancado desde SESION 829 (18/06) — corregido hoy. Rama `backup/` pre-push: salteada, no se puede recrear con sentido retroactivo — a partir de esta sesion, ningun push sin ese paso primero.
- Segunda pasada de autoauditoria (misma sesion, tras pregunta directa de Carlos "¿esta cumplido el Omega?"): brechas residuales encontradas y corregidas — `CONTEXTO_CS/` nunca regenerado (Bits16-18 apagados pese a bandera roja abierta, semaforo mentia VERDE por default), `BITACORA_DEV.md` nunca abierto pese a estar en el pedido, `BITACORA_VIVA` archivada sin filas de checkpoint (5A/10A/15A/20A) ni fila de cierre formal (21) — las tres corregidas.
- HALLAZGO Y CORRECCION DE ERROR PROPIO: `SESION_NEXT.md` (reescrito por CC en esta misma sesion) afirmaba "auto-push de MT dictaminado por Nike, falta ejecucion" — verificado contra `BIBLIOTECA_NIKE.md`, no existia tal dictamen. Carlos aporto el dictamen real (veto al auto-push + aprobacion de Bit 12 REBUILD_PENDIENTE + asignacion de posicion, Bit 12=4096 verificado libre en CA/OF/MT), canonizado en `BIBLIOTECA_NIKE.md`.
- Fix ejecutado en B (mismo patron que la purga de Bit 20 — commit+push sin depender de que MT este online): `LANZAR_V5_SOBERANA.bat` linea 29 (`git push prod main >nul 2>&1`) eliminada — MT vuelve a ser estrictamente pull-only. Bit 12 (REBUILD_PENDIENTE) implementado en `scripts/ARRANQUE_V5.bat`: se enciende si el diff post-pull toca `current/frontend/`, se apaga solo tras `npm run build` exitoso, via nuevo utilitario compartido `Q:\...\actualizar_system_flag.py` (identidad de maquina pasada explicita, no auto-detectada — `current/.gy_identity` de B es stale desde S840). Commit `58c5d49`, push a `prod/main` OK. Bandera Roja #6 abierta (BOARD_V5.xlsx) — a diferencia de la fila 5, no espera a que MT este online, solo a que MT haga su propio pull.
- CASI-ERROR ATRAPADO ANTES DE EJECUTAR (segunda vez esta misma sesion): al correr `actualizar_card000.py` para reflejar el nuevo hash B (58c5d49), la linea 1 de este archivo ya decia "851" (restaurada tras el cierre formal) — hubiera estampado Card #000 como "Sesion 851" para trabajo que en realidad seguia siendo esta misma S850. Revertido a "850" temporalmente, corrido, restaurado a "851".
- `banderas_rojas_activas` en `SISTEMA_STATUS.json`: 1 -> 2. `ultimo_hash_B_en_P` y `OF.hash_P`: 32f630a -> 58c5d49.
- D:775216e1 B:58c5d49 | PIN: 1974

---

# CAJA NEGRA: OMEGA Completo — Reconciliacion D<->B, Historial de Notas, reorganizacion del Silo, cierre BR#4 — S849 (2026-07-14/15)

Sesion 849 OF (accidentada — corte de luz a mitad de sesion, retomada sin perdida de contexto). Hash D: 8429cb14 | Hash B: e3424a6. Estado: NOMINAL GOLD. Agentes: CC.
- Reconciliacion completa D<->B de `exportar_pedidos_excel.py`: la deteccion de entorno (TOM/DEV via .env) existia solo en B; extraida a `scripts/_env_db.py` compartido (sin openpyxl) para que D tenga la misma capacidad real. Corregidos 4 callers (`execute_omega.py`/`omega_closure.py` en D y B) que invocaban el script con un flag `--entorno` ya inerte en B desde hace meses.
- Feature nuevo "Historial de Notas": canal CSV de baja frecuencia para que Tomy deje notas operativas en MT fuera de horario, sincronizadas a `Pedidos.nota` via ALFA + PIN 1974. Diseño iterado en 3 rondas (hoja oculta+formulas -> hoja visible -> CSV real) hasta viabilidad confirmada. Bug real de deduplicacion A/B encontrado y corregido en prueba end-to-end antes de commitear. Verificado con smoke test contra la copia local de B (nunca produccion real).
- Reorganizacion del Silo: carpetas `D\`/`B\`/`P\` creadas para separar lo especifico de cada entorno. Inventario completo de la raiz, resuelto en 6 puntos (basura borrada, historicos archivados, PEDIDOS_ESPEJO viejo a D\, HISTORIAL_NOTAS/PEDIDOS_ESPEJO_TOM/`.bat` de MT a P\, estructura legacy CA/OF anidada en `_LEGACY_MAQUINA_MAYO/`). Card #98 creada para lo que queda.
- Dictamen Nike sobre BR#4/Card #87 ejecutado: `current/frontend/dist/` sacado del tracking de git en B (43 archivos) con evidencia real — mecanismo de rebuild condicional en `ARRANQUE_V5.bat` confirmado (aunque con `.build_hash` roto, nunca persiste — Card #96), precedente historico S843 confirmado como causa raiz del mismo sintoma. Card #87 y las 4 filas de `BANDERAS_ROJAS` cerradas — primera vez en varias sesiones con 0 banderas rojas activas.
- Hallazgo de proceso: `OMEGA.md` del Silo (canonico) y de D habian divergido en direcciones opuestas desde S841 — Silo tenia contenido que D nunca recibio, D tenia el fix de FASE 6 de Card #88 que nunca llego al Silo. B ademas tenia un bug de header (decia "Entorno D", se autorreferenciaba) congelado en V3.0 desde 2026-06-01. Reconciliadas las 3 copias a V3.3.
- D:8429cb14 B:e3424a6 | PIN: 1974

---

# CAJA NEGRA: OMEGA Completo — Feature CUIT duplicado + colision de genoma Bit5 D/B — S844 (2026-07-06)

Sesion 844 CA. Hash D: cf6248ba (pendiente commit de cierre) | Hash B: 218f2a3 (sin cambios). Estado: NOMINAL GOLD. Agentes: CC.
- Correccion de identidad de maquina: `.gy_identity` de la Silo decia "OF" desde 2026-06-18 pese a ser CA la maquina real. SISTEMA_STATUS.json de CA sincronizado (habia cerrado S837 localmente, congelado en el registro desde entonces). Card #89: `.gy_identity` versionado en git dentro de D hereda identidad de la ultima maquina que lo commitea (diseno roto).
- Diagnostico de severidad PIN 1974 en MasterToolsView.vue: proteccion cosmetica de UI, sin validacion server-side en 7 endpoints `/hard` (hard-delete ejecutable sin conocer el PIN via API directa).
- Feature completo "CUIT duplicado / Unidades de Negocio" (dictamen Nike, antecedente real 2026-02-04 nunca completado + Sesion 787): matching difuso (SequenceMatcher 0.85) sobre razon social + domicilio de entrega como gate, modal 3 vias, panel de hermanos, excepcion a guarda GOLD de CUIT unico condicionada a Bit 5 (guarda de razon social / Blindaje Nuclear INAPYR 2026-04-08 PIN 1974, intacta sin excepcion). Verificado con POST real + DB en D (Escenario A 201+bit, Escenario B 400 limpio).
- HALLAZGO CRITICO al cherry-pickear a B: colision de genoma real, Bit 5 = MULTI_CUIT en D vs IS_GHOST en B, divergencia desde ~2026-03-30 nunca detectada — reabre BR#3 (bits fantasma Lacteos/Centro Pet) con causa raiz nueva. Cherry-pick revertido sin commitear, working tree de B limpio confirmado. Card #90 creada, pendiente dictamen Nike. Bloquea despliegue del feature a B.
- D:cf6248ba B:218f2a3 | PIN: 1974

---

# CAJA NEGRA: OMEGA Completo — Diagnostico push faltante B->prod + Bits 10/11 — S843 (2026-07-03)

Sesion 843 OF. Hash D: 0bd56218 | Hash B: 218f2a3. Estado: NOMINAL GOLD. Agentes: CC, Carlos (incursion directa en MT).
- Bits 10/11 (CS_PRESENTE/GA_PRESENTE) formalizados: modelo Principal/Consultivo sin exclusion mutua, dictamen Nike S842 (2026-07-02). SISTEMA_STATUS_SPEC.md + ALFA.md actualizados.
- Diagnostico y resolucion de push faltante B->prod desde cierre de S842: 6 commits (incluido fix critico de `unicodedata` en productos/service.py) quedaron atrapados en B ~22hs. Rebuild frontend + `git push prod main` (PIN 1974). Card #88 creada en Board (deuda tecnica: OMEGA no verifica push multi-remoto).
- Episodio paralelo en MT (incursion directa de Carlos, sin ALFA corrido): atraso de 13 commits por auto-bloqueo de `current/frontend/dist/` trackeado en git — backup, migracion schema 036, pull limpio, rebuild, fix del lanzador `.vbs`. Bug original de Tomy (Rubro con padre_id, 500) confirmado resuelto con smoke test real tras sincronizar B.
- Hallazgo de proceso: Bit 19 (FORZAR_OMEGA_COMPLETO) no se encendio en tiempo real pese a ediciones de ALFA.md/SISTEMA_STATUS_SPEC.md esta sesion — encendido retroactivamente, perfil de cierre = Completo.
- D:0bd56218 B:218f2a3 | PIN: 1974

---

# CAJA NEGRA: OMEGA Lite — Fixes Topología B y UI — S842 (2026-07-02)

Sesion 842 CA. Hash D: 374fe0fb | Hash B: 218f2a3. Estado: NOMINAL GOLD. Agentes: Gy.
- Resolución de split-brain en B (backend parásito borrado).
- Corrección de bugs de UI y Escape Bubbling en Alta de Producto.
- Cards #50 y #51 de Remitos/Pedidos resueltas.
- D:374fe0fb B:218f2a3 | PIN: 1974

# CAJA NEGRA: OMEGA Completo/Lite + Bits CS 16-19 + Bits 26-28 Dâ†’Bâ†’P â€” S841 (2026-07-01)

Sesion 841 OF. Hash D: 0cfdf238 | Hash B: 9555956 (sin cambios). Estado: NOMINAL GOLD. Agentes: CC.

- DiagnÃ³stico del OMEGA S840 (56 min, 53k tokens): 285 tool calls totales, distribuidos en 4 ventanas de contexto. Rabbit holes identificados: lectura de plantillas completas para continuidad narrativa (W2), debugging de `.gy_identity` mal seteado (W3, ~47 min), burocracia de FASE 2 sin batching de tareas (W4).
- Propuesta y aprobaciÃ³n de **perfiles OMEGA Completo/Lite**: Bit 19 (`FORZAR_OMEGA_COMPLETO`) se enciende en el momento del evento (bandera roja, migraciÃ³n, ediciÃ³n de doctrina), no se infiere en FASE 3. FASE 2 anotada Ã­tem por Ã­tem con variante Lite â€” nunca se recorta seguridad/trazabilidad (Canario, BV archival, git backup, verificaciÃ³n de Ã³rbita), solo prosa discursiva (Informe HistÃ³rico, hitos de ESTADO_ECOSISTEMA, sub-bullets de BITACORA_DEV).
- **Bits CS 16-18** (semÃ¡foro de salud de CS): autoevaluaciÃ³n exclusiva de CS, mutuamente excluyentes, sin auto-recuperaciÃ³n. CS_ROJO enciende Bit 40 automÃ¡ticamente.
- **CONTEXTO_CS/ adelgazado**: de bundle completo (SESION_NEXT + BV + status concatenados) a puntero mÃ­nimo (semÃ¡foro + puntero al Informe HistÃ³rico del dÃ­a, secciÃ³n DESTILADO CS). `generar_contexto_cs.py` reescrito â€” fix adicional: ya no hardcodea "OF", lee `.gy_identity` dinÃ¡micamente (mismo patrÃ³n de bug que costÃ³ 47 min en S840).
- **Bits 26-28** (jerarquÃ­a de fuente de verdad Dâ†’Bâ†’P): D_SOBERANO (26, siempre ON), B_DIVERGE (27) y P_DIVERGE (28) detectan commits fuera del flujo Dâ†’Bâ†’P vÃ­a comparaciÃ³n de hash. **LimitaciÃ³n documentada explÃ­citamente**: no detectan divergencia estructural de paths dentro de un hash vÃ¡lido â€” el caso real de S840 (`current/frontend`) sigue sin mecanismo automÃ¡tico â†’ Card #87 creada (DISEÃ‘O/ALTA, requiere dictamen Nike).
- **HALLAZGO operativo menor**: al operacionalizar el mecanismo de `ultimo_hash_D_en_B`, el nombre del campo sugiere un hash de D pero la mecÃ¡nica descrita (comparar contra HEAD real de `prod/main`) requiere que almacene un hash de B â€” inicializado con el hash de B (`9555956`) para que la comparaciÃ³n funcione como estÃ¡ escrita en ALFA.md. Nomenclatura a revisar en sesiÃ³n futura, no bloqueante.
- Card #87 creada en Board. Verificado: `generar_contexto_cs.py` no existe en B â€” nada para cherry-pickear esta sesiÃ³n.
- D:0cfdf238 B:9555956 (sin cambios) | PIN: 1974

---

# CAJA NEGRA: Card #50 + Bug #46#2 + Genoma ALFA Bits 3-9 â€” S840 (2026-06-30)

Sesion 840 OF. Hash D: ad283268 | Hash B: 9555956. Estado: NOMINAL GOLD. Agentes: CC.

- Card #50 CERRADA: eliminado `flags_estado: Optional[int] = None` de `PedidoUpdate` en schemas.py. Cerraba bypass de superficie â€” el endpoint PATCH /pedidos/{id} permitÃ­a modificar bits arbitrarios (incluyendo Bit 13 LAVIMAR y Bit 40 DISCRIMINA_IVA, ambos prohibidos) vÃ­a setattr genÃ©rico sin pasar por STATE_MASK ni los endpoints dedicados (/circuito-bipolar, /no-comercial). Verificado cero usos legÃ­timos en frontend/store/scripts antes del fix.
- Card #46 Bug #2 CERRADO (UX): IngestaFacturaView.vue â€” fix de 3 puntos quirÃºrgicos cuando el OCR no lee el nÃºmero de comprobante de un PDF AFIP: (1) input con borde Ã¡mbar + warning animado si numero=null, (2) guard pre-confirmIngesta que bloquea el envÃ­o sin nÃºmero/guiÃ³n con mensaje claro, (3) handler especÃ­fico de HTTP 400 NUMERO_COMPROBANTE en el catch. Solo frontend, sin tocar backend.
- Card #46 Bugs #1/#3/#4 verificados por cÃ³digo (sin fix): #1 ingesta sin vÃ­nculo previo â†’ 409 PEDIDO_REQUERIDO por diseÃ±o ArlequÃ­n V2, sin UX recovery. #3 PedidoTacticoView sin guard de duplicados (PedidoCanvas sÃ­ lo tiene). #4 PedidoTacticoView sin lÃ³gica de IVA en el total â€” suma cruda.
- ALFA V3.4â†’V3.6 + SISTEMA_STATUS_SPEC V1.4â†’V1.5: genoma de arranque Bits 3-9 (stale lock auto-sanaciÃ³n, firma de agente), Edge Cases A/B documentados.
- actualizar_card000.py: agregadas funciones contar_pendientes + actualizar_bit7 para automatizar Bit 7 (BOARD_PENDIENTE) en cada cierre OMEGA.
- **HALLAZGO IMPORTANTE**: `current/frontend/` en B (v5-ls-Tom) ya divergÃ­a estructuralmente de D antes de esta sesiÃ³n â€” el cherry-pick del fix de Bug #2 aterrizÃ³ en una copia no-servida (`frontend/` raÃ­z de B) porque el path correcto en B's historial git para ese archivo es distinto al de D. Se decidiÃ³ NO parchear a mano la copia divergente (violarÃ­a Regla de Hierro Dâ†’B) y NO desplegar el fix visual a B esta sesiÃ³n. Solo Card #50 (backend) y el script Bit7 llegaron efectivamente a producciÃ³n. Bug #2 queda pendiente de reconciliaciÃ³n en sesiÃ³n futura.
- D:ad283268 B:9555956 | PIN: 1974

---

# CAJA NEGRA: Card #81 Bits 20/21 + Fixes #83/#59 â€” S839 (2026-06-29)

Sesion 839 OF. Hash D: ea117af8 | Hash B: 92c2cc8. Estado: NOMINAL GOLD. Agentes: CC.

- _recalcular_bits_entrega: helper centralizado en RemitosService. Predicate corregido (has_any>0 como guard evita Bit20 espurio en rollback total). Cubre 4 paths: create_manual, create_from_ingestion (EC-B R16 drop-shipping directo), update_remito/ANULADO (EC-A), delete_remito/BORRADOR (EC-A).
- Card #83: PedidoCanvas.vue envÃ­a hora local real en payload fecha (era solo fecha â†’ medianoche â†’ 12:00 en locale es-AR 12h). PedidoList.vue formatDate con hour12:false.
- Card #59: DEBUG_PDF=False en pdf_parser.py. Datos AFIP (CUIT, CAE, cliente) no se vuelcan a disco en producciÃ³n.
- Card #36 cerrada en Board: PEDIDO_GHOST descartado, doctrina Pedidos soberano. S836.
- OMEGA.md: bloque verificaciÃ³n Card #000 post-actualizaciÃ³n agregado en FASE 2.
- Cards #85/#86 creadas: Reestructurar docs D + ALFA V3.4 informe histÃ³rico semÃ¡foro.
- D:ea117af8 B:92c2cc8 | PIN: 1974

---

# CAJA NEGRA: Doctrina Nike S836 â€” Bits Fiscales + ES_NO_COMERCIAL + Genoma Remitos (2026-06-26)

Sesion 836 OF. Hash D: bbe0dcec | Hash B: 6edba99. Estado: NOMINAL GOLD. Agentes: CC.

- ALFA V3.3 canonizado en Q:\Mi unidad\V5_Silo_Claude\ALFA.md. FASE 0 â€” ARRANQUE RÃPIDO: compara hash_D de SISTEMA_STATUS.json con hash local git log -1. Si coinciden y omega_cerrado:true â†’ skip FASE 1 y 2, ir directo a FASE 3. Sin hardcodeo de branch, reutiliza lo que OMEGA ya escribe.
- migrate_036: ALTER TABLE remitos ADD COLUMN flags_estado INTEGER DEFAULT 0. 10 remitos existentes actualizados a DEFAULT 0. Registrada en _migraciones_aplicadas.
- RemitoFlags genoma canonizado (backend/remitos/constants.py). Bits: EXISTENCE(0), HAS_ACTIVITY(1), ES_LIBRE(4), V15_STRUCT(10), VINCULAR_PARCIAL(11), PROHIBIDO(13). Nota: ES_LIBRE Bit4 y VINCULAR_PARCIAL definidos pero pendientes de uso real.
- HAS_PARTIAL_INVOICE = 1<<22 y FULL_INVOICED = 1<<23 en PedidoFlags. Sin migraciÃ³n (flags_estado ya existe). Dos ejes ortogonales: fÃ­sico (Bits 20/21) vs fiscal (Bits 22/23). Cherry-pick 4f88bf67 â†’ B:b32f47d.
- ES_NO_COMERCIAL = 1<<11 en PedidoFlags. Banda de Excepciones junto a NO_FISCAL_FORCE (Bit 12). Reversible con nota forense obligatoria. Cherry-pick bbe0dcec â†’ B:6edba99.
- Doctrina Ghost descartada: pedido_id sigue NOT NULL en remitos. No hay remito sin pedido. Ghost + ES_LIBRE + nullable explorados y abandonados. migrate_037 creado y eliminado en la misma sesiÃ³n. PEDIDO_GHOST Bit43 = dead code en constants.py (purga pendiente S837).
- Doctrina Nike canonizada: Pedidos soberano â€” no hay salida de stock sin pedido. R15>R16>Factura. AsimetrÃ­a Rosaâ†”Blanco. Banda Excepciones Bits 11/12.
- Card #84 creada: Agentes activos en SISTEMA_STATUS + ALFA V3.4. Requiere dictamen Nike (N horas stale).
- D:bbe0dcec B:6edba99 | PIN: 1974

---

# CAJA NEGRA: Talonario 0015 + sombra Blanco + ALFA V3.2 (2026-06-25)

Sesion 835 OF. Hash D: bfa623ba | Hash B: 3b213d1. Estado: NOMINAL GOLD. Agentes: CC.

- ALFA V3.2 canonizado en Q:\Mi unidad\V5_Silo_Claude\ALFA.md. Base path explÃ­cita, lectura Fase 0 expandida, nomenclatura B aplicada. Sin commit â€” el Silo es su hogar.
- Cherry-pick S834 completo a B (da006caf â†’ 33610dc, build frontend). PatrÃ³n session_counter.json: D-especÃ­fico, excluir de cherry-pick via `git rm --cached`.
- Fix UnboundLocalError update_domicilio: service.py:763,775 â€” `from ... import domicilios_clientes` dentro del cuerpo de funciÃ³n hace el nombre local en toda la funciÃ³n (regla Python: cualquier asignaciÃ³n o import de un nombre dentro de una funciÃ³n lo vuelve local en toda la funciÃ³n). Eliminados imports locales redundantes. D:2493105b, B:f6812e8.
- Fix talonario DOS CAPAS: (1) service.py create_manual() 0016â†’0015 en 4 strings (lÃ­neas 542,596,597,608). (2) remito_engine.py preserva prefijo del input en lugar de forzar 0016 (lÃ­neas 327-342). Test: POST 200 OK â†’ 0015-00003010. PDF = 0015-00003010. D:2a35a5a4, B:403ffee.
- DiagnÃ³stico ALFA/OMEGA en D y B: B tiene ALFA V2.0 + OMEGA V2.2 desactualizados. D sin ALFA.md en root. Cards #79 y #80 creadas. update_board.py bug: wb.active devuelve CSV_DUMP_ARCHIVADO en lugar de Board V5; corregido ad-hoc vÃ­a openpyxl directo. Card #79 trackea fix pendiente del script.
- DELETE cascade pedidos prueba #52-#60: 9 pedidos, 6 remitos, 10 items, 6 remito_items (PIN 1974). Sobreviven #51, #61, #62.
- Fix sombra visual Blanco: PedidoList.vue:160 â€” border emerald en AMBOS mode para pedidos sin Bit4096. D:b5932bae.
- Fix serie 0015 dinÃ¡mica: ManualRemitoView.vue â€” ref `ultimoNumeroLegal` almacena `numero_legal` de la Ãºltima respuesta API. Template muestra "Ãšltimo emitido: 0015-XXXXXXXX" en lugar de texto hardcodeado. D:b5932bae, B:3b213d1.
- Cards creadas: #81 (Rollback bits 20/21, ALTA), #82 (Sombra Blanco, BAJA â€” CERRADA esta sesiÃ³n), #83 (Hora hardcodeada, MEDIA).
- D:bfa623ba B:3b213d1 | PIN: 1974

---

# CAJA NEGRA: HAS_PARTIAL_DELIVERY Bit 20 + OMEGA V3.1 (2026-06-23)

Sesion 833 OF. Hash D: 241cddff | Hash P: c613d2c. Estado: NOMINAL GOLD. Agentes: CC + Gy.

- HAS_ACTIVITY (Bit 1) + HAS_PARTIAL_DELIVERY (Bit 20) canonizados en PedidoFlags. Dictamen Nike S833.
- create_manual() en remitos/service.py evalua Bit 20 via @property runtime (PedidoItem.cantidad_entregada).
- ALFA.md V3.0->V3.1: archivo BV pre-header obligatorio, AGENTE explicito, checkpoint cada 5 filas.
- OMEGA.md V3.0->V3.1: BV archivada como condicion obligatoria, commit OMEGA siempre incluye BV.
- Gy: Urgencia Remitos Manuales (Rosa) â€” schemas, service, router, ManualRemitoView V15.1.4.
- Gy: Modal PedidoCanvas (Doctrina Teleport) + Badges PARCIAL en PedidoList y PedidoCanvas.
- Gy: migrate_034 revertido (cantidad_entregada = @property, no columna DB).
- Gy: migrate_035 DROP COLUMN aplicado D+P.
- Cards #79 (OMEGA perfiles) y #80 (auditoria genomas) creadas en Board.
- D:241cddff P:c613d2c | PIN: 1974

---

SesiÃ³n actual: 832

# CAJA NEGRA: Cards #75/#76 SmartSelect + Prompts V4.1/V3.1 (2026-06-22)

SesiÃ³n 832 OF. Hash D: 53429c3f | Hash P: ba9361e. Estado: NOMINAL GOLD.

Card #76 + Card #75 implementacion frontend completa en LogisticaPanel.vue:
- Card #76: SmartSelect nodo_transporte_id â€” condicional Bit6(HAS_NODOS=64). Computed nodoOptions + handler updateNodo + PATCH pedidosStore. D:87e7d554.
- Card #75: GET /clientes/{id}/vinculos â€” nuevo endpoint con filtro flags_mask opcional. Schema VinculoForSelect: Vinculo+Persona join, nombre_completo es @property, serializacion manual por dict (workaround from_attributes). D:5093157f.
- Card #75 frontend: SmartSelect contacto_responsable_id â€” watch cliente_id, fetchVinculos en onMounted+watch, computed contactoOptions, handler updateContacto. FK verificada: contacto_responsable_id -> vinculos.id. D:53429c3f.
- Cherry-pick pattern: falla por _GY/_MD divergencias .gitignore, workaround copy manual D->P. Remote P = "prod". P:ba9361e push prod OK.
- PROMPT_INSTALACION_CLAUDE V4.0->V4.1 + GEMINI V3.0->V3.1: ROL EJECUTORES + PIN 1974 criterio vs lista estatica. Cherry-pick/merge a P/MT en tabla PIN.
- SISTEMA_STATUS.json: banderas_rojas_activas 3->0, deuda tecnica 820 reclasificada amarillo.
- Board CERRADO: Cards #75/#76, 2026-06-22, D:53429c3f P:ba9361e.

**Agente:** Claude Code (Sonnet 4.6) -- Hash D: 53429c3f | Hash P: ba9361e | PIN: 1974

---

# CAJA NEGRA: Card #70 GOLD + PedidoCanvas Sync Dâ†’P + Watcher (2026-06-16)

SesiÃ³n 826 OF. Hash D: 85a0b630 (+ OMEGA push pendiente) | Hash P: de802c6 âœ“. Estado: NOMINAL GOLD.
ALFA V2.0: merge manuales OF+CA (stash/pull/pop, fa29be66). Forensic DOCTRINA rename + DOCTRINA_PROCESOS.md staged.
Card #70 GOLD: SISTEMA_STATUS.json V1.2 + BITACORA_VIVA.md (Q:). Canario 2.0 en ALFA.md (LAVIMAR deprecado).
OMEGA.md 4 capas nuevas + BANDERAS_ROJAS. actualizar_card000.py CP1252-safe. Commit 0b743562.
PedidoCanvas.vue: port watcher route.params.id Pâ†’D (85a0b630). Sync Dâ†’P copia directa (cherry-pick descartado: path mismatch git root D vs P). Build 290 mÃ³dulos. Push prod (de802c6).
Cards #71 (guardar.py) y #72 (hash ALFA Fase 0) en Board.

# CAJA NEGRA: Sync D+P CA + Fix #51 STATE_MASK + Board #60-#70 (2026-06-14)

SesiÃ³n 825 CA. Hash D: b2557445 (pendiente commit) | Hash P: pendiente commit. Estado: NOMINAL GOLD.
ALFA V2.0 ejecutado: sync git D y P en CA. P requiriÃ³ resoluciÃ³n compleja de conflictos post-stash (remote habÃ­a eliminado .pyc/.env del tracking en commit 27190c0). Resuelto con git rm --cached recursivo sobre __pycache__, .env, cantera.db, V5_LS_MASTER.db.
ALFA.md copiado a Q:\Mi unidad\V5_Silo_Claude\ALFA.md (4878 bytes). ALFA.md/ALFA_OLD.md removidos del tracking git D y cubiertos por .gitignore.
Fix quirÃºrgico Card #51 (Bug latente â€” 0 instancias activas): router.py:266 `pedido_viejo.flags_estado = (flags or 0) | PF.ES_ANULADO.value` â†’ `((flags or 0) & ~STATE_MASK.value) | PF.ES_ANULADO.value`. Sin STATE_MASK se dejaba ES_FIRME|ES_ANULADO simultÃ¡neos en migraciÃ³n.
.gy_identity verificado: ambos D y P = "CA".
BOARD_V5.xlsx Q: actualizado: #51â†’CERRADO 2026-06-14. Cards nuevas: #60-#70 (infra, protocolo, SISTEMA_STATUS_SPEC V1.1). Cards #59/#65 duplicados â†’ CERRADO.
Espejo Excel: 36 pedidos, 65 Ã­tems exportados.
Backups DB rotados: MAESTRO+DESARROLLO slots 1-3. Slot 4 en 11 dÃ­as.

**Agente:** Claude Code (Sonnet 4.6) â€” Hash D: b2557445 | PIN: pendiente

---

# CAJA NEGRA: Canon UI Lista 2 + ConsolidaciÃ³n Backup DB (2026-06-12)

SesiÃ³n 824 OF. Hash D: [Por comitear] | Hash P: [Por comitear]. Estado: NOMINAL GOLD.
UI PedidoCanvas: Renombrado "Circuito Celeste/Negro" a "CIRCUITO LISTA 2". Paleta ajustada al canon del sistema (Rosa/Magenta `pink-500`).
Nomenclatura: Renombramiento de `DOCTRINA.md` a `DOCTRINA_DATOS.md` y `DOCTRINA_PROCESOS.md`.
Omega Protocol: Agregada FASE 1B.2 para rotaciÃ³n en cascada de DBs.
Backup DB: Restaurado el script avanzado `backup_db.py` (10006 bytes, con hash guards) en el repositorio y limpiado el directorio ROTATIVO en Silo.
OMEGA V3.0 ejecutÃ¡ndose.

**Agente:** Antigravity (Gy V5) â€” PIN: 1974

---

# CAJA NEGRA: Parche Defensivo Remitos + UI Z-Index Refactor (2026-06-10)

SesiÃ³n 823 OF. Hash D: 1b3dc55b | Hash P: e7572c3. Estado: NOMINAL GOLD.
Parche Defensivo PDF: Se corrigiÃ³ bug 500 en impresiÃ³n de remitos al intentar acceder al producto de un renglÃ³n de pedido (`PedidoItem`) inexistente, producto del borrado fÃ­sico (hard-delete) que no cascada al remito durante ediciones al pedido. Ahora inserta fallback `"ÃTEM DESCONOCIDO"`.
Deuda TÃ©cnica detectada: Falta `ON DELETE CASCADE` en la base de datos para la relaciÃ³n `PedidoItem` â†’ `RemitoItem`, o en su defecto refactor de lÃ³gica en backend.
Refactor UI PedidoCanvas: Footer reubicado dentro de bloque overflow-hidden y subida de jerarquÃ­a de `<main>` (z-index) para resolver el corte transversal del menÃº dropdown de productos Cantera.
Limpieza Transaccional: IntervenciÃ³n manual exitosa en `pilot_v5x.db`. Se borraron 16 facturas fantasma, 12 remitos huÃ©rfanos y los pedidos 47 y 48 de prueba.
OMEGA V3.0 ejecutado completo. Canario NOMINAL GOLD.

**Agente:** Antigravity (Gy V5) â€” Hash D: 1b3dc55b | PIN: 1974

---# CAJA NEGRA: Hotfix 822.1 â€” Pantalla negra Nuevo Pedido (2026-06-05)

Hotfix post-822 OF. Hash D: 34a918fc | Hash P: 7ee67b3. Estado: NOMINAL GOLD.
HaweLayout.vue: v-if â†’ v-show en GlobalStatsBar.
Teleport portal #global-header-center no puede estar bajo v-if (se destruye en transicion).
Con v-show queda en DOM (display:none) y el Teleport lo encuentra. Pantalla negra resuelta.
D y P sincronizados. Cherry-pick limpio.

**Agente:** Claude Code (Sonnet 4.6) â€” PIN: 1974

# CAJA NEGRA: Excel Espejo de Pedidos + UI GlobalStatsBar (2026-06-04)

SesiÃ³n 822 OF. Hash D: 135a16f8 (sin push â€” pendiente PIN 1974). Estado: NOMINAL GOLD.
Entregable principal: Excel Espejo de Pedidos operativo end-to-end.
- Script `exportar_pedidos_excel.py`: formato bloque por pedido, colores STATE_MASK (bits 32-35),
  lÃ³gica IVA Motor Bipolar (bit 12 + condicion_iva_id RI), fila NOTAS mergeada, costos opcionales.
- Endpoint `GET /pedidos/exportar-espejo` en FastAPI (movido antes de /{pedido_id}).
- Frontend: botones "Nuevo" y "Exportar Excel" teletransportados al GlobalStatsBar via <Teleport to="#global-header-center">.
- Safety Net Export (tabla plana pandas) eliminado.
Bug corregido: 422 en /exportar-espejo por route ordering (endpoint especifico antes de parametrico).
Board V5 actualizado: #26 EN PROGRESO, #40 motor prompts, #46 Bugs Tomy NUEVA ALTA.
4 bugs Tomy detectados en P/MT: ingesta sin vinculo, NUMERO_COMPROBANTE, guard duplicados, IVA subtotal.

**Agente:** Claude Code (Sonnet 4.6) â€” Hash D: 135a16f8 | PIN: pendiente

# CAJA NEGRA: AuditorÃ­a Ingesta + Board Banderas Rojas + InvestigaciÃ³n Bits Fantasma (2026-05-30)

SesiÃ³n CA 2026-05-30 (820). Hash D: e41038a0. Estado: NOMINAL GOLD.
AuditorÃ­a del Sistema de Ingesta y FacturaciÃ³n (cÃ³digo vs diseÃ±o arquitectÃ³nico):
  - Sistema al 60% implementado, 25% parcial, 15% pendiente
  - Flujo bÃ¡sico (OCR + anti-duplicaciÃ³n + remito 0016) operativo
  - CRÃTICO: AfipComparisonOverlay.vue visual-only sin acciones (faltan botones ARCA GANA / PEDIDO GANA)
  - CRÃTICO: Split-Brain TIENE_NC/TIENE_ND â€” Bits 2/3 en ingesta/constants.py vs Bits 17/18 en facturacion/constants.py
  - Bits pendientes de crear: PENDIENTE_AJUSTE_DOCUMENTAL (dictaminado Bit 46), PEDIDO_GHOST (1<<43), IS_PROSPECT (128) â€” este Ãºltimo sÃ­ existe en ClientFlags
RestauraciÃ³n DB (PIN 1974):
  - pilot_v5x.db reemplazado desde Q:\Mi unidad\V5_Silo_Claude\pilot_v5x.db
  - Canario post-restauraciÃ³n: NOMINAL GOLD (flags_estado=13, 0.014s)
  - WAL checkpoint: OK
InvestigaciÃ³n forense clientes flags_estado=65581:
  - LÃ¡cteos de Poblet SA (CUIT 33660726859) y CENTRO PET ARGENTINA S.R.L. (CUIT 30715138707)
  - Bits activos: Bit0 EXISTENCE + Bit2 GOLD_ARCA + Bit3 V14_STRUCT + Bit5 MULTI_CUIT + Bit16 INDOCUMENTADO
  - Bit 16 (65536) no documentado en ClientFlags â€” bandera roja #3 levantada
  - CUITs Ãºnicos (no hay colisiÃ³n con otros registros)
  - CENTRO PET: domicilio "Vieytes CABA" duplicado detectado
Board BOARD_V5.xlsx actualizado (Q:\Mi unidad\V5_Silo_Claude\):
  - 7 cards CERRADOS: #6,#7,#8,#9,#10,#27,#28 con fechas_cierre
  - 6 cards NUEVOS: #40 Talonario Rosa, #41 Domicilio Rosa, #42 PENDIENTE_AJUSTE Bit46,
    #43 AfipComparison acciones, #44 Script rescate lunes, #45 Board en ALFA/OMEGA
  - Hoja BANDERAS_ROJAS: 3 banderas ROJA (Split-Brain bits, duplicados pilot, Bit5+Bit16 V5_LS_MASTER)
  - CSV_DUMP regenerado (54 filas, 3 hojas)
Informe archivado en AUDITORIA_INGESTA_FACTURACION_2026-05-30.md (C:\dev\)

**Agente:** Claude Code (Sonnet 4.6) â€” Hash D: e41038a0 | PIN: 1974

---

# CAJA NEGRA: Identidad Visual P + Board Actualizado (2026-05-29)

SesiÃ³n OF 2026-05-29 (819). Hash D: 5c15bae2 | Hash P: 92497c6. Estado: NOMINAL GOLD.
Identidad Entorno P â€” Frontend:
  - static/index.html: TÃ­tulo cambiado de "Sonido LÃ­quido V5 [DESARROLLO] - D" a "Sonido LÃ­quido V5 - Mando"
  - static/favicon.svg: Reemplazado diseÃ±o 4 cuadrantes neÃ³n por fondo pÃºrpura sÃ³lido (#6B21A8) + "SL" blanco
  - public/favicon.svg: Sincronizado con static/
  - Commit P: 92497c6 (Fix: identidad entorno P - tÃ­tulo y favicon)
Board Sonido LÃ­quido V5:
  - Agregadas 3 nuevas cards (IDs 29-31):
    * ID 29: ES_ENTREGADO â€” nuevo estado genoma pedidos (DISEÃ‘O, ALTA, Pedidos, V6.0, BACKLOG)
    * ID 30: Bit COBRADO â€” disparador contable (DISEÃ‘O, ALTA, Pedidos, V6.0, BACKLOG, #29)
    * ID 31: Excel snapshot de pedidos â€” implementaciÃ³n (FEATURE, MEDIA, Pedidos, V5.9, BACKLOG)
  - Board guardado en Q:\Mi unidad\V5_Silo_Claude\BOARD_V5.xlsx (32 filas totales)
AuditorÃ­a:
  - Canario D: NOMINAL GOLD (flags_estado=13)
  - WAL checkpoint: OK
  - Git D: 5c15bae2 (main, up-to-date origin/main)
  - Git P: 92497c6 (main, up-to-date prod/main)

**Agente:** Claude Code (Haiku 4.5) â€” PIN: 1974

---

# CAJA NEGRA: Hardening Ingesta â€” 3 Fixes QuirÃºrgicos (2026-05-28)

SesiÃ³n CA 2026-05-28 (818, sub-sesiÃ³n). Hash D: 2938c77a. Estado: NOMINAL GOLD.
AuditorÃ­a cruzada (CC Opus 4.8 + Gy High) sobre mÃ³dulo de ingesta. 3 fixes validados contra cÃ³digo real y aplicados:
  - FIX 1 (URLs): IngestaFacturaView.vue usaba /api/ingesta y /api/remitos en 3 iframes/links; Vite no proxea /api y los routers se montan sin prefijo â†’ 404 en panel de duplicados. Corregido a /ingesta y /remitos.
  - FIX 2 (STATE_MASK): router.py:231 usaba PedidoFlags.STATE_MASK, pero STATE_MASK vive a nivel mÃ³dulo en constants.py, no como miembro de la clase â†’ AttributeError 500 al anular pedido con ORIGEN_FACTURA. Corregido import a `from backend.pedidos.constants import PedidoFlags, STATE_MASK`.
  - FIX 3 (guard None): router.py:243 `flags_estado &= ~2048` sin guard â†’ TypeError si flags es None. Corregido a `(raw_nuevo.flags_estado or 0) & ~2048`.
OMEGA.md FASE 1 actualizado: snippet de canario migrado a lÃ³gica de mÃ¡scara (flags & 13)==13.
Canario D: NOMINAL GOLD.

**Agente:** Claude Code (Haiku 4.5) â€” Hash D: 2938c77a | PIN: 1974

---

# CAJA NEGRA: DetecciÃ³n Temprana Duplicados + Fixes UI (2026-05-28)

SesiÃ³n OF 2026-05-28 (818). Hash D: f7a48c08. Estado: NOMINAL GOLD.
DetecciÃ³n Temprana de Duplicados en Ingesta:
  - BÃºsqueda preventiva en tabla `facturas` por clave Ãºnica al cargar el PDF en `POST /ingesta/raw`.
  - Frontend `IngestaFacturaView.vue` intercepta duplicado y renderiza un panel de comparaciÃ³n de datos.
  - Endpoint `POST /ingesta/raw/{raw_id}/anular-y-reingestar` permite al operador (previa validaciÃ³n de PIN Maestro 1974) anular el procesado viejo (estado "ANULADA"), marcar RAW viejo con Bit 11 (DUPLICATE=2048), anular el pedido originado en la factura, eliminar el remito viejo en BORRADOR y la factura espejo, y dejar el nuevo RAW listo para ser procesado.
Integridad y Cascada en Remito:
  - AdiciÃ³n de `cascade="all, delete-orphan"` en relaciÃ³n `vinculos_facturas` de `Remito` (hacia `FacturaRemito`) en `backend/remitos/models.py` para erradicar huÃ©rfanos al borrar remitos en borrador.
Fix A â€” HaweView null.includes():
  - IncorporaciÃ³n de guard contra CUIT nulo en la funciÃ³n de filtrado: `(cliente.cuit || '').includes(query)` en `HaweView.vue:771`.
Fix B â€” Bucle de RedirecciÃ³n Nuevo Pedido TÃ¡ctico:
  - Limpieza de `ingestaData` del store Pinia en `onUnmounted` de `PedidoCanvas.vue` para prevenir redirecciones indeseadas al mÃ³dulo de Ingesta tras cancelar o salir de una ingesta.
Canario D: NOMINAL GOLD. WAL checkpoint ejecutado.

**Agente:** Antigravity (Gy) â€” Hash D: f7a48c08 | PIN: 1974

---

# CAJA NEGRA: Sync Dâ†’Pâ†’MT + Migraciones + Fixes UI (2026-05-27)

SesiÃ³n OF 2026-05-27 (817). Hash D: ec5cb6de. Estado: NOMINAL GOLD.
SincronizaciÃ³n y Despliegue de Infraestructura: xcopy completo de backend y frontend de D a P. Entorno virtual reconstruido y dependencias instaladas. npm run build ejecutado con Ã©xito en P/MT.
Migraciones de BD:
  - Bit 40 (DISCRIMINA_IVA) re-auditorÃ­a ejecutada en pilot_v5x.db para 28 Responsables Inscriptos.
  - ReparaciÃ³n de consistencia Bit 20/19 ejecutada para 9 clientes anÃ³malos.
  - ALTER TABLE pedidos ADD COLUMN fecha_vencimiento DATE ejecutada con Ã©xito.
  - MigraciÃ³n a Genoma V6 (banda 32+) para todos los pedidos histÃ³ricos segÃºn su estado.
Fix PedidoCanvas Estado Hardcodeado:
  - Variable reactiva `estadoPedido` introducida para registrar y enviar el estado impositivo/operativo real del pedido (`estado: estadoPedido.value`), evitando sobreescritura con "PENDIENTE".
  - Badge visible de solo lectura agregado en encabezado de la ficha del pedido.
  - Poka-Yoke: advertencia visual en pantalla si el pedido es CUMPLIDO o ANULADO, bloqueo de controles en UI, atajo F10 y deshabilitaciÃ³n estricta de botÃ³n Guardar.
Fix Altura Contenedores (Bug Barra Windows):
  - Cambio de `min-h-screen` y `h-screen` a `min-h-full` y `h-full` en PedidoCanvas.vue para adaptarse a la altura dinÃ¡mica de la zona de contenidos y no desbordar por el padding de HaweLayout, eliminando el corte del pie en Windows.
Canario D: NOMINAL GOLD. WAL checkpoint ejecutado.

**Agente:** Antigravity (Gy) â€” Hash D: ec5cb6de | PIN: 1974

---

# CAJA NEGRA: Fix Ingesta/Pedido + Salvaguardas (2026-05-26)

SesiÃ³n OF 2026-05-26 (816). Hash D: 39309805. Estado: NOMINAL GOLD.
Fix Ingesta/Pedido: ReparaciÃ³n de 3 bugs encadenados en el mÃ³dulo de ingesta:
  - BUG 1: IngestaService.approve() retornaba un dict pero el router accedÃ­a como objeto. Corregido a sintaxis dict (`procesada["id"]`, `procesada["estado"]`).
  - BUG 2: service.py aceptaba vinculaciÃ³n de pedido_id como None sin validaciÃ³n. Se hizo obligatoria la existencia del pedido vinculante para aprobar una ingesta.
  - BUG 3: Frontend IngestaFacturaView.vue no permitÃ­a seleccionar pedido en el modal de aprobaciÃ³n. Modificado modal para requerir selector de pedido y enviar payload correcto.
  - Remitos: Eliminado endpoint obsoleto `/remitos/ingesta-process` del frontend y backend en favor de `/ingesta/raw/{raw_id}/approve`.
ImportError en Pedidos Router: EliminaciÃ³n de imports internos redundantes de PF y ClientFlags en la funciÃ³n `_aplica_iva` que causaban fallas al buscar PF dentro de constants.py.
Salvaguardas Remitos: ImportaciÃ³n de validaciones defensivas desde P en `backend/remitos/router.py` para prevenir accesos inseguros a `remito.pedido.cliente` en el endpoint de generaciÃ³n de PDF.
AnÃ¡lisis Comparativo P vs D: VerificaciÃ³n estructural. P (raÃ­z) posee estructura de 9 archivos, mientras que P (current) estÃ¡ al dÃ­a con D con la Ãºnica excepciÃ³n de `backend/core/utils/text.py` que es exclusivo de D.
Canario D: NOMINAL GOLD â€” flags=13. WAL checkpoint ejecutado.

**Agente:** Antigravity (Gy) â€” Hash D: 39309805 | PIN: 1974

---

# CAJA NEGRA: AuditorÃ­a GenÃ³mica + apply_iva Bit40 (2026-05-22)

SesiÃ³n CA 2026-05-22 (815). Hash D: 1faac75e. Estado: NOMINAL GOLD.
AuditorÃ­a GenÃ³mica Completa: Descubrimiento de patrÃ³n sistÃ©mico donde cada regla nueva en `_audit_sovereignty` deja desactualizados los clientes histÃ³ricos. Ejecutadas 5 consultas forenses contra pilot_v5x.db identificando 37 anomalÃ­as en total:
  - Bit 40 (DISCRIMINA_IVA): 28 RI pre-SesiÃ³n 812 sin Bit 40 prendido (causa: nunca fueron UPDATE post-REGLA3)
  - Bit 20 (PENDIENTE_REVISION): 6 clientes con 4 pilares OK pero Bit 20 prendido (fantasma)
  - Bit 19 (MEDALLA_ROSA): 3 clientes Rosa sin Bit 19
  - Bit 2 (GOLD_ARCA): consistente (OK)
  - Bit 1 (IS_VIRGIN): consistente (OK)
  - CF CUIT fallback: consistente (OK)
Script reparaciÃ³n masiva ejecutado: apagÃ³ Bit 20 en 6, encendiÃ³ Bit 19 en 3, total 9 anomalÃ­as corregidas post-diagnÃ³stico.
apply_iva Helper: CentralizaciÃ³n de lÃ³gica fiscal en `backend/pedidos/router.py`. FunciÃ³n `_aplica_iva(pedido, cliente)` reemplaza 5 ocurrencias de tipo_facturacion string con Doctrina V6 (Circuito Bipolar: Bit 12 soberano + Bit 40 decide en blanco).
Commits: d84641b8 (apply_iva), 1faac75e (OMEGA auditorÃ­a).
Plan AuditorÃ­a GenÃ³mica documentado en INBOX: 4 pasos (Gy arqueologÃ­a, CC forense, script reparaciÃ³n masiva, Utilidad Maestra flags).
Agenda 816 CA registrada: Mapa flags UX + 5 bugs pedidos (crÃ­tico: ingesta sin validaciÃ³n pedido refiere).
Canario CA/D: NOMINAL GOLD â€” LAVIMAR flags=13, 29/29 RI Bit40 OK post-reparaciÃ³n.
WAL checkpoint ejecutado pre-OMEGA.
OMEGA V2.2 ejecutado completo: Fase 1B, 2, 4, 6, 7.

**Agente:** Claude Code Haiku 4.5 â€” Hash D: 1faac75e | PIN: 1974

---

# CAJA NEGRA: Genoma Pedidos V6 + OperaciÃ³n Mudanza + Diff 4 (2026-05-22)

SesiÃ³n OF 2026-05-22 (814). Hash D: 5e1e2445. Estado: NOMINAL GOLD.
Genoma Pedidos V6: IntroducciÃ³n de `PedidoFlags` en backend/pedidos/constants.py con bits universales en la banda baja y banda alta (bits >= 32). MÃ¡scara de estados excluyentes (`STATE_MASK`) que abarca `ES_PRESUPUESTO` (Bit 32), `ES_FIRME` (Bit 33), `ES_CUMPLIDO` (Bit 34) y `ES_ANULADO` (Bit 35).
OperaciÃ³n Mudanza: MigraciÃ³n del campo string legacy `estado` a la estructura genÃ³mica en pilot_v5x.db para 31 pedidos y adiciÃ³n de la columna `fecha_vencimiento`.
Router Backend: Modificaciones en `backend/pedidos/router.py` para asegurar que las transiciones de estado apliquen `(flags & ~STATE_MASK) | NUEVO_ESTADO` en escrituras (Paso A) y validen estados con operaciones bitwise en lecturas (Paso B).
PedidoCanvas.vue (Diff 4): IntegraciÃ³n de BigInt en frontend para evitar la pÃ©rdida de precisiÃ³n en JS al evaluar flags > 31 (en particular `isClienteRI` con el Bit 40). RefactorizaciÃ³n de `isSinIVA` (Motor Bipolar: Bit 12 del pedido y Bit 40 del cliente). selectProduct aplica divisor 1.21 en LISTA_5 Ãºnicamente para clientes RI. Desglose fiscal Ley 27.743 en pie del canvas discriminando IVA segÃºn el perfil impositivo y circuito (blanco/negro).
Canario D: NOMINAL GOLD â€” flags=13.

**Agente:** Antigravity (Gy) â€” Hash D: 5e1e2445

---

# CAJA NEGRA: DISCRIMINA_IVA Bit 40 + Purga HerejÃ­a del 15 (2026-05-20)

SesiÃ³n OF 2026-05-20 (812). Hash D: pendiente (pre-commit PIN 1974). Estado: NOMINAL GOLD.
DISCRIMINA_IVA Bit 40: `ClientFlags.DISCRIMINA_IVA = 1 << 40` (1099511627776). Responsable Inscripto = discrimina IVA, emite Factura A, precio de lista / 1.21. Implementado en 3 nodos: constants.py (definiciÃ³n canÃ³nica), afip_bridge.py (auto-encendido desde condicion_iva devuelta por RAR), service.py _audit_sovereignty REGLA 3 (toggle permanente en create/update segÃºn condicion_iva.nombre).
Purga HerejÃ­a del 15: 5 clientes en pilot_v5x.db tenÃ­an Bit 15 (32768 = FacturaFlags.PASADO_A_PEDIDO) encendido por error de IA anterior que confundiÃ³ "Nivel 15" del CÃ³dice ArlequÃ­n (valor decimal = suma EXISTENCE+IS_VIRGIN+GOLD_ARCA+V14_STRUCT = 15) con "Bit 15" (posiciÃ³n = 1<<15). Purga: flags_estado & ~32768. 5 registros saneados. Canario NOMINAL GOLD.
BIBLIOTECA_NIKE.md: MÃ³dulo 2 actualizado con doctrina canÃ³nica "La HerejÃ­a del 15" â€” prohÃ­be asignar 1<<15 en clientes.flags_estado.
INBOX.md: pendiente sesiÃ³n 813 registrado â€” diff 4 PedidoCanvas lÃ³gica selectProduct por Bit 12 (negro) + Bit 40 (RI) + CF (precio final con IVA incluido). isClienteRI computed ya diseÃ±ado.
Frontend diff 4 NO ejecutado â€” postergado sesiÃ³n 813. No commitear.
Canario D: NOMINAL GOLD â€” flags=13. WAL checkpoint ejecutado.

**Agente:** Claude Code Sonnet 4.6 â€” Hash D: b0ac3c47

---

# CAJA NEGRA: HONNEY fix + DEOU F4 + CF CUIT fallback (2026-05-19)

SesiÃ³n OF 2026-05-19 (811). Hash D: 208d6a46. Hash P: 937d5be. Estado: NOMINAL GOLD.
HONNEY fix: hard_delete_cliente() â€” guard IS_VIRGIN relajado para flags_estado=0 (fÃ³siles pre-genoma). Frontend HardDeleteManager: amber border, label "CLIENTE IMPOSIBLE", botÃ³n habilitado, integrity safe.
DEOU F4: 3 bugs en alta rÃ¡pida â€” cliente nacÃ­a inactivo (flags|=3 mÃ­nimo vital), CUIT era '' en lugar de null, _audit_sovereignty ausente en create_cliente. Fix: currentFlags|=3 en ClientCanvas, cuit:null en PedidoCanvas, _apply_cf_cuit_fallback+_audit_sovereignty+activo sync en create_cliente.
CF CUIT fallback: nuevo mÃ©todo _apply_cf_cuit_fallback() en ClienteService â€” si condicion_iva='Consumidor Final' y cuit=null â†’ asigna '00000000000'. Llamado antes de _audit_sovereignty en create y update.
Borrado Dai (pilot_v5x.db) â€” fÃ³sil de test, PIN 1974.
Deuda tÃ©cnica Rosa unification documentada en INBOX.md: 3 estrategias divergentes (Bit4/nibble/Bit19).
Commits D: 1e5d4327 (HONNEY), 0286f0df (DEOU), 208d6a46 (CF CUIT). Cherry-picks P: 85a48b8, 0b31fe2, 937d5be.

**Agente:** Claude Code Sonnet 4.6 â€” Hash D: 208d6a46 / Hash P: 937d5be

---

# CAJA NEGRA: FIX C4 ClientCanvas + IVA Rosa + NavegaciÃ³n + Bit 4 MigraciÃ³n (2026-05-18)

SesiÃ³n OF 2026-05-18 (810). Hash D: ff77a309. Hash P: 3e060bb. Estado: NOMINAL GOLD.
FIX C4 ClientCanvas.vue: has4Pillars bifurcado â€” Rosa valida es_entrega, Gold valida es_fiscal. Eliminado currentFlags &= ~2 (violaciÃ³n doctrina IS_VIRGIN desde frontend).
Syntax error Vite PedidoCanvas: bloque else espurio en savePedido (lÃ­nea ~1306) eliminado. Vite arranca sin errores.
IVA Rosa: selectProduct divide precio /1.21 cuando isSinIVA && origen === 'LISTA_5'. Template v-if="!isSinIVA" oculta secciÃ³n IVA para informales.
Reset post-save: resetPedido(skipConfirm=true) â€” sin confirm() espurio tras guardar.
NavegaciÃ³n corregida: PedidoList.vue (2x) y PedidoInspector.vue (2x) â€” ruta muerta /hawe/tactico reemplazada por named routes PedidoCanvas / PedidoEditar.
MigraciÃ³n Bit 4 (PIN 1974): _audit_sovereignty() gap documentado (requiere segmento_id). UPDATE manual V5_LS_MASTER.db: 4 clientes Rosa confirmados. Sync pilot_v5x.db: 2 nuevas + Ana Robles ya tenÃ­a.
2 commits D: bf406415, ff77a309. 2 cherry-picks P: 5adf6f4, 3e060bb. Push confirmado en ambos.

**Agente:** Claude Code Sonnet 4.6 â€” Hash D: ff77a309 / Hash P: 3e060bb

---

# CAJA NEGRA: AuditorÃ­a Cruzada IS_VIRGIN + Motor Bipolar + Roseti 1482 (2026-05-18)

SesiÃ³n CA 2026-05-18 (809). Hash D: 4010b655. Estado: NOMINAL GOLD (OMEGA pendiente 810).
AuditorÃ­a cruzada Opus 4.7 + Antigravity Pro en serie â€” hallazgos convergentes confirman bugs reales.
IS_VIRGIN rename global: HAS_ACTIVITY â†’ IS_VIRGIN en 15 archivos (clientes, pedidos, facturacion, ingesta, productos, remitos). Guard hard_delete invertido: if not (current_flags & IS_VIRGIN) â€” bloquea tocados, permite vÃ­rgenes.
Motor Bipolar canonizado: Bit 12 (NO_FISCAL_FORCE) del PEDIDO soberano para IVA. isClientRosa (Bit 4) solo para restricciones operativas. Fixes PedidoCanvas: isSinIVA Bit 12, wasIngesta pre-clear, Guardar e Imprimir condicional, 409 early return.
nivel_id huÃ©rfano eliminado ClientCanvas.vue:1557 â€” reemplazado por lÃ³gica CUIT genÃ©rico.
Roseti 1482 creado como domicilio plantilla (ID: 59b01b5a). DOMICILIO_ROSETI_ID en constants.py. _ensure_domicilio_rosa() en create/update cliente Rosa.
DeprecaciÃ³n documentada: campo cliente_id legacy en models.py Domicilio.
Fixes backend pedidos: C1 delete_pedido NameError, C3 NO_FISCAL_FORCE IVA 5 puntos, C5 STRICT_MODE_VIOLATION nivel_lista=None.
3 commits D: c2372d5a, bb5576c9, 4010b655. Push origin/main confirmado.

**Agente:** Claude Code Sonnet 4.6 + Opus 4.7 (auditor) + Antigravity Pro (auditor) + Nike Arq 5.5 â€” Hash D: 4010b655

---

# CAJA NEGRA: Doctrina Virginidad + Atomicidad Ingesta + Sync Dâ†”P (2026-05-15)

SesiÃ³n OF 2026-05-15 (808). Hash D: 513796bf. Hash P: 5865616. Estado: NOMINAL GOLD.
FIX UX PedidoCanvas: botÃ³n "Guardar e Imprimir" oculto con v-if en flujo manual. wasIngesta capturado pre-clearIngestaData. Reset canvas post-guardado manual en vez de redirigir a PedidoList.
FIX Rosa/OPERATOR_OK: esOperatorOk bypasea todo el bloque fiscal en savePedido(). Sin borrador factura, sin remito puente.
Doctrina de Virginidad implementada: removidos 2 triggers incorrectos (4 pilares, Vanguard Canon). Agregados 2 triggers canÃ³nicos: CUMPLIDO en pedidos/router.py, CAE en facturacion/service.py. Ghost pedido remito manual nace PENDIENTE.
DiagnÃ³stico 409 ingesta: raw 80af6b8b stuck en RECIBIDO con downstream ya existente (remito 0016-00002535 + factura AUTORIZADA_AFIP). Reconciliado manualmente (PIN 1974).
Atomicidad IngestaService.approve(): flush-only en create_from_ingestion, checkpoint PROCESANDO, estado ERROR en fallo. Ãšnico db.commit() al final del flujo exitoso.
Cherry-pick Dâ†’P: 4 commits sesiÃ³n 807-808. Conflicto clientes/service.py resuelto con versiÃ³n D (doctrina virginidad). Push P: d3173b2..5865616.

**Agente:** Claude Code Sonnet 4.6 â€” Hashes D: 513796bf / P: 5865616

---

# CAJA NEGRA: Silo Drive + Pricing Engine Soberano + Protocolos ALFA/OMEGA (2026-05-14)

SesiÃ³n OF 2026-05-14 (807). Hash D: 0b34f1f9. Hash P: d3173b2. Estado: NOMINAL GOLD.
Silo Drive creado: Q:\Mi unidad\V5_Silo_Claude â€” README, INBOX, ESTADO_ECOSISTEMA, estructura OF/CA/GLOBAL/LEIDOS.
ALFA.md D y P: PASO 0 con lectura de INBOX + ESTADO_ECOSISTEMA en cada despertar.
OMEGA.md D y P: FASE 1B WAL checkpoint obligatorio antes de exportar DB. ESTADO_ECOSISTEMA como primer Ã­tem de burocracia.
Fix pricing engine: costos=None ya no bloquea con 409 â€” precio soberano del operador. STRICT_MODE_VIOLATION reservado para cliente invÃ¡lido.
3 deudas tÃ©cnicas registradas (sesiÃ³n 807): Badge FALTAN, Guardar e Imprimir, etiqueta botÃ³n por contexto.
DB 807d instalada en D desde MT (5 pedidos nuevos: 34-38). Pedido 38 eliminado (Pao Tandil â€” incompleto, a recrear).
Canario D: NOMINAL GOLD â€” flags=13.

**Agente:** Claude Code Haiku 4.5 â€” Hashes D: 0b34f1f9 / P: d3173b2

---

# CAJA NEGRA: ArlequÃ­n V2 â€” Inferencia Rosa + GENOMA_UNIVERSAL + fix NO_FISCAL_FORCE (2026-05-13)

SesiÃ³n OF 2026-05-13 (806). Hash D: abd34332. Hash P: 2d7c5c2. Estado: NOMINAL GOLD.
GENOMA_UNIVERSAL.md sellado por Nike Arq 5.5 â€” mapa canÃ³nico de bits para todas las entidades del ecosistema.
HerejÃ­a NO_FISCAL_FORCE purgada: Bit10 (1024) â†’ Bit12 (4096) en constants.py, PedidoList.vue (6 refs) y router.py.
Doctrina ArlequÃ­n V2 implementada: inferencia automÃ¡tica de cliente Rosa (OPERATOR_OK Bit4) en _audit_sovereignty().
Consumidor Final blindado: CUIT 00000000000 forzado GOLD_ARCA, nunca infiere Rosa.
CUIT 00000000000 declarado exclusivo del MOSTRADOR/GENÃ‰RICO (bloqueo en create y update).
PROTOCOLO_EMERGENCIA_MT.md creado. 7 Ã­tems registrados en deuda_tecnica.
DevBadge oculto en producciÃ³n (import.meta.env.DEV). Cherry-pick Dâ†’P limpio (4 commits).
Canario D: NOMINAL GOLD â€” flags=13.

**Agente:** Claude Code Sonnet 4.6 â€” Hashes D: abd34332 / P: 2d7c5c2

---

# CAJA NEGRA: EstabilizaciÃ³n Infraestructura y SoberanÃ­a Tomy (2026-05-11)

SesiÃ³n OF 2026-05-11 (802). Saneamiento integral de ProducciÃ³n (Tomy): Carpeta renombrada a `v5-ls-Tom` para consistencia. Exorcismo de rutas legacy (`C:/dev/V5-LS`) en 28 archivos fÃ­sicos (scripts, logs, bitÃ¡coras). Saneamiento de archivos `.env` en `current` y `staging` de P. UnificaciÃ³n de repositorio Git Tomy: merge de divergencias OF/CA, limpieza de binarios (.db, .pyc) del Ã­ndice y push a GitHub (`2abc8d6`). EliminaciÃ³n de mock data en `ClientCanvas.vue` (D y P) y registro de deuda tÃ©cnica para API real de inteligencia comercial. FormalizaciÃ³n de protocolo OMEGA estrictamente manual en `ALFA.md`. Canario D: NOMINAL GOLD â€” flags=13.

**Agente:** Antigravity (Gy V5) â€” PIN 1974

---

# CAJA NEGRA: EstandarizaciÃ³n NumeraciÃ³n 0016 + Ingesta V2 (2026-05-08)

SesiÃ³n OF 2026-05-08 (800). MÃ³dulo Ingesta V2 completo (FacturasRaw/Procesadas). Conserje v2 READ ONLY sellado por Nike. Factura Espejo Bit 22 (PRE_MODULO_FACTURACION = 4227083). Sabueso V5.7: estandarizaciÃ³n 0016-XXXXXXXX en remitos (pdf_parser.py robustecido). Live preview numeraciÃ³n en UI Ingesta. Fix em dash en remito_engine.py (L74, L167). Purgado de LABME y Pedido 32. OMEGA V2.2 ejecutado (PIN 1974). Genoma actualizado: 851.

**Agente:** Antigravity (Gy V5) â€” Hash: 9e593e67

---

# CAJA NEGRA: Genoma Facturas + Conserje Duplicados CA (2026-05-08)

SesiÃ³n CA 2026-05-08 (799). `backend/facturacion/constants.py` (nuevo): clase `FacturaFlags` con mapa completo bits 0-21 de `flags_estado` en tabla facturas, sellado Nike Arq 5.5. Bits: EXISTENCE(1), HAS_ACTIVITY(2), HAS_REMITO(4), ACTIVE(8), V15_STRUCT(1024), PASADO_A_PEDIDO(32768), EN_CUARENTENA(65536), TIENE_NC(131072), TIENE_ND(262144), ES_NC(524288), ES_ND(1048576), AUDITADA(2097152). `models.py`: `notas_auditoria = Column(String, nullable=True)` en Factura â€” texto libre para observaciones de auditorÃ­a, complementa bit 21. MigraciÃ³n 029 ejecutada (`ALTER TABLE facturas ADD COLUMN notas_auditoria VARCHAR`, idempotente, registrada en `_migraciones_aplicadas`). Conserje en `POST /remitos/ingesta-pdf`: guard pre-proceso consulta `facturas` por `punto_venta + numero_comprobante` â†’ HTTP 409 `FACTURA_DUPLICADA` con `factura_id` si existe. Bug G: modal advertencia pedidos duplicados (mismo cliente + fecha + Ã­tems similares) â€” operador decide continuar o cancelar. Canario D: NOMINAL GOLD â€” flags=13.

**Agente:** Claude Code Sonnet 4.6 â€” Hashes: 93a9a3d4 (tÃ©cnico), 58404b1b (Bug G)

---

# CAJA NEGRA: Bugs D/E/F/H + IngestaItemModal ExtracciÃ³n OF (2026-05-07)

SesiÃ³n OF 2026-05-07 (798). Bug C Ã­tem 13 ya resuelto en CA-797. Esta sesiÃ³n: Bugs D/E/F (F4 satÃ©lite PedidoCanvas) â€” Fix F: `ProductoInspector.vue` fetchRubros defensivo en modo satellite; Fix D+E: ProductosView v-if en `<main>` + nombre Ãºnico `AltaProducto_${Date.now()}` en PedidoCanvas. Hash: db72e856. ExtracciÃ³n IngestaItemModal.vue: modal de resoluciÃ³n de Ã­tems extraÃ­do de PedidoCanvas (-137 lÃ­neas) a componente propio con props `items`, emits `resolved/cancel`. Fix H integrado: F4 en modal abre satÃ©lite de alta producto via `handleOverlayKeydown`. BotÃ³n copy descripciÃ³nâ†’buscador. Bugs registrados: IngestaItemModal navegaciÃ³n teclado pendiente. Migraciones ejecutadas en D: 026, 027, 028, 029 (facturas schema drift, EmpresaTransporte.activo). Tablas nuevas en pilot_v5x.db: `deuda_tecnica`, `roadmap`. Hash final: afd5cd74.

**Agente:** Claude Code Sonnet 4.6 â€” Hashes: db72e856, afd5cd74

---

# CAJA NEGRA: Bug C Backend + Migraciones CA (2026-05-06)

SesiÃ³n CA 2026-05-06 (797). Bug B resuelto: `pending409Context` en store pedidos + restore en `onMounted` de IngestaFacturaView â€” canal separado que PedidoCanvas nunca toca (usa `clearIngestaData`). Bug C: 7 bugs forenses en endpoint `/remitos/puente/desde_factura/{id}` â€” `factura_id: intâ†’str` (endpoint inoperativo), `fecha_vto_caeâ†’cae_vencimiento` (AttributeError), doctrina numeraciÃ³n `0016-XXXX-YYYYYYYY`/`0015-XXXXXXXX`, `total_brutoâ†’factura.total` (silencioso 0.0), `cuit_comprador` post-flush. Arquitectura N:M: clase `FacturaRemito` con GUID + fecha_vinculo + flags_estado reemplaza `Table` simple, guard idempotencia en `_vincular_factura_remito()`. Sistema migraciones: `_migraciones_aplicadas` + patrÃ³n SKIP/REGISTER en migrate_000 y migrate_026. Pendiente: D-7 savePedidoâ†’cadena facturaâ†’remito. Informe: `INFORMES_HISTORICOS/2026-05-06_BUG_C_BACKEND_MIGRACIONES_CA.md`

**Agente:** Sonnet (arquitecto) + Claude Code Sonnet 4.6 (ejecutor) â€” Hashes: 9df14bdf, 0cf51130, 529aa2be

---

# CAJA NEGRA: Parser Y-Axis Fix + Modal Sync CA â€” Ingesta PDF Items (2026-05-05)

SesiÃ³n CA 2026-05-05 (796). Causa raÃ­z items[] vacÃ­o: tolerancia Y-axis `/4` (Â±2pts) insuficiente para PDFs AFIP â€” qty y u_medida en misma lÃ­nea visual pero con delta real 5pts. Fix: `/4`â†’`/6`. Caso validado: L EPI S.R.L., Alcohol 70% qty=4,00 precio=$13.500,00. Typo DB corregido (Acoholâ†’Alcohol ID 150). Canario v2.py actualizado TARGET_FLAGS 8205â†’13 post-saneamiento 2026-05-02. Bugs backlog: A (search/ref modal), B (ESC 409), C (ciclo logÃ­stico), Clientes azules, Build P pendiente. Informe: `INFORMES_HISTORICOS/2026-05-05_INGESTA_PARSER_FIX_MODAL_SYNC_CA.md`

**Agente:** Claude Code Sonnet â€” Hashes: pendiente commit OMEGA

---

# CAJA NEGRA: ArlequÃ­n V2 Merge CA â€” Doctrina Bit 1 Resuelta (2026-05-04)

SesiÃ³n CA 2026-05-04. Merge quirÃºrgico feature/arleq-v2-productos en D (5 archivos). 3 bugs post-merge corregidos (VIRGINITYâ†’HAS_ACTIVITY, default=2, lÃ³gica hard_delete). Doctrina Bit 1 canonizada: 1=virgen/borrable, 0=tocado/bloqueado. OMEGA V2.2 en D y P. Informe: `INFORMES_HISTORICOS/2026-05-04_ARLEQ_V2_MERGE_QUIRURGICO_CA.md`

**Agente:** Sonnet (arquitecto) + Claude Code Haiku (ejecutor) â€” Hash D: f9ae409a â€” Hash P: 8ad0ad58

---

# CAJA NEGRA: ModernizaciÃ³n IVA V1 & Espejado Soberano Dâ†”P (2026-04-24)

## 1. ModernizaciÃ³n IVA V1 (Satelite)
Se eliminÃ³ la dependencia de consola (`.bat` arcaico) para la ingesta. Se implementÃ³ una **Interfaz Web (FastAPI + Jinja2)** que permite:
- **Drag & Drop**: Ingesta intuitiva de archivos ZIP/CSV de ARCA.
- **ReporterÃ­a Avanzada**: El `ReportGenerator` ahora incluye el campo `Tipo` (FAC/NC/ND) y la sumatoria de `Î£ (Otros Tributos)`, crucial para el saldo operativo fiscal.
- **Lanzador**: Se creÃ³ `LANZAR_IVA_WEB.bat` para facilitar el acceso de Tomy.

## 2. Espejado Soberano Dâ†”P
Se detectaron divergencias crÃ­ticas entre el entorno de Desarrollo (D) y ProducciÃ³n (P).
- **AcciÃ³n**: SincronizaciÃ³n binaria del Backend y reconstrucciÃ³n (`npm run build`) del Frontend en P.
- **Resultado**: Paridad 1:1 alcanzada. El nuevo mÃ³dulo de **FacturaciÃ³n** y las mejoras de logÃ­stica ahora son nativas en ProducciÃ³n.

## 3. EstabilizaciÃ³n de ProducciÃ³n (BioTenk)
- **Remitos**: Se resolviÃ³ la orfandad del remito #2528 re-vinculÃ¡ndolo al Pedido #28 tras la purga del duplicado #29.
- **PDF Engine**: Se corrigiÃ³ el truncado de domicilios en `remito_engine.py` mediante la concatenaciÃ³n de `calle + numero + localidad` en el Router.
- **UX**: Se forzÃ³ el cambio de Favicon a **Lila/Violeta** en P para evitar errores de contexto operativo.

---
**Marcador de SesiÃ³n**: 2026-04-24_OMEGA_MODERNIZACION_ESPEJADO
**Agente**: Antigravity (Gy V5)

---

# CAJA NEGRA: Estrategia de SoberanÃ­a Fiscal & Centro de LiquidaciÃ³n (2026-04-23)

## 1. ValidaciÃ³n de Arquitectura "Soberana" (Fase 1)
Se ratificÃ³ el funcionamiento del **Asistente de FacturaciÃ³n (Modo Espejo ARCA)**. La premisa es que el sistema asume la soberanÃ­a del cÃ¡lculo fiscal (prorrateos de descuentos e IVA) para evitar errores humanos al cargar en la web oficial de AFIP. 
- **Carga Manual**: Se confirmÃ³ que el CAE y el NÃºmero de Comprobante son tokens externos generados por ARCA que el usuario debe re-ingresar en HAWE para "sellar" la operaciÃ³n.
- **Estado Nominal**: VerificaciÃ³n exitosa del bitmask de sesiÃ³n (Bit 851) y la paridad de datos.

## 2. DefiniciÃ³n de Fase 2: Ingesta AsincrÃ³nica
Se esbozÃ³ la lÃ³gica de **Ingesta de CAE**:
- El sistema permitirÃ¡ arrastrar el PDF de la factura emitida en AFIP o importar un CSV de "Comprobantes Emitidos" para automatizar el sellado de los borradores, eliminando el "copia-pega" manual.

## 3. CalibraciÃ³n Bipolar
Se revisÃ³ la lÃ³gica de filtrado en `PedidoList.vue`. El Bit 1024 (`NO_FISCAL_FORCE`) opera como el switch maestro entre los circuitos **Oficial (Esmeralda)** e **Interno (Ãndigo)**.

---
**Marcador de SesiÃ³n**: 2026-04-23_OMEGA_ESTRATEGIA_FISCAL
**Agente**: Antigravity (Gy V5)

---

# CAJA NEGRA: Siembra Contactos + Purga PostgreSQL (2026-04-19)

## 1. Variable de sistema Windows â€” la fuente real del problema
`DATABASE_URL=postgresql://postgres:Spawn8559@34.95.172.190:5432/postgres` estaba seteada a nivel de usuario en el registro Windows (`HKCU\Environment`). Esta variable pisaba cualquier `.env`, cualquier fallback en `database.py`, y cualquier override manual. Todos los scripts apuntaban a la nube sin excepciÃ³n. Eliminada con `[System.Environment]::SetEnvironmentVariable('DATABASE_URL', $null, 'User')`.

## 2. IP `34.95.172.190` vs `104.197.57.226`
El sistema tenÃ­a dos IPs de Postgres distintas en diferentes archivos. `34.95.172.190` era la variable de sistema (Spawn8559). `104.197.57.226` era la de `backend/.env` (SonidoV5_2025). Ambas eliminadas. El stack opera 100% local.

## 3. Defensa en capas en `import_contactos_bulk.py`
El script ahora: (1) carga el `.env` raÃ­z del proyecto vÃ­a `load_dotenv`, (2) si la URL resultante sigue siendo postgres, fuerza `sqlite:///pilot_v5x.db`. Esto hace al script inmune a contaminaciÃ³n de entorno sin importar quÃ© haya en el sistema operativo.

## 4. SegregaciÃ³n notas en Persona (Person-Centric)
- `notas_globales`: texto visible para el operador (Carlos escribe, asigna tags)
- `notas_sistema`: auditorÃ­a del script (origen, % fuzzy match, cargo detectado, ENTIDAD_PENDIENTE)
Los dos campos son independientes para evitar que el audit sobreescriba notas comerciales.

## 5. Genoma de la siembra (10 contactos)
- flags=16 (solo Bit5): MarÃ­a E. Garrido, Joshua Sosa, SebastiÃ¡n Fiorito, Facundo Ardissone, Ignacio Gonzalo
- flags=48 (Bit5+Bit6): Marcelo Massel, Agustina Verea, Matias E. Castelo, Carolina Papatanasi, Vanesa Vinciguerra
- 3 contactos con `[ENTIDAD_PENDIENTE: Rizobacter*]` â€” listos para vincular cuando se cree la empresa

---
**Marcador de SesiÃ³n**: 2026-04-19_OMEGA_SIEMBRA_SOBERANIA_LOCAL
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: Forense Git Tom + DiagnÃ³stico DB CA (2026-04-18 â€” SesiÃ³n 2)

## 1. Remoto `produccion` eliminado de D
- D tenÃ­a configurado `produccion â†’ v5-ls-Tom.git`. No era automÃ¡tico (CIERRE solo hace push a `origin`), pero era un vector de push manual. Eliminado con `git remote remove produccion`. D ahora tiene un Ãºnico remoto: `origin`.

## 2. Tom's CIERRE.ps1 y OMEGA.md â€” sin cross-push
- Tom empuja a `prod` (remoto inexistente â†’ falla silenciosa con `SilentlyContinue`). Sin riesgo.
- OMEGA.md de Tom: push a `origin` (Tom's own GitHub). Sin riesgo.

## 3. DB de Tom en CA â€” diagnÃ³stico
- `data/V5_LS_MASTER.db` (CA): 9 pedidos, 37 clientes. Rubros con cÃ³digos numÃ©ricos pre-refactor (`'6'`, `'26'`, `'27'`). Sin LAVIMAR.
- DB con ~18 pedidos (OF real) estÃ¡ **atrapada en OF** â€” gitignoreada, nunca viajÃ³. Hay que ir a buscarla fÃ­sicamente o subirla al Drive.
- `.bak` del commit 13-Apr en git: sin tablas (WAL no checkpointed al commitear).

---
**Marcador de SesiÃ³n**: 2026-04-18_OMEGA2_FORENSE_GIT_TOM
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: HuÃ©rfanos + Alta de Rubro en Caliente + AdopciÃ³n (2026-04-18)

## 1. Indicadores de HuÃ©rfandad (Bit 3)
- Dot neon `#24e70f` en tarjetas y listado. Borde verde en inspector. Filtro "HuÃ©rfanos" client-side.
- **Fix crÃ­tico**: `flags_estado` faltaba en `ProductoRead` â†’ frontend recibÃ­a `undefined` â†’ dots nunca aparecÃ­an.

## 2. Alta de Rubro en Caliente (F4)
- Modal Ã¡mbar desde el selector de Rubro. Backend genera `codigo` automÃ¡ticamente (3 chars ASCII + sufijo numÃ©rico).
- `SelectorCreatable`: F4 siempre emite `create`. "Crear..." visible al fondo cuando hay texto.

## 3. Protocolo de AdopciÃ³n V5.9
- ReasignaciÃ³n a cualquier rubro â†’ Bit 3 limpiado silenciosamente en backend.
- ReasignaciÃ³n a General desde huÃ©rfano â†’ modal de confirmaciÃ³n especial antes de guardar.

## 4. Fix Ciclo Reactivo (bug alto de rubro)
- `fetchRubros()` â†’ reemplazo reactivo del store â†’ watch `deep:true` disparaba `full-sync` borrando el form.
- SoluciÃ³n: `productosStore.rubros.push(newRubro)` directo + `localProducto.value.rubro_id = id`. Sin re-fetch.
- F10 ruteado: si modal abierto â†’ `saveRubroFromModal`; si no â†’ `save()` del producto.
- `showRubroModal` hoisted antes de los watches (fix Temporal Dead Zone).

## 5. Fix handleSave
- `ProductosView.handleSave` llamaba doble a `updateProducto`. Simplificado a actualizar lista local con resultado del inspector.

---
**Marcador de SesiÃ³n**: 2026-04-18_OMEGA_HUERFANOS_ALTA_RUBRO
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: Saneamiento Remitos (RAR-V1) + Resiliencia de Identidad (2026-04-16)

## 1. Saneamiento de Remitos (RAR-V1)
- **Flexibilidad de Datos**: ModificaciÃ³n de `schemas.py` y `models.py` para que `bultos` y `valor_declarado` sean opcionales (`nullable`).
- **QR Oficial**: URL actualizada a `https://liquid-sound.com.ar/` en el motor de PDF.
- **EstÃ©tica de PDF**: Etiquetas fijas ("BULTOS:", "VALOR DECL.:") con valores condicionales para evitar ceros innecesarios.
- **DirecciÃ³n Completa**: IntegraciÃ³n de `@property resumen` en el modelo `Domicilio` para visualizaciÃ³n unificada en remitos desde ingesta.

## 2. Resiliencia de Identidad (V5-LS)
- **Fix ReversiÃ³n CUIT**: ImplementaciÃ³n de sincronizaciÃ³n soberana en `ClientCanvas.vue`. Tras validaciÃ³n ARCA, el CUIT corregido sobreescribe reactivamente el dato de Cantera durante el `updateCliente`.
- **Fix Error 500**: Null-safety inyectado en `_audit_sovereignty` de `service.py`. El sistema ya no crashea si un cliente importado carece de CondiciÃ³n IVA durante la auditorÃ­a de domicilios.
- **Blindaje 422**: Manejo de IDs nulos en persistencia de domicilios, redirigiendo correctamente a `POST` cuando el registro es nuevo.

## 3. HomologaciÃ³n de Entornos
- SincronizaciÃ³n binaria total de los mÃ³dulos `clientes`, `remitos` y `Canvas` hacia el repositorio de producciÃ³n `V5-LS`.

---
**Marcador de SesiÃ³n**: 2026-04-16_OMEGA_ESTABILIZACION_SOBERANA
**Agente**: Antigravity (Gy V5)

---

# CAJA NEGRA: ProducciÃ³n Soberana â€” Fixes Operativos + DiseÃ±o Doctrinal (2026-04-15)

## 1. Fix Domicilios â€” Triple Causa del 500
- **Kwarg duplicado**: `is_maps_manual` en `model_dump()` + constructor â†’ `TypeError`. Fix: agregar al `exclude`.
- **Junction table**: `create_domicilio` no insertaba en `domicilios_clientes` (N:M). `GET /clientes/{id}` usa joinedload por esa tabla â†’ domicilio invisible. Fix: `db.execute(domicilios_clientes.insert().values(...))`.
- **Pinia corruption**: `createDomicilio` en store hacÃ­a `splice(index, 1, response.data)` donde `response.data` es Domicilio, no Cliente â†’ store corrompido â†’ loop navegaciÃ³n. Fix: `client.domicilios.push(response.data)`.

## 2. Fix PedidoCanvas â€” Edit Mode
- `savePedido()` siempre llamaba `POST /pedidos/tactico`. En modo ediciÃ³n (route.params.id presente) debe llamar `PATCH /pedidos/{id}`. El endpoint PATCH ya existÃ­a y funcionaba â€” nunca se invocaba.
- Impacto: Tomy generÃ³ ~5 pedidos duplicados en producciÃ³n. Limpiados manualmente en dos pasadas.

## 3. Fix Rosa Clients â€” clienteEsVerde
- Rosa: `(flags_estado & 15) in [9, 11]`. No tienen CUIT ni domicilio obligatorio. El computed `clienteEsVerde` los evaluaba igual que clientes formales â†’ siempre rojo. Fix: detecciÃ³n `isRosa` + `return true` anticipado.

## 4. MigraciÃ³n GENERAL â†’ General
- D: 4 prods migrados de rubro id=28 a id=26. P: 7 prods. `activo=0` en GENERAL (id=28) en ambas DBs.

## 5. Fix PedidoInspector â€” Nota invisible
- BotÃ³n âœ editar nota tenÃ­a `opacity-0 group-hover/nota:opacity-100` â†’ invisible. Fix: `text-yellow-500/50` siempre visible.

## 6. DiseÃ±o Doctrinal â€” OrÃ­genes de Pedido (PENDIENTE implementaciÃ³n)
- La ingesta de facturas creaba pedidos en $0 silenciosamente (satisfy `pedido_id NOT NULL` en remitos). Mal.
- DiseÃ±o acordado: bits libres de `flags_estado` identifican el origen. `BIT_ORIGEN_FACTURA` (con respaldo AFIP, no anular livianamente). `BIT_ORIGEN_REMITO` (sin respaldo, pendiente de facturar).
- El Remito siempre tiene pedido padre (real o forzado). No hay "huÃ©rfanos" â€” son categorÃ­as de pedido.

---
**Marcador**: 2026-04-15_OMEGA_PRODUCCION_SOBERANA_FIXES
**Agente**: Claude Code (Sonnet 4.6)

---

# CAJA NEGRA: Saneamiento DB + Fixes Operativos + Paridad D/P (2026-04-14)

## 1. CirugÃ­a DB â€” pilot_v5x.db
- **Objetivo**: Llevar D a paridad con P post-saneamiento productivo del 13/04.
- **7 fusiones ejecutadas**: grupos {156â†’179}, {176,186â†’172}, {169â†’6}, {170â†’149}, {171â†’175}, {173â†’177}, {152â†’161}. Pedidos re-apuntados (173â†’177, 159â†’175).
- **NULL SKU eliminados**: IDs 158, 159, 160 â€” borrados fÃ­sicamente tras reapuntar pedido de 159 a survivor 175.
- **Limpieza fÃ­sica**: 8 productos borrados (flags=0 Ã³ flags=2, sin movimientos). Estado final: **23 productos**.

## 2. Fixes Backend â€” Cantera Import
- **flags_estado=3**: Productos importados desde cantera ahora nacen con bits ACTIVE+VIRGIN seteados.
- **Auto-SKU**: Si el producto llega sin SKU del mirror, se asigna `MAX(sku)+1` con piso en 9001. Rango cantera: 9001+.
- **SKU Integer**: ConversiÃ³n `int(float(sku_raw))` â€” maneja strings `"123"` y floats `"123.0"` del mirror JSON.
- **rentabilidad_target**: Fix de campo renombrado (ex `margen_mayorista`) que causaba 500 en importaciÃ³n.
- **Paridad D/P**: Mismo cÃ³digo aplicado en ambos entornos.

## 3. Fixes Frontend
- **F4 PedidoCanvas**: Apertura condicional corregida â€” product search tiene prioridad; modal cliente solo en foco explÃ­cito del campo cliente.
- **Rubro obligatorio ProductoInspector**: Asterisco rojo + ring de error + mensaje de validaciÃ³n `rubroError`.

## 4. Fixes Infraestructura
- **DESPERTAR.ps1**: Guard contra null reference cuando `.pasaporte_v5.json` no existe o Git no disponible. Mensaje informativo si no hay `.bak`.
- **boot_system.py**: `--reload-dir backend` (evita reload por writes de Vite). Health check polling vs `sleep(5)` fijo.
- **main.py (D y P)**: Ruta `/` â†’ `/health` â€” libera el catch-all SPA para servir `index.html` en raÃ­z.

---
**Marcador de SesiÃ³n**: 2026-04-14_OMEGA_SANEAMIENTO_DB_FIXES_OPERATIVOS
**Agente**: Claude Code (Sonnet 4.6)

# CAJA NEGRA: Remitos V5.8 GOLD & Productos Fase 1 (2026-04-10)

## 1. ResoluciÃ³n LogÃ­stica Remitos
- **Problema**: Truncamiento de direcciones en ingesta ARCA.
- **Motor de Scoring (ðŸª„)**: Algoritmo de comparaciÃ³n heurÃ­stica para pre-selecciÃ³n automÃ¡tica de sedes legÃ­timas (SSoT).
- **Alta DinÃ¡mica (âž•)**: Persistencia reactiva de nuevas sedes de entrega directamente desde el flujo de ingesta.
- **Paridad P/D**: SincronizaciÃ³n absoluta de la lÃ³gica de resoluciÃ³n entre V5-LS y Desarrollo.

## 2. ModernizaciÃ³n de Productos (Protocolo Alfa)
- **DiagnÃ³stico**: IdentificaciÃ³n de deuda tÃ©cnica en IDs (Integers vs UUIDs).
- **Refactor ArquitectÃ³nico**: ExtracciÃ³n de lÃ³gica de negocio (SKU, Precios, Virginidad) a `service.py`.
- **Cierre Fase 1**: Routers saneados y centralizados en la capa de servicio.

---
**Marcador de SesiÃ³n**: 2026-04-10_OMEGA_REMITOS_PRODUCTOS_GOLD
**Agente**: Gy (Antigravity V5)

# CAJA NEGRA: HomologaciÃ³n Identity Shield V5.7 (2026-04-09)

## 1. HomologaciÃ³n Genoma V5-LS
- **SincronizaciÃ³n**: Paridad total entre Dev y ProducciÃ³n/Staging para el Protocolo Nike (Bag of Words).
- **Backend Master**: InyecciÃ³n de `razon_social_canon` en `V5_LS_STAGING.db` y backfill de 35 registros legÃ­timos.
- **Circuit Breaker**: ImplementaciÃ³n de bloqueo por colisiÃ³n canÃ³nica estricta (Bloqueo Nuclear).

## 2. Sensor UI Antigravedad
- **Componente**: `ClientCanvas.vue` en Staging actualizado con sensor reactivo debounced.
- **AuditorÃ­a**: CertificaciÃ³n `audit_production_duplicates.py` limpia. Estado: NOMINAL GOLD.

---
**Marcador de SesiÃ³n**: 2026-04-09_OMEGA_HOMOLOGACION_NIKE
**Agente**: Antigravity (Atenea AI)

# CAJA NEGRA: Blindaje Nuclear de Identidad (2026-04-08)

## 1. Protocolo Bag of Words V16.2
- **LÃ³gica**: Refactor de `normalize_name` para ser insensible al orden de las palabras ("El Taller SRL" == "SRL El Taller").
- **ImplementaciÃ³n**: TokenizaciÃ³n, eliminaciÃ³n de ruido (<2 chars), ordenamiento alfabÃ©tico y sellado Ãºnico.
- **UnificaciÃ³n de Siglas**: Saneo nativo de puntos en siglas ("S.R.L." -> "SRL").

## 2. HÃ©metizaciÃ³n Estructural (HomologaciÃ³n P)
- **DB Master**: InyecciÃ³n de columna `razon_social_canon` en `V5_LS_MASTER.db`.
- **Saneamiento**: RecanonizaciÃ³n masiva de 37 registros en producciÃ³n. 
- **SincronizaciÃ³n**: Paridad total de lÃ³gica entre entornos D (Desarrollo) y P (ProducciÃ³n).

---
**Marcador de SesiÃ³n**: 2026-04-08_OMEGA_BLINDAJE_NUCLEAR
**Agente**: Antigravity (Google DeepMind)

# CAJA NEGRA: Deudas TÃ©cnicas + Sync DB INAPYR (2026-04-02)

## 1. SincronizaciÃ³n de Base de Datos (CA â†’ OF)
- Base CA reemplazÃ³ base OF. Backup: `pilot_v5x_PRE_CA_20260402.db`.
- Incorporado: INAPYR S.R.L. (CUIT 30714145351, codigo_interno 46), pedido INGESTA_PDF
  (factura 00001-00002514), remito con CAE `86139705410697` (vto 10/04), 2 domicilios La Plata.
- Canario post-migraciÃ³n: NOMINAL GOLD (flags 8205).

## 2. AuditorÃ­a flags_estado â€” BigInteger 64-bit
- 7 modelos activos: BigInteger confirmado. SQLite permisivo (INTEGER = hasta 8 bytes).
- Pydantic: `int` Python arbitrario. Sin validators de cap 32 bits.
- **Dictamen: Deuda ya resuelta. Cerrada sin cambios.**

## 3. Conexion_Blindada.py â€” OpenSSL desacoplado
- Antes: rutas absolutas hardcodeadas `C:\Program Files\Git\...`.
- DespuÃ©s: `OPENSSL_PATH` env var â†’ `shutil.which("openssl")` â†’ fallback Windows.
- `.env.example` creado en raÃ­z con documentaciÃ³n.

## 4. Limpieza de Entorno â€” 37 Scripts HuÃ©rfanos
- Eliminados: debug_* (21), test_* (15), miner.py (1) de raÃ­z, scripts/ y backend/.
- Conservados: `tests/test_v7_*.py` â€” pendiente revisiÃ³n formal.
- Tesseract: confirmado ausente en requirements.txt.

---
**Marcador de SesiÃ³n**: 2026-04-02_OMEGA_DEUDAS_TECNICAS
**Agente**: Claude Code (Anthropic CLI)

# CAJA NEGRA: Burbuja Tomy V5-LS + AuditorÃ­a Seguridad (2026-04-01)

## 1. AuditorÃ­a de Seguridad npm
- Incidente real: Claude Code v2.1.88 con source map (~60MB) publicado por error en npm (31/03/2026).
- InstalaciÃ³n Carlos: nativa, no npm â†’ no afectada. VersiÃ³n activa: 2.1.89.
- axios en proyecto: 1.13.2 (no troyanizado). plain-crypto-js: no encontrado.
- AcciÃ³n: eliminado binario obsoleto `claude.exe.old.*`.

## 2. Blindaje V5-LS (Puerto Unificado 8090)
- **main.py**: corregido `static_dir` path (faltaba un nivel `..` para llegar a `V5-LS/static/`).
- **LANZAR_V5_SOBERANA.bat**: eliminado `python -m http.server 5174`. Un proceso Ãºnico en 8090 sirve API + SPA.
- **SATELITE_TOMY.bat**: actualizado a puerto 8090.
- **Login.vue (V5-LS)**: fix endpoint `:8000` â†’ `api proxy`; fix texto blanco sobre blanco.

## 3. Fixes Dev Versionados (trabajo de Gy del 31/03)
- **ClientCanvas.vue**: UUID nulo al crear cliente (`emit` propagaba formulario sin ID del servidor).
- **PedidoCanvas.vue**: F10 bloqueado en modal (faltaba guarda `if (showClientModal.value) return`).
- **Login.vue**: puerto 8000 hardcodeado â†’ `api.post('/auth/token')`; inputs sin color de texto.

## 4. Deuda Activa
- npm run build pendiente en V5-LS antes de que Tomy opere en producciÃ³n.

---
**Marcador de SesiÃ³n**: 2026-04-01_OMEGA_BURBUJA_TOMY
**Agente**: Claude Code (Anthropic CLI)

# CAJA NEGRA: OperaciÃ³n Vanguardia V5-LS (2026-03-30)

## 1. ReestructuraciÃ³n de Infraestructura
- **Directorio RaÃ­z**: Desmantelado `V5_RELEASE_09` âž” Elevado a `V5-LS`.
- **JerarquÃ­a Soberana**: SegmentaciÃ³n en `current/`, `data/`, `archive/`, `shared/` para independencia modular.

## 2. Movimiento de Activos y Limpieza
- **CÃ³digo Fuente**: Despliegue de backend y frontend en `current/`. Purga fÃ­sica de `venv` y `node_modules`.
- **Base de Datos**: MigraciÃ³n de `pilot_v5x.db` a `V5_LS_MASTER.db` (568 KB Nominal Gold).
- **Credenciales**: CentralizaciÃ³n de `Clave-Jason.jason` en `shared/credentials/`.

## 3. ConfiguraciÃ³n de SoberanÃ­a
- **Network Stack**: Puerto **8090** asignado.
- **Environment Logic**: InyecciÃ³n de rutas absolutas en `.env` para bypassear fallos de ruta relativa en LAN.

---
**Marcador de SesiÃ³n**: 2026-03-30_OMEGA_VANGUARDIA_V5LS
**Agente**: Gy (Antigravity V5 - Atenea)

# CAJA NEGRA: SesiÃ³n Entrega V5-LS Tomy (2026-03-27)

## 1. Network & Routing
- **Puerto 8090/5174**: DefiniciÃ³n de arquitectura dual para evitar colisiones en LAN IP 192.168.0.34.
- **Ruta Hardcodeada (Bug)**: LocalizaciÃ³n de `pilot_v5x.db` forzado en el arranque. Se devolviÃ³ la soberanÃ­a al `.env`.
- **Axios Absolute Fix**: Reemplazo de `/clientes` por `http://192.168.0.34:8090/clientes` en assets minificados.

## 2. Integridad de Datos
- **Purga Master**: EliminaciÃ³n de SKUs de prueba (Agua/Soda) y reseteo de `sqlite_sequence`.
- **Censo de Clientes**: VerificaciÃ³n de 32 registros legÃ­timos en la base de producciÃ³n final.

---
**Marcador de SesiÃ³n**: 2026-03-27_OMEGA_SUPREMO_FINAL
**Agente**: Gy (Atenea AI)

# CAJA NEGRA: SesiÃ³n PerfecciÃ³n Soberana V5.5 GOLD (2026-03-26 Parte 2)

## 1. Movimiento de Bits y Genoma
- **Bit 6 (OC_REQUIRED)**: ImplementaciÃ³n de Poka-Yoke visual (Neon Blue) y validaciÃ³n en PedidoCanvas.
- **Bitwise Logic**: CalibraciÃ³n en Frontend para diferenciar obligatoriedad de asterisco vs borde neÃ³n.

## 2. IntervenciÃ³n en el NÃºcleo (Backend)
- **Decimal Fix**: RefactorizaciÃ³n de 8 puntos en `backend/pedidos/router.py` usando `Decimal(str(item.cantidad))` para evitar TypeErrors con floats.
- **ProductoCosto Extensions**: InyecciÃ³n de `costo_reposicion` y `margen_sugerido` en modelos y esquemas Pydantic.

## 3. Persistencia FÃ­sica y UI
- **PedidoCanvas (Ficha #ID)**: TransformaciÃ³n en "Ficha del Pedido" con tÃ­tulo dinÃ¡mico e hidrataciÃ³n mejorada.
- **Rentabilidad DinÃ¡mica**: Panel F8 migrado de estÃ¡tico a dinÃ¡mico con lÃ³gica de cÃ¡lculo viva sobre `items`.
- **Keyboard Optimization**: Secuencia de foco `Cliente -> OC -> SKU` (Hoja de cÃ¡lculo mode).
- **Hotfix**: Blindaje de `RentabilidadPanel.vue` con guardas contra `undefined reduce`.

---
**Marcador de SesiÃ³n**: 2026-03-26_OMEGA_GOLD_SYNC_V8_6
**Agente**: Gy (Antigravity V5 - Atenea)

# CAJA NEGRA: SesiÃ³n PerfecciÃ³n Soberana V5.2 GOLD (2026-03-25 Parte 3)

## 1. Movimiento de Bits y Genoma
- **Bindings N/M**: Planeamiento estratÃ©gico documentado en `ANALISIS_TRANSPORTE_LOGISTICA.md` para integrar `EmpresaTransporte` y `NodoTransporte` en los domicilios del `Cliente`.

## 2. IntervenciÃ³n en el NÃºcleo (Backend)
- **Pydantic Property Forcing**: ImplementaciÃ³n de `@property cliente_id` expuesta llanamente en `RemitoResponse` para bypassear las limitaciones de lazy-load de SQLAlchemy sin incurrir en N+1 Queries.
- **Client Mapping Fix**: Mapeo riguroso de `payload.cliente.id` en el Router de ingesta de facturas, eliminando la creaciÃ³n colateral de cuentas "Desconocido".
- **Cascaded Eradication**: AdiciÃ³n de `DELETE /remitos` con purga lÃ³gica del remito e interceptaciÃ³n fÃ­sica de eliminaciÃ³n en cascada para su Pedido de origen (sÃ³lo si es `INGESTA_PDF`).

## 3. Persistencia FÃ­sica
- Cambios frontend directos en `RemitoListView.vue` inyectando botones de estado (Imprimir) y cierre (Trash) con reestructuraciÃ³n visual Poka-Yoke.

---
**Marcador de SesiÃ³n**: 2026-03-25_OMEGA_GOLD_SYNC_V3
**Agente**: Gy (Antigravity V5 - Atenea)

