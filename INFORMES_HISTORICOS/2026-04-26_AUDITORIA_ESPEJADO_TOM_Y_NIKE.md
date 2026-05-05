# Informe de Misión: Auditoría de Espejo Soberano y Habilitación de Tom
**Fecha**: 2026-04-26  
**Estado**: ALERTA (Tom operativo con deuda técnica pendiente — ver Sección 6)  
**Autor**: Claude Code (Sonnet 4.6) — consultoría, diagnóstico, ejecución parcial  
**Operador**: Carlos (CA — Casa)

---

## LECTURA OBLIGATORIA AL DESPERTAR

**Si estás leyendo esto desde el DESPERTAR de mañana en OF:**

1. D (este repo) tiene **cambios sin commitear desde el 25/04** (scripts de higiene de Antigravity: check_health.ps1, purgar_gy.ps1, CIERRE.ps1, DESPERTAR.ps1, OMEGA.md). Están listos para commit pero Carlos quiso revisarlos en OF antes de pushear.

2. Tom (`C:\dev\v5-ls-Tom`) fue espejado parcialmente esta noche desde D. Los cambios están commiteados en el repo `v5-ls-Tom` en GitHub. **Tom está funcional pero tiene una deuda técnica importante** (ver Sección 6).

3. **La tarea de mañana es**: Pisar P con D completamente (sincronización total, no el espejado quirúrgico de hoy). La metodología correcta está en la Sección 7.

---

## 1. Contexto y Motivo de la Sesión

El informe de auditoría de Gy (Canario V2.0) detectó **4 archivos divergentes** entre D y Tom (P). El origen del trabajo era sincronizar esos 4 archivos. En el proceso se descubrió que la divergencia era más profunda: Tom está en commit del **19 de abril**, D en commit del **24 de abril** — 5 días de diferencia en repos Git separados (`ventasliquid-png/Sonido_Liquido_V5` vs `ventasliquid-png/v5-ls-Tom`).

---

## 2. Diagnóstico Inicial — Informe de Auditoría de Gy

El informe de Gy fue evaluado punto por punto:

| Punto | Veredicto |
|---|---|
| Protocolo ALFA (Canario) | Correcto. NOMINAL GOLD, flags 8205, UUID LAVIMAR OK |
| Mirror D↔P (4 archivos) | Correcto. Divergencia real confirmada |
| Estado Git (cambios sueltos) | Correcto al 100% |
| **ORM Vinculo (NameError)** | **Diagnóstico ERRADO** |

**El bug de Vinculo:** Gy atribuyó el error a violación de Regla Crítica 3. La causa real era más simple: `scripts/chk_dups.py` no importaba `backend.contactos.models`, por lo que `Vinculo` no estaba en el registry de SQLAlchemy cuando el script corría. El modelo (`models.py`) ya cumplía Regla Crítica 3 correctamente. La fix fue agregar una línea de import al script, no tocar los modelos. Tom fue espejado con la misma fix.

---

## 3. Trabajo Realizado en Tom Esta Noche

### Espejado de los 4 archivos originales (Gy con supervisión Claude):
- **Acción 1** — `database.py` Tom: Inyección de WAL mode enforcement (9 líneas). El resto del archivo NO fue tocado (la lógica de DATABASE_URL hardcodeada a V5_LS_MASTER.db es intencional para P).
- **Acción 2** — `main.py` Tom: Bloque `configure_mappers()` explícito con try/except (V14.12 GOLD). Módulo de facturación NO incluido (no existe en Tom).
- **Acción 3** — `service.py` Tom: Espejado completo desde D. Incluye Protocolo Nike (blindaje duplicados por CUIT + clave canónica + fuzzy matching), `normalize_name`, `check_similarity`, hidratación flags Bit 21.
- **Acción 4** — `ClientCanvas.vue` Tom: Espejado completo desde D. Incluye UI del Protocolo Nike, motor de Deshacer Híbrido (useFormHistory), debounce lodash.

### Fixes adicionales necesarios (no estaban en el espejado original):
- **`useFormHistory.js`** Tom: Bug `TypeError: Converting circular structure to JSON`. Fix en 3 iteraciones: `toRaw()` shallow → `deepToRaw()` sin WeakSet → `deepToRaw()` con WeakSet + `isRef()` + filtro `__v_*`. Fix definitivo: desnuda recursivamente todos los Proxies Vue 3 anidados con detección de ciclos.
- **`Login.vue`** Tom: Puerto 8000 hardcodeado en la URL de auth. Fix: URL relativa `/auth/token`.
- **`backend/clientes/router.py`** Tom: Faltaba el endpoint `GET /check-similarity`. Agregado.
- **`frontend/src/services/clientes.js`** Tom: Faltaba la función `checkSimilarity`. Agregada.
- **`backend/clientes/models.py`** Tom: Faltaba el campo `razon_social_canon` en el ORM `Cliente`. Agregado. Nota: el campo YA existía en la DB (V5_LS_MASTER.db) pero no estaba mapeado en la clase.

