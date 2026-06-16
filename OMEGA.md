# PROTOCOLO OMEGA V3.0 — CIERRE Y PERSISTENCIA DE ESTADO
## Sonido Líquido V5 — Entorno D (Sonido_Liquido_V5)

> Protocolo exclusivo para entorno D (desarrollo).
> Para P ver: C:\dev\v5-ls-Tom\OMEGA.md
> **Versión:** 3.0 — 2026-06-01
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
`python scripts/exportar_pedidos_excel.py --entorno D` (o P según corresponda).
Esto crea un snapshot histórico de los pedidos que sirve como red de seguridad visual antes del cierre de sesión. Si ocurre un error generando el Excel, OMEGA arrojará un `[WARN] Error generando Espejo Excel`, el cual debe ser reportado.

---

## FASE 2 — BUROCRACIA Y MESA DE TRABAJO

Regla de Oro: No decir "voy a actualizar". Presentar texto exacto.

- [ ] **SESION_NEXT.md** (`Q:\Mi unidad\V5_Silo_Claude\SESION_NEXT.md`):
  **CHECKBOX OBLIGATORIO** — Sobrescribir con el estado actual de la mesa:
  - Vaciar tareas resueltas
  - Documentar próxima tarea concreta
  - Anotar pendientes Nike
  - Registrar callejones explorados si los hubo

- [ ] **BITACORA_VIVA.md** — agregar fila de cierre:
  `| N | HH:MM | CC | OMEGA — cierre sesión NNN | ✅ | D=HASH P=HASH |`
  Luego mover a `INFORMES_HISTORICOS/YYYY-MM-DD_SNNN_MAQUINA.md`
  y crear archivo vacío con header para próxima sesión.

- [ ] **SISTEMA_STATUS.json** — actualizar entrada de esta máquina:
  - `omega_cerrado: true`
  - `fecha_ultimo_omega`: hoy
  - `hash_D` y `hash_P`: hashes del commit de cierre
  - `commits_sin_push_D/P`: 0 (tras push exitoso)
  - `system_flags`: encender Bits 60+61+62 (ESPEJO_TOTAL) si las
    4 capas de la Trinidad se actualizaron correctamente.
    Encender Bits de agentes activos (20-25) según quién participó.
    Encender Bit 30 si MT participó en la sesión.
  - Ejecutar: `python scripts/actualizar_card000.py`
    (actualiza Card #000 en Board con hash, sesión y semáforo)

- [ ] **ESTADO_ECOSISTEMA** (`Q:\Mi unidad\V5_Silo_Claude\ESTADO_ECOSISTEMA.md`):
  - Hash git actual
  - Estado (🟢 OK / 🟡 ATENCIÓN / 🔴 CRÍTICO)
  - Alertas activas

- [ ] **Caja Negra** (`_GY/_MD/CAJA_NEGRA.md`): header + incrementar sesiones

- [ ] **Manuales** (`_GENOMA_DOCS/MANUAL_TECNICO_V5.md` y `MANUAL_OPERATIVO_V5.md`)

- [ ] **Bitácora** (`_GY/_MD/BITACORA_DEV.md`): fecha, título, bullets

- [ ] **Informe Histórico** (`INFORMES_HISTORICOS/YYYY-MM-DD_TITULO.md`)

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
```cmd
# [PROHIBIDO] git add . — siempre explícito
git add [archivo1] [archivo2] ...
git status  # verificar staged antes de commitear
git commit -m "Omega: [Resumen] (PIN 1974)"
git push origin [rama_actual]
```

Ticket de Certificación:
```cmd
git show --name-only HEAD
```

---

## FASE 6 — VERIFICACIÓN DE ÓRBITA (TRUST BUT VERIFY)

PROHIBIDO reportar éxito sin verificar:
```cmd
git log origin/[RAMA_ACTIVA] -n 1 --format="%h - %s"
git rev-parse HEAD
```
Los hashes DEBEN coincidir.
- Coinciden → reportar **"SESIÓN CLAUSURADA CON ÉXITO"**
- No coinciden → reportar **"FALLO DE SINCRONIZACIÓN"** de inmediato.

---

## FASE 7 — HIGIENE PROFILÁCTICA ANTIGRAVITY (OBLIGATORIA)

Requiere PIN 1974. CIERRE.bat lo solicita automáticamente.

Qué purga: Cache, GPUCache, Code Cache, blob_storage, WebStorage,
           CachedData, shared_proto_db, Network, Service Worker, logs anteriores.
Qué NO toca: User\, Workspaces\, Preferences.

---

*Última actualización: 2026-06-01 — OF*
*Reemplaza: OMEGA.md (V2.2)*
