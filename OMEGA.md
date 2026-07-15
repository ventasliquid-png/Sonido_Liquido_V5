# PROTOCOLO OMEGA V3.0 — CIERRE Y PERSISTENCIA DE ESTADO
## Sonido Líquido V5 — Entorno D (Sonido_Liquido_V5)

> Protocolo exclusivo para entorno D (desarrollo).
> Para P ver: C:\dev\v5-ls-Tom\OMEGA.md
> **Versión:** 3.3 — 2026-07-15
> **Dictamen:** Nike Arq 5.5 — Redacción: Carlos + Claude Sonnet 4.6

---

## 🛑 REGLA CERO — EL FRENO DE MANO

Si Carlos indica "Presentar plan SIN ejecutar", ninguna aprobación
automática tiene validez.
- Acción: Pausar y solicitar PIN 1974
- Cláusula de Hierro: "LGTM", "Proceed" o botones de interfaz
  NO sustituyen al PIN 1974.
- [PROHIBIDO] `git add .` — siempre stagear archivos explícitamente.

---

## FASE 1 — AUDITORÍA DE SALUD

Canario obligatorio antes de cerrar:
```python
python -c "
import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
cur = conn.cursor()
cur.execute(\"SELECT id, flags_estado FROM clientes WHERE id = 'e1be0585cd3443efa33204d00e199c4e'\")
row = cur.fetchone()
flags = row[1] if row else 0
print(row, '-> OK' if (flags & 13) == 13 else '-> STOP')
conn.close()
"
```
Los 3 bits obligatorios deben estar presentes: `(flags_estado & 13) == 13`.
El valor absoluto puede ser mayor por bits acumulados — NO se exige igualdad exacta.
Si no se cumple → STOP.

| Estado | Descripción |
|---|---|
| **NOMINAL** | Canario = 13, rama correcta, working tree limpio |
| **ALERTA** | Funciona pero con deudas técnicas o rama provisional |
| **CRÍTICO** | DB corrupta, canario falla, desincronía total de Git |

Si no es NOMINAL:
1. `python scripts/manager_status.py set 3`
2. Crear bloque `[!CAUTION]` en `INFORME_CIERRE_SESION.md`

---

## FASE 1B — WAL CHECKPOINT (antes de exportar DB al Drive)

Ejecutar SIEMPRE antes de copiar `pilot_v5x.db` al Drive:
```python
python -c "
import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
conn.execute('PRAGMA wal_checkpoint(FULL)')
conn.close()
print('WAL checkpoint OK')
"
```
Si no devuelve `WAL checkpoint OK` → STOP. No exportar.

---

## FASE 1B.2 — ROTACIÓN DE BACKUPS (BACKUPS_DB)

Ejecutar:
```python
python scripts/backup_db.py
```
Rota MAESTRO/DESARROLLO en Q:\Mi unidad\V5_Silo_Claude\BACKUPS_DB\ROTATIVO
según esquema dinámico de cascada (slots 1-3: ventana rodante de últimos
3 días; slot 4: hereda de slot 3 cuando pasaron >=14 días desde su última
actualización o está vacío; slot 5: hereda de slot 4 cuando pasaron >=35
días desde su última actualización o está vacío).

Si falla → [WARN] Error en rotación de backups. No bloquea el cierre.

---

## FASE 1C — ESPEJO EXCEL V2 (Snapshot de Pedidos)

Durante el cierre, el script OMEGA generará automáticamente un Excel Espejo de solo lectura ejecutando:
`python scripts/exportar_pedidos_excel.py` — el entorno (TOM/DEV) se auto-detecta leyendo
`DATABASE_URL` de `.env` (o `current/.env` en B), no se pasa por flag (reconciliación S849,
Card #93-bis). En entorno TOM, el archivo se guarda en `Silo\P\` (la carpeta sigue al dato
de producción, no al código que lo genera — S850).
Esto crea un snapshot histórico de los pedidos que sirve como red de seguridad visual antes del cierre de sesión. Si ocurre un error generando el Excel, OMEGA arrojará un `[WARN] Error generando Espejo Excel`, el cual debe ser reportado.

---

## SELECCIÓN DE PERFIL — COMPLETO / LITE

Antes de ejecutar FASE 2, determinar el perfil de este OMEGA:

```
Leer Bit 19 (`FORZAR_OMEGA_COMPLETO`) en system_flags de esta máquina.
Bit 19 ON  → perfil = Completo (obligatorio). No se reconstruye el criterio por inferencia.
Bit 19 OFF → perfil = Lite (propuesto). Se confirma junto con el PIN 1974 del plan en FASE 3,
             igual que cualquier otro plan bajo REGLA CERO.
```

