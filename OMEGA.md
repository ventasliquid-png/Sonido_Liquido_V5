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

## FASE 5: EJECUCIÓN GIT (solo tras PIN 1974)

```cmd
git add .
git status
git commit -m "Omega: [Resumen de Misión] (PIN 1974)"
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

*Última actualización: 2026-03-31 — OF*
