# PROTOCOLO OMEGA V2.2 — El Cierre (D — Sonido_Liquido_V5)

> Protocolo exclusivo para entorno D (desarrollo).
> Para P ver: C:\dev\v5-ls-Tom\OMEGA.md

---

## 🛑 REGLA CERO: EL FRENO DE MANO

Si Carlos indica "Presentar plan SIN ejecutar", ninguna aprobación automática tiene validez.
- Acción: Pausar y solicitar PIN Maestro: 1974
- Cláusula de Hierro: "LGTM", "Proceed" o botones de interfaz NO sustituyen al PIN 1974.
- git add . PROHIBIDO — siempre stagear archivos explícitamente.

---

## FASE 1: AUDITORÍA DE SALUD

Canario obligatorio antes de cerrar:
```
python -c "
import sqlite3
conn = sqlite3.connect('pilot_v5x.db')
cur = conn.cursor()
cur.execute(\"SELECT id, flags_estado FROM clientes WHERE id = 'e1be0585cd3443efa33204d00e199c4e'\")
print(cur.fetchone())
conn.close()
"
```
→ Debe devolver flags_estado = 13. Si no → STOP.

| Estado | Descripción |
|---|---|
| **NOMINAL** | Canario = 13, rama correcta, working tree limpio |
| **ALERTA** | Funciona pero con deudas técnicas o rama provisional |
| **CRÍTICO** | DB corrupta, canario falla, desincronía total de Git |

Si no es NOMINAL:
1. Ejecutar `python scripts/manager_status.py set 3`
2. Crear bloque `[!CAUTION]` en `INFORME_CIERRE_SESION.md`

---

## FASE 2: BUROCRACIA (OBLIGATORIA)

Regla de Oro: No decir "voy a actualizar". Presentar texto exacto.

- [ ] **Caja Negra** (`_GY/_MD/CAJA_NEGRA.md`): header + incrementar sesiones
- [ ] **Manuales** (`_GENOMA_DOCS/MANUAL_TECNICO_V5.md` y `MANUAL_OPERATIVO_V5.md`)
- [ ] **Bitácora** (`_GY/_MD/BITACORA_DEV.md`): fecha, título, bullets
- [ ] **Informe Histórico** (`INFORMES_HISTORICOS/YYYY-MM-DD_TITULO.md`)

---

## FASE 3: PLANIFICACIÓN Y STOP

1. Verificar que NO se operó sobre `pilot_v5x.db` directamente sin PIN
2. Confirmar rama activa: `git branch --show-current`
3. STOP: Presentar plan a Carlos y esperar PIN 1974

---

## FASE 4: AUDITORÍA DE PESO (ADUANA TÉCNICA)

- Listar archivos > 5MB (excepto `.db` si es intencional)
- PROHIBIDO commit con más de 100 archivos sin autorización explícita
- Ejecutar `python audit_v5.py`
- Límite: repo > 50MB → Push bloqueado

---

## FASE 5: EJECUCIÓN GIT (solo tras PIN 1974)

```cmd
# NUNCA git add . — siempre explícito
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

## FASE 6: VERIFICACIÓN DE ÓRBITA (TRUST BUT VERIFY)

PROHIBIDO reportar éxito sin verificar:
```cmd
git log origin/[RAMA_ACTIVA] -n 1 --format="%h - %s"
git rev-parse HEAD
```
Los hashes DEBEN coincidir. Si no → reportar "FALLO DE SINCRONIZACIÓN".

---

## FASE 7: HIGIENE PROFILÁCTICA ANTIGRAVITY (OBLIGATORIA)

Requiere PIN 1974. CIERRE.bat lo solicita automáticamente.

Qué purga: Cache, GPUCache, Code Cache, blob_storage, WebStorage,
           CachedData, shared_proto_db, Network, Service Worker, logs\ anteriores.
Qué NO toca: User\, Workspaces\, Preferences.

---

*Última actualización: 2026-05-04 — Sonnet + Claude Code (CA)*