**Override:** si Bit 19 está ON, Carlos puede igual forzar Lite, pero tiene que decirlo
explícitamente — el bit no se auto-ignora ni se apaga solo por decisión de perfil. Sigue ON
hasta que se ejecute un OMEGA Completo real.

**Qué cambia entre perfiles** (el resto de FASE 2 está anotado inline más abajo):

| Ítem FASE 2 | Completo | Lite |
|---|---|---|
| SESION_NEXT.md | igual | igual — nunca se abrevia |
| BITACORA_VIVA archival | igual | igual — no negociable |
| SISTEMA_STATUS.json + `actualizar_card000.py` | igual | igual — no se abrevia |
| CONTEXTO_CS/ + Bits 16-18 | igual | igual |
| ESTADO_ECOSISTEMA.md | hitos narrativos | solo fila de tabla + una línea de hito |
| Manuales | prosa completa | una línea si no hubo cambio funcional visible; checkbox sigue siendo obligatorio |
| BITACORA_DEV.md | Hito + sub-bullets | una línea por sesión |
| Informe Histórico | narrativo completo (Resumen Ejecutivo → Lecciones Aprendidas) | párrafo + tabla BV — sección DESTILADO CS siempre presente en ambos |
| BANDERAS_ROJAS check | igual | igual |

FASE 1/1B/1B.2/1C, FASE 3-7: **idénticas en ambos perfiles** — seguridad y trazabilidad
nunca se recortan, solo se recorta la prosa discursiva dirigida a lectura humana futura.

---

## FASE 2 — BUROCRACIA Y MESA DE TRABAJO

Regla de Oro: No decir "voy a actualizar". Presentar texto exacto.

- [ ] **SESION_NEXT.md** (`Q:\Mi unidad\V5_Silo_Claude\SESION_NEXT.md`):
  **CHECKBOX OBLIGATORIO** — Sobrescribir con el estado actual de la mesa:
  - Vaciar tareas resueltas
  - Documentar próxima tarea concreta
  - Anotar pendientes Nike
  - Registrar callejones explorados si los hubo

- [ ] **BITACORA_VIVA.md** — 🔴 **CONDICIÓN OBLIGATORIA: OMEGA SIN BV ARCHIVADA NO ES OMEGA COMPLETO**
  1. Verificar que BV refleja todas las tareas de la sesión con agente explícito (CC/Gy/CP/CS/GA).
     Recordatorio: cada 5 filas nuevas debe haber una fila checkpoint:
     `| N | HH:MM | AGENTE | ✅ SAVED | — | D:{hash} P:{hash} |`
  2. Agregar fila de cierre:
     `| N | HH:MM | AGENTE | OMEGA — cierre sesión NNN | ✅ | D=HASH P=HASH |`
  3. Mover contenido completo a `INFORMES_HISTORICOS/YYYY-MM-DD_SNNN_MAQUINA.md`
     > El archivo histórico **ES** la BV de esa sesión — no es un documento separado.
     > Su contenido es la copia fiel e íntegra de BITACORA_VIVA.md de esa sesión.
  4. Dejar BV con solo el bloque de cierre:
     ```
     ## Sesión NNN — YYYY-MM-DD — {máquina} (CERRADA)
     **Archivado en:** INFORMES_HISTORICOS/YYYY-MM-DD_SNNN_MAQUINA.md
     **Estado cierre:** OMEGA NNN completado. D:{hash} P:{hash} GOLD
     ```