### Nota sobre `checkSimilarity` en D:
D tampoco tiene `checkSimilarity` en `frontend/src/services/clientes.js`. Solo lo tiene Tom (que lo recibió esta noche). Cuando se haga el sync completo D→Tom, este método deberá preservarse en Tom o también agregarse en D.

---

## 4. Estado del Protocolo Nike en Tom al Cierre

- Formulario "Nuevo Cliente": **CARGA SIN CRASH** ✅ (useFormHistory fix aplicado)
- Login con admin/admin123: **FUNCIONAL** ✅ (Login.vue fix aplicado)
- Panel de similarity warnings: **NO VERIFICADO** — el servidor necesitaba reiniciarse para tomar el cambio de `models.py` (campo `razon_social_canon`). La lógica fue verificada en Python directo y retorna LAVIMAR con score 1.0 correctamente. Faltó el reinicio del servidor de Tom al cierre de sesión.

---

## 5. Arquitectura D-P (para recordar)

| Entorno | Directorio | Repo GitHub | Puertos | Último commit antes de hoy |
|---|---|---|---|---|
| D (Desarrollo) | `C:\dev\Sonido_Liquido_V5` | `ventasliquid-png/Sonido_Liquido_V5` | 5173/8080 | 2026-04-24 |
| P (Tom/Producción) | `C:\dev\v5-ls-Tom` | `ventasliquid-png/v5-ls-Tom` | 5174/8090 | 2026-04-19 (antes) / 2026-04-26 (después de hoy) |

**Topología física:** D y P son máquinas físicas distintas en la Oficina (OF), conectadas por cable LAN. El directorio `C:\dev\v5-ls-Tom` en D contiene el código de P. Los cambios se sincronizan via Git. P corre como SATELITE_TOMY. D dispara primero como Soberana.

---

## 6. Deuda Técnica Pendiente (CRÍTICO para mañana)

**El espejado de esta noche fue quirúrgico pero incompleto.** Tom está en commit del 19/04 y D en el 24/04. Hay 5 días de commits de D que Tom no tiene. El mirror_audit solo detectó los 4 archivos más visibles. Probablemente hay más diferencias.

**Lo que encontramos que faltaba (y no era parte de los 4 archivos del mirror_audit):**
- `models.py` → `razon_social_canon` ausente en ORM de Tom
- `router.py` → endpoint `check-similarity` ausente
- `services/clientes.js` → función `checkSimilarity` ausente
- `Login.vue` → puerto hardcodeado a 8000

Esto sugiere que el mirror_audit fue incompleto o hubo cambios en D posteriores al último sync.

---

## 7. Tarea de Mañana: Sync Total D→Tom (metodología correcta)

**NO hacer espejado archivo por archivo.** Hacer un diff completo:

```bash
# Listar todos los archivos que difieren entre D y Tom
# (excluyendo DB, static/, node_modules, .git)
diff -rq \
  --exclude="*.db" --exclude="*.bak" --exclude=".pasaporte*" \
  --exclude="node_modules" --exclude="static" --exclude="dist" \
  C:/dev/Sonido_Liquido_V5/backend \
  C:/dev/v5-ls-Tom/backend
```

Luego evaluar archivo por archivo qué va a Tom y qué no (algunos archivos de Tom tienen configuraciones de P que NO se pisan, como `database.py` y el bloque de DATABASE_URL en `main.py`).

**Archivos que NUNCA se pisan de D→Tom:**
- `backend/core/database.py` — tiene DATABASE_URL hardcodeada a V5_LS_MASTER.db
- `backend/main.py` completo — tiene path absoluto a MASTER. Solo se cherry-pickean mejoras puntuales.
- `.env` de Tom — configuración de entorno P

---

## 8. Manuales y Caja Negra

Sin cambios arquitectónicos en D esta sesión. La sesión de hoy operó exclusivamente sobre Tom. Los manuales técnicos de D no requieren actualización.

---

**Sello de Cierre**: Protocolo OMEGA Tom ejecutado. PIN 1974.  
**Redactado por**: Claude Code (Sonnet 4.6) — mensaje para la próxima sesión.
