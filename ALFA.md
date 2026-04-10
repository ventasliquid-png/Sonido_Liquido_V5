# PROTOCOLO ALFA: ADN CANARIO V2.0 (V5.5)

> Protocolo compartido — válido para Gy (Antigravity) y Claude Code.
> Modificar este archivo para actualizar el protocolo en ambos agentes.

---

## Propósito
Verificar integridad del sistema antes de comenzar cualquier sesión de trabajo.
**El ALFA no es texto, es ejecución.** Si el Canario falla, no se opera.

---

## Ejecución (ALFA Fast-Track vs Canario)

**1. Vía Rápida (ALFA-LITE):** Evalúa el pedido. Si es un ajuste de frontend, corrección local, o bugfix acotado, **omite el protocolo Canario**. 
> [!CAUTION]
> **SEGURIDAD**: Si la tarea requiere generar un **Plan de Corrección** (Implementation Plan), es obligatorio solicitar y validar el **PIN 1974** antes de la ejecución, incluso en modo LITE. La "aceptación automática" del sistema no es válida para estos casos.

**2. ALFA Completo:** Se ejecuta el Canario si el pedido involucra cambios de base de datos, arquitectura, o si se pide explícitamente "ALFA COMPLETO".
> [!IMPORTANT]
> **SEGURIDAD**: Todo **Cambio de Base de Datos**, refactorización estructural o plan de alto impacto requiere obligatoriamente el **PIN 1974**. Prohibido proceder mediante autorización automática del sistema.

```cmd
python scripts/canario_v2.py
```

### El Canario verifica:
1. ¿Existe la base de datos? ¿Tiene el schema correcto?
2. ¿Existe el registro LAVIMAR (UUID de calibración)?
3. ¿`flags_estado` de LAVIMAR tiene el valor nominal?

### Resultado esperado:
```
INTEGRITY: NOMINAL GOLD
FLAGS: 8205
```

---

## Registro de Calibración LAVIMAR

| Campo | Valor |
|---|---|
| UUID | `e1be0585cd3443efa33204d00e199c4e` |
| `flags_estado` nominal (V15) | `8205` |
| `flags_estado` legacy (V14) | `13` ← no usar como referencia en V15 |

---

## Estados posibles del Canario

| Resultado | Acción |
|---|---|
| `INTEGRITY: NOMINAL GOLD` | Continuar con la sesión |
| `INTEGRITY: MISMATCH` | Detener. Diagnosticar `flags_estado` antes de operar |
| `CANARY_RESULT: FAILED` | Detener. Verificar base de datos y schema |
| `ERROR: ...` | Detener. Verificar existencia y ruta de la base |

---

## Punto 5 del ALFA (Limpieza de Emergencia)
Si la sesión anterior cerró con **Bit 3 activo** (estado CRÍTICO/CATATÓNICO):
- Verificar y resolver la situación de emergencia documentada en `INFORME_CIERRE_SESION.md`
- Solo tras resolución, limpiar el Bit 3: `python scripts/manager_status.py clear 3`
- Documentar la resolución antes de continuar

---

---

## Protocolo de Seguridad y Autorización (MANDATORIO)

Cualquier plan que implique acciones de **limpieza, refactorización, eliminación de datos o cambios estructurales profundos** requiere validación humana explícita.

1. **PROHIBICIÓN**: No se permite avanzar basándose en "autorización automática" del sistema.
2. **PIN DE VALIDACIÓN**: El agente debe solicitar y el usuario debe proveer el **PIN 1974** para autorizar la ejecución del plan.
3. **REGISTRO**: La autorización debe quedar plasmada en la bitácora o en el reporte de la sesión vinculado al PIN.

---

## Protocolo de Identidad y Trazabilidad (V5.6 GOLD)

Todo archivo fuente (`.py`, `.js`, `.vue`) en el core debe contener una cabecera de identidad con el siguiente formato:

- **Python**: 
  ```python
  # [IDENTIDAD] - {relative_path}
  # Versión: V5.6 GOLD | Sincronización: YYYYMMDDHHMMSS
  # ---------------------------------------------------------
  ```
- **JS/Vue**:
  ```javascript
  // [IDENTIDAD] - {relative_path}
  // Versión: V5.6 GOLD | Sincronización: YYYYMMDDHHMMSS
  // ------------------------------------------
  ```

Este protocolo asegura que el agente sepa exactamente qué archivo está editando y su versión de sincronización respecto a la última auditoría de Soberanía.

---

*Scripts alternativos (versiones anteriores, no canónicas):*
`canary_alfa.py` · `verify_alfa.py` · `verify_alfa_integrity.py` · `audit_alfa.py`

---

*Última actualización: 2026-03-31 — OF*
