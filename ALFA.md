# PROTOCOLO ALFA: ADN CANARIO V2.0 (V5.5)

> Protocolo compartido — válido para Gy (Antigravity) y Claude Code.
> Modificar este archivo para actualizar el protocolo en ambos agentes.

---

## Propósito
Verificar integridad del sistema antes de comenzar cualquier sesión de trabajo.
**El ALFA no es texto, es ejecución.** Si el Canario falla, no se opera.

---

## Ejecución

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

*Scripts alternativos (versiones anteriores, no canónicas):*
`canary_alfa.py` · `verify_alfa.py` · `verify_alfa_integrity.py` · `audit_alfa.py`

---

*Última actualización: 2026-03-31 — OF*
