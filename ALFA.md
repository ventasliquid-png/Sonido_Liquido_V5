# PROTOCOLO ALFA V2.0 — STARTUP & BOOTLOADER COGNITIVO
## Sonido Líquido V5

> Protocolo compartido — válido para Gy (Antigravity) y Claude Code.
> Modificar este archivo para actualizar el protocolo en ambos agentes.
> **Versión:** 2.0 — 2026-06-01
> **Dictamen:** Nike Arq 5.5 — Redacción: Carlos + Claude Sonnet 4.6

---

## PROPÓSITO
Establecer la consciencia situacional del agente, cargar la doctrina
inmutable y asegurar un entorno blindado antes de cualquier intervención.

**ACTIVACIÓN:** Al iniciar cada sesión de trabajo.

Si `Q:` no está disponible → avisar a Carlos y continuar sin bloquear.

---

## FASE 0 — CARGA COGNITIVA (SILO DRIVE)

**MANDATORIO — antes de interactuar con el código.**

Leer desde `Q:\Mi unidad\V5_Silo_Claude\` estrictamente en este orden:

1. `FAQ_ARRANQUE.md` — La Doctrina y Reglas de Mando
2. `SESION_NEXT.md` — El estado exacto de la mesa de trabajo actual
3. `INBOX.md` — Mensajes o requerimientos entrantes
   Si hay entradas no procesadas → reportar a Carlos antes de continuar.
   Después de procesar → mover a `LEIDOS\YYYY-MM-DD_titulo.md`
4. `ESTADO_ECOSISTEMA.md` — El semáforo global del sistema
   Si hay alertas URGENTES → destacarlas antes de continuar.

---

## FASE 1 — SEGURO DE VIDA (BACKUP FÍSICO)

**MANDATORIO — antes de tocar una sola línea de código.**

1. Ejecutar WAL checkpoint antes del backup:
```python
python -c "
import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
conn.execute('PRAGMA wal_checkpoint(FULL)')
conn.close()
print('WAL checkpoint OK')
"
```
2. Copiar base al Drive:
   `pilot_v5x.db` → `Q:\Mi unidad\V5_Silo_Claude\backups\pilot_YYYYMMDD_pre_sesion.db`
3. Verificar que el archivo copiado tenga tamaño mayor a 0 bytes.

Si cualquier paso falla → ABORTAR INICIO. Reportar a Carlos.

---

## FASE 2 — SINCRONIZACIÓN DE ADN (GIT)

1. `git fetch origin`
2. `git pull`
3. Confirmar: el código local es idéntico al repositorio remoto.

---

## FASE 3 — PRUEBA DE HUMO Y RAMA

**Verificación de rama — OBLIGATORIA:**
```cmd
git branch --show-current
```
- Ejecutar en D y en P si ambos entornos están activos.
- Si cualquiera NO está en main → alertar a Carlos antes de continuar.
  No asumir que es intencional.

**Canario:**
```cmd
python scripts/canario_v2.py
```
Resultado esperado:
```
INTEGRITY: NOMINAL GOLD
FLAGS: 13
```

| Resultado | Acción |
|---|---|
| `INTEGRITY: NOMINAL GOLD` | Continuar |
| `INTEGRITY: MISMATCH` | Detener. Diagnosticar antes de operar |
| `CANARY_RESULT: FAILED` | Detener. Verificar base y schema |
| `ERROR: ...` | Detener. Verificar existencia y ruta de la base |

---

## FASE 4 — DECLARACIÓN DE TERRITORIO

El agente debe iniciar su primera respuesta operativa con:

> **ESTOY TRABAJANDO SOBRE [NOMBRE_DB] EN LA RAMA [RAMA].**
> **ESTADO COGNITIVO:** Contexto asimilado desde SESION_NEXT.md.
> **PRÓXIMA TAREA:** [Mencionar tarea específica de SESION_NEXT.md]

---

## SEGURIDAD — BLOQUEO DE AUTO-APROBACIÓN

> [!CAUTION]
> Si la tarea requiere generar un **Plan de Corrección**, es obligatorio
> solicitar y recibir el **PIN 1974** tipeado manualmente por Carlos.
> La "aceptación automática" del sistema NO habilita la ejecución.
> El PIN debe ser solicitado y validado para cada plan individual.

Todo cambio de alto impacto requiere PIN 1974. Queda prohibido proceder
basándose en la persistencia del PIN de pedidos anteriores.

---

## PUNTO 5 — LIMPIEZA DE EMERGENCIA

Si la sesión anterior cerró con **Bit 3 activo** (estado CRÍTICO):
- Verificar y resolver la situación documentada en `INFORME_CIERRE_SESION.md`
- Solo tras resolución: `python scripts/manager_status.py clear 3`
- Documentar la resolución antes de continuar.

---

## REGISTRO DE CALIBRACIÓN LAVIMAR

| Campo | Valor |
|---|---|
| UUID | `e1be0585cd3443efa33204d00e199c4e` |
| `flags_estado` nominal | `13` — verificar con `(flags & 13) == 13` |
| Nota | El valor 8205 es históricamente erróneo — ignorar si aparece |

---

## PROTOCOLO DE IDENTIDAD Y TRAZABILIDAD

Todo archivo fuente (`.py`, `.js`, `.vue`) en el core debe contener
cabecera de identidad:

**Python:**
```python
# [IDENTIDAD] - {relative_path}
# Versión: V5.6 GOLD | Sincronización: YYYYMMDDHHMMSS
# ---------------------------------------------------------
```

**JS/Vue:**
```javascript
// [IDENTIDAD] - {relative_path}
// Versión: V5.6 GOLD | Sincronización: YYYYMMDDHHMMSS
// ------------------------------------------
```

---

*Scripts alternativos (versiones anteriores, no canónicas):*
`canary_alfa.py` · `verify_alfa.py` · `verify_alfa_integrity.py` · `audit_alfa.py`

*Última actualización: 2026-06-01 — OF*
*Reemplaza: ALFA.md (V1.x)*