- [ ] **CONTEXTO_CS/** — actualizar puntero mínimo:
  1. Confirmar que Bits 16-18 reflejan el semáforo real de cierre de CS (autoevaluación de
     CS, no de CC/Gy).
  2. Regenerar `CONTEXTO_CS/CONTEXTO_CS_{timestamp}.md` (`python scripts/generar_contexto_cs.py`)
     — puntero mínimo, ya no bundle completo.
  3. Escribir la sección `## DESTILADO CS` al final del Informe Histórico de esta sesión
     (ver ítem Informe Histórico abajo) — obligatoria en ambos perfiles, profundidad según
     el semáforo (una línea si VERDE, destilado completo si AMARILLO/ROJO).

- [ ] **SISTEMA_STATUS.json** — actualizar entrada de esta máquina:
  - `omega_cerrado: true`
  - `fecha_ultimo_omega`: hoy
  - `hash_D` y `hash_P`: hashes del commit de cierre
  - `commits_sin_push_D/P`: 0 (tras push exitoso)
  - `system_flags`: encender Bits 60+61+62 (ESPEJO_TOTAL) si las
    4 capas de la Trinidad se actualizaron correctamente.
    Encender Bits de agentes activos (20-25) según quién participó.
    Encender Bit 30 si MT participó en la sesión.
    Bit 26 (`D_SOBERANO`): siempre ON — documentario.
    Bits 27/28 (`B_DIVERGE`/`P_DIVERGE`): recalcular contra `ultimo_hash_D_en_B` /
    `ultimo_hash_B_en_P` (ver FLUJO DE CAMBIOS en ALFA.md); actualizar esos dos campos
    globales si el cierre de este OMEGA incluyó push a B.
    Bit 19 (`FORZAR_OMEGA_COMPLETO`): si este OMEGA es Completo → apagarlo. Si está ON y
    este OMEGA se ejecuta como Lite sin override explícito de Carlos → bloquear el cierre.
  - Ejecutar: `python scripts/actualizar_card000.py`
    (actualiza Card #000 en Board con hash, sesión y semáforo)
    Verificar que el script imprimió la `IDENTIDAD` usada y que coincide con la máquina
    declarada en el header de BV de esta sesión — si no coincide, el script está
    escribiendo sobre la entrada equivocada (ver Informe Histórico S840, hallazgo
    `.gy_identity`); parar y corregir antes de confiar en la escritura.
    Verificar que Card #000 quedó actualizada con el hash del commit
    de cierre. Si el hash en Card #000 no coincide con el commit
    actual → [WARN] Card #000 desactualizada. No bloquea el cierre
    pero debe registrarse en BV.

- [ ] **ESTADO_ECOSISTEMA** (`Q:\Mi unidad\V5_Silo_Claude\ESTADO_ECOSISTEMA.md`):
  - Hash git actual
  - Estado (🟢 OK / 🟡 ATENCIÓN / 🔴 CRÍTICO)
  - Alertas activas
  - **Lite:** solo actualizar la fila de la tabla + una línea en "Últimos hitos". No
    reescribir alertas si no cambiaron esta sesión.

- [ ] **Caja Negra** (`_GY/_MD/CAJA_NEGRA.md`): header + incrementar sesiones

- [ ] **Manuales** (`_GENOMA_DOCS/MANUAL_TECNICO_V5.md` y `MANUAL_OPERATIVO_V5.md`) —
  **CHECKBOX OBLIGATORIO** — Actualizar con los cambios de esta sesión.
  Si no hay cambios que documentar → marcar igual con nota: *"sin cambios esta sesión"*.
  - **Lite:** si no hubo cambio funcional/UX visible al operador, una sola línea
    `"SNNN — sin cambios"` reemplaza la prosa completa. El checkbox sigue siendo
    obligatorio — lo que se recorta es la extensión, no el paso.

- [ ] **Bitácora** (`_GY/_MD/BITACORA_DEV.md`): fecha, título, bullets
  - **Lite:** una línea por sesión, sin sub-bullets de Hito, salvo que haya algo no obvio
    que documentar.

- [ ] **Informe Histórico** (`INFORMES_HISTORICOS/YYYY-MM-DD_TITULO.md`)
  - **Completo:** narrativo completo — Resumen Ejecutivo, desarrollo por card/fix, Decisiones
    tomadas y por qué, Lecciones aprendidas, Estado final, Próxima sesión, Apéndice BV.
  - **Lite:** un párrafo de resumen + tabla BV completa como apéndice. Sin secciones de
    "Decisiones tomadas" ni "Lecciones aprendidas".
  - **Ambos perfiles, sección final obligatoria:** `## DESTILADO CS` (ver CONTEXTO_CS arriba)
    — mismo header siempre, profundidad según semáforo CS.

- [ ] **BANDERAS_ROJAS** — verificar hoja en BOARD_V5.xlsx:
  Si alguna se resolvió en esta sesión → CERRADO + fecha + hash.
  Si hay nuevas → agregarlas antes de cerrar.
  Actualizar `banderas_rojas_activas` en SISTEMA_STATUS.json.
  No cerrar OMEGA con banderas nuevas sin registrarlas.

---

## FASE 3 — PLANIFICACIÓN Y STOP

1. Verificar que NO se operó sobre `pilot_v5x.db` directamente sin PIN
2. Confirmar rama activa: `git branch --show-current`
3. STOP: Presentar plan a Carlos y esperar PIN 1974

---

## FASE 4 — AUDITORÍA DE PESO (ADUANA TÉCNICA)

- Listar archivos > 5MB (excepto `.db` si es intencional)
- PROHIBIDO commit con más de 100 archivos sin autorización explícita
- Límite: repo > 50MB → Push bloqueado

---

## FASE 5 — EJECUCIÓN GIT (solo tras PIN 1974)

### PASO 5A — Control de Sesión
1. Preguntar: "¿Lo que sigue es una NUEVA sesión? (S/N)"
   - **S** → Incrementar número en `_GY/_MD/CAJA_NEGRA.md`
   - **N** → Mantener número actual

### PASO 5B — Rama de Respaldo
Antes del push final:
```cmd
git branch backup/YYYYMMDD_HHMM_cierre
```
Crea una "caja negra" inmutable del estado local exacto.

### PASO 5C — Autorización y Push
El commit de OMEGA **incluye siempre** `BITACORA_VIVA.md` archivada y `SISTEMA_STATUS.json` actualizado.
```cmd
# [PROHIBIDO] git add . — siempre explícito
git add [archivo1] [archivo2] ... OMEGA.md SISTEMA_STATUS.json
git status  # verificar staged antes de commitear
git commit -m "Omega NNN: [Resumen] (PIN 1974)"
git push origin [rama_actual]
```

Ticket de Certificación:
```cmd
git show --name-only HEAD
```

---

## FASE 6 — VERIFICACIÓN DE ÓRBITA (TRUST BUT VERIFY)

Verificación multi-remoto obligatoria (Card #88, S843 — un push parcial es indistinguible
de uno completo si nadie verifica los dos remotos por separado). El cierre solo es válido
si AMBOS remotos están sincronizados.

### PASO 6A — Verificación en D
```cmd
cd C:\dev\Sonido_Liquido_V5
git log origin/main..HEAD --oneline
```
**Resultado esperado:** vacío (sin salida)
- Si está vacío → D sincronizado ✓
- Si hay commits → **DETENER** — existe push pendiente a `origin/main`. Reportar:
  > *"FALLO: D tiene commits sin pushear a origin/main. Ejecutar `git push origin main` antes de cerrar."*

### PASO 6B — Verificación en B
```cmd
cd C:\dev\v5-ls-Tom\current
git log prod/main..HEAD --oneline
```
**Resultado esperado:** vacío (sin salida)
- Si está vacío → B sincronizado ✓
- Si hay commits → **DETENER** — existe push pendiente a `prod/main`. Reportar:
  > *"FALLO: B tiene commits sin pushear a prod/main. Ejecutar `git push prod main` antes de cerrar."*

### PASO 6C — Reporte de Cierre
Solo si ambos pasos 6A y 6B dieron vacío:
```cmd
git log origin/main -n 1 --format="%h - %s"
git log prod/main -n 1 --format="%h - %s"
```
Registrar en BITACORA_VIVA. Reportar **"SESIÓN CLAUSURADA CON ÉXITO"** con hashes de ambos remotos.

---

## FASE 7 — HIGIENE PROFILÁCTICA ANTIGRAVITY (OBLIGATORIA)

Requiere PIN 1974. CIERRE.bat lo solicita automáticamente.

Qué purga: Cache, GPUCache, Code Cache, blob_storage, WebStorage,
           CachedData, shared_proto_db, Network, Service Worker, logs anteriores.
Qué NO toca: User\, Workspaces\, Preferences.

---

*Última actualización: 2026-07-15 — OF*
*Reemplaza: OMEGA.md (V3.2)*
*Versión 3.2 — S841-OF — Perfiles Completo/Lite (Bit 19), Bits 26-28 en actualización de
system_flags, CONTEXTO_CS/ + DESTILADO CS como ítem obligatorio de FASE 2, fix diagnóstico
actualizar_card000.py en verificación.*
*Versión 3.3 — S849/S850-OF — Reconciliación de la copia canónica del Silo con las copias
locales de D y B, que habían divergido en direcciones opuestas (la del Silo tenía todo el
contenido de S841 que D nunca recibió; la de D tenía el fix de FASE 6 de Card #88 que nunca
llegó al Silo). FASE 6 reescrita con verificación multi-remoto (Pasos 6A/6B/6C). FASE 1C
actualizada: entorno auto-detectado sin flag, TOM guarda en Silo\P\.*
