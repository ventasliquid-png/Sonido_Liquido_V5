# PROTOCOLO OMEGA V2.1 — El Cierre

> Protocolo compartido — válido para Gy (Antigravity) y Claude Code.
> Modificar este archivo para actualizar el protocolo en ambos agentes.

---

## 🛑 REGLA CERO: EL FRENO DE MANO

Si Carlos indica "Presentar plan SIN ejecutar", ninguna aprobación automática del sistema tiene validez.
- **Acción:** Pausar y solicitar el **PIN Maestro: 1974**
- **Cláusula de Hierro:** "LGTM", "Proceed" o botones de aprobación de interfaz **NO sustituyen** al PIN 1974. Rechazar aprobación genérica y volver a pedir el código numérico.

---

## FASE 1: AUDITORÍA DE SALUD

Declarar el estado del sistema antes de cerrar:

| Estado | Descripción |
|---|---|
| **NOMINAL** | Todo funciona, rama correcta, tests pasados |
| **ALERTA** | Funciona pero con deudas técnicas o rama provisional |
| **CRÍTICO (Catatónico)** | Nada funciona, DB corrupta o desincronía total de Git |

Si el estado **no es NOMINAL**:
1. Ejecutar `python scripts/manager_status.py set 3` (activa Bit CRÍTICO)
2. Crear bloque `> [!CAUTION]` al inicio de `INFORME_CIERRE_SESION.md` detallando el problema

---

## FASE 2: BUROCRACIA (OBLIGATORIA)

Antes de tocar Git:

- [ ] **Caja Negra** (`_GY/_MD/CAJA_NEGRA.md`): Actualizar header + incrementar sesiones completadas
- [ ] **Manuales** (`MANUAL_TECNICO_V5.md` / `MANUAL_OPERATIVO_V5.md`): Reflejar cambios de lógica, arquitectura o UI. Si no hubo cambios, indicarlo explícitamente.
- [ ] **Bitácora** (`_GY/_MD/BITACORA_DEV.md`): Log de cierre con fecha, título y bullets de lo logrado
- [ ] **Informe Histórico** (`INFORMES_HISTORICOS/YYYY-MM-DD_TITULO.md`): Narrar la sesión — Objetivo, Intervenciones, Métricas, Conclusión. Leer últimos 4 informes antes de redactar.

**Regla de Oro Documental:** No decir "voy a actualizar". Presentar el texto exacto (borrador) que se planea insertar.

---

## FASE 3: PLANIFICACIÓN Y STOP

1. Generar `implementation_plan.md`
2. **Verificación 4 bytes:** Si se crearon módulos o tablas nuevas, confirmar que incluyen `flags_estado`
3. Confirmar que NO se operó sobre `pilot.db` o `main.py` directamente
4. **STOP:** Presentar el plan a Carlos y esperar el **PIN Maestro 1974**

---

## FASE 4: AUDITORÍA DE PESO (ADUANA TÉCNICA)

Antes del push:
- Listar archivos > 5MB (excepto `.db` si es intencional)
- Verificar `.gitignore` — no subir binarios pesados por error
- **Regla de Oro (Límite 100):** PROHIBIDO commit con más de 100 archivos sin autorización explícita
- **Ojo de Halcón:** Ejecutar `python audit_v5.py`. Si reporta discrepancias → sesión BLOQUEADA. Corregir antes de continuar.
- **Límite de peso:** Si el repo supera 50MB → Push bloqueado. Ejecutar purga antes de cerrar.

---

## FASE 5: EJECUCIÓN TÉCNICA (solo tras PIN 1974)

1. **Sello de Pasaporte y Polizón**: Generar snapshot de la DB activa y actualizar metadatos.
```powershell
Copy-Item [db_activa] POLIZON_MAESTRO.bak -Force
$pasaporte = @{ origen = $env:COMPUTERNAME; fecha = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'); estado = '[ESTADO_FASE1]' }
$pasaporte | ConvertTo-Json | Set-Content -Path '.pasaporte_v5.json' -Encoding UTF8
```

2. **Commit y Push**:
```cmd
git add .
git status
git commit -m "Omega: [Resumen] (PIN 1974)"
git push origin [rama_actual]
```

**Ticket de Certificación (obligatorio):**
```cmd
git show --name-only HEAD
```

---

## FASE 6: VERIFICACIÓN DE ÓRBITA (TRUST BUT VERIFY)

PROHIBIDO reportar éxito sin verificar:

```cmd
git log origin/[RAMA_ACTIVA] -n 1 --format="%h - %s"
git rev-parse HEAD
```

Los hashes DEBEN coincidir. Si no coinciden → reportar "FALLO DE SINCRONIZACIÓN" y no cerrar la sesión.

---

## Nota sobre el Bit 3 (Estado Crítico)

Si se activa el Bit 3 al cerrar, la limpieza es responsabilidad del próximo agente en el **Punto 5 del Protocolo ALFA**, una vez verificado el retorno a la normalidad.

---

## FASE 7: HIGIENE PROFILÁCTICA DE ANTIGRAVITY (OBLIGATORIA)

**Contexto:** Antigravity acumula archivos transitorios (Cache, GPUCache, logs de sesión, blob_storage, etc.) que NO se limpian automáticamente. La acumulación sostenida degrada el canal IPC entre el servidor Go y Electron, aumentando el riesgo del bug crítico `state syncing error: key not found` que causa bloqueo total del agente.

**Acción al cierre — requiere PIN 1974 para ejecutarse:**

`CIERRE.bat` lo solicita automáticamente en el paso 6. Si no ingresás el PIN, la purga se omite y Antigravity conserva el contexto de sesión para repreguntas posteriores.

> ⚠️ **Regla:** Solo ingresá el PIN 1974 cuando estés **seguro** de que no vas a volver a consultar a Gy en esta jornada. Si purgás y después necesitás contexto, Gy no va a recordar nada de la sesión.

**Qué purga:**
- `Cache`, `GPUCache`, `Code Cache` — caché de renderizado y red
- `blob_storage`, `WebStorage`, `CachedData` — almacenamiento transitorio de sesión
- `shared_proto_db`, `Network`, `Service Worker` — bases LevelDB y workers
- `logs\` — sesiones anteriores al día actual (conserva los logs de hoy)

**Qué NO toca:**
- `User\` — configuración y settings del usuario
- `Workspaces\` — historial de conversaciones
- `Preferences` — configuración del IDE

**Si Antigravity está corriendo:** el script avisa y purga lo que no esté bloqueado. Para purga completa, cerrar Antigravity primero.

---

*Última actualización: 2026-04-25 — Claude Code (Haiku 4.5) + Gy*
