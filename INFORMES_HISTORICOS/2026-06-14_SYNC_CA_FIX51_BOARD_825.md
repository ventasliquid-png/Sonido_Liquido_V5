# Informe de Sesión 825 CA: Sync Git + Fix #51 STATE_MASK + Board #60-70

## Resumen Ejecutivo
Sesión de mantenimiento completa ejecutada en CA (Casa). Cuatro hitos principales: (1) sincronización git de D y P en CA mediante ALFA V2.0 con resolución quirúrgica de conflictos, (2) fix quirúrgico Card #51 — bug latente de estados mutuamente excluyentes en migración de pedidos, (3) higiene de documentos ALFA.md fuera del tracking git, (4) actualización extensiva del BOARD_V5.xlsx con 11 cards nuevas (#60-#70).

---

## 1. Sincronización Git CA — ALFA V2.0

### D (Sonido_Liquido_V5)
- Pull limpio desde origin. Sin conflictos.
- Hash base de trabajo: b2557445 (último OMEGA 824).

### P (v5-ls-Tom)
- Conflictos en stash pop: el remote había eliminado del índice todos los archivos `.pyc`, `.env`, `cantera.db` y `V5_LS_MASTER.db` en commit 27190c0 ("cleanup: remove tracked binaries and env").
- Causa: `git stash pop` intentó restaurar esos archivos como modificados, pero el índice remoto ya no los trackeaba → conflictos modify/delete.
- Resolución: `git rm --cached -r` en 7 directorios `__pycache__`, más `backend/data/cantera.db`, `.env`, `"../data/V5_LS_MASTER.db"`. Los archivos permanecieron en disco (datos locales CA preservados).
- `git stash drop` post-resolución. Pull completado. P actualizado.

**Nota técnica:** La ruta de `V5_LS_MASTER.db` requirió `"../data/V5_LS_MASTER.db"` porque el root git de P es un nivel arriba del directorio `current/` donde se trabaja.

---

## 2. Fix Quirúrgico — Card #51 (ES_FIRME|ES_ANULADO simultáneos)

### El Bug
`backend/pedidos/router.py:266` — migración quirúrgica (path cuando Ingesta detecta discrepancia con pedido existente del mismo día):

```python
# ANTES (BUG):
pedido_viejo.flags_estado = (pedido_viejo.flags_estado or 0) | PF.ES_ANULADO.value
```

Si `pedido_viejo` tenía `ES_FIRME` activo (Bit 33), la operación `|=` sumaba `ES_ANULADO` (Bit 35) sin limpiar primero la máscara de estados mutuamente excluyentes. Resultado: pedido con `ES_FIRME|ES_ANULADO` simultáneos — aparecía en filtros de ambos estados.

### La Corrección

```python
# DESPUÉS (FIX):
pedido_viejo.flags_estado = ((pedido_viejo.flags_estado or 0) & ~STATE_MASK.value) | PF.ES_ANULADO.value
```

`STATE_MASK` está importado en línea 19 del mismo módulo: `from backend.pedidos.constants import PedidoFlags as PF, STATE_MASK`.

### Estado en DB al momento del fix
Consulta forense contra `pilot_v5x.db`:
```sql
SELECT COUNT(*) FROM pedidos
WHERE (flags_estado & (1<<33)) > 0 AND (flags_estado & (1<<35)) > 0
```
**Resultado: 0 filas.** Bug latente — nunca se disparó en producción. El fix es preventivo.

---

## 3. Higiene ALFA.md — Fuera del Tracking Git

### Contexto
`ALFA.md` y `ALFA_OLD.md` estaban siendo trackeados en el repo D. Por doctrina (cada máquina/entorno tiene su propio protocolo ALFA), estos archivos deben ser locales y no versionados.

### Acciones
- `git rm --cached ALFA.md ALFA_OLD.md` — removidos del índice, permanecen en disco.
- `.gitignore` D actualizado con:
  ```
  # Protocolos locales (ALFA/OMEGA — cada máquina/entorno tiene versión propia)
  ALFA.md
  ALFA_OLD.md
  ```
- ALFA.md copiado a `Q:\Mi unidad\V5_Silo_Claude\ALFA.md` (4878 bytes) como respaldo en Silo.

---

## 4. BOARD_V5.xlsx — Actualización Integral

### Cards cerradas
| ID | Motivo cierre |
|----|--------------|
| #51 | Fix router.py:266 — STATE_MASK aplicado en migración quirúrgica. CA sesión 825. |
| #59 | Duplicado de #58. |
| #65 | Duplicado de #60. |

### Cards nuevas (#60-#70)
| ID | Título | Tipo | Prioridad | Estado |
|----|--------|------|-----------|--------|
| #60 | Estructurar PROTOCOLO/ en Q: (D/, P_DEV/, P_GOLD/) | INFRA | ALTA | PENDIENTE |
| #61 | Verificar ALFA.md en Q: OF | DEUDA | MEDIA | PENDIENTE |
| #62 | ALFA offline fallback | DEUDA | MEDIA | PENDIENTE |
| #63 | Semáforo SystemFlags (.pasaporte_v5.json genoma) | DEUDA | MEDIA | PENDIENTE |
| #64 | Reformular cierre reporte ALFA | DEUDA | BAJA | PENDIENTE |
| #66 | Limpiar cards vacías BOARD (#41-#45) | DEUDA | BAJA | PENDIENTE |
| #67 | Rediseñar Board | DISEÑO | MEDIA | PENDIENTE |
| #68 | Nexo Card #000 en ALFA | FEATURE | MEDIA | PENDIENTE |
| #69 | Board P-Gold para Tomy | FEATURE | MEDIA | PENDIENTE |
| #70 | SISTEMA_STATUS_SPEC.md V1.1 (Radar + Canario 2.0) | INFRA | ALTA | PENDIENTE |

Card #70: spec canonizado por Nike LUZ VERDE GOLD 2026-06-14. Secuencia de implementación: SISTEMA_STATUS.json en Q: → Canario 2.0 en ALFA Fase 0 → escritura en OMEGA (4 capas + bits 60/61/62) → script actualizar_card000.py → estructurar PROTOCOLO/ con 3 perfiles. Depende de: #60, #62, #63, #64, #68.

---

## 5. Verificación .gy_identity
- `C:\dev\Sonido_Liquido_V5\.gy_identity` → `CA`
- `C:\dev\v5-ls-Tom\current\.gy_identity` → `CA`
- Ambos coinciden. Identidad de entorno confirmada.

---

## 6. Estado Final OMEGA

| Fase | Estado |
|------|--------|
| Canario LAVIMAR | NOMINAL GOLD (flags=13) |
| WAL checkpoint | OK |
| Backup DB rotación | OK (slots 1-3, MAESTRO+DESARROLLO) |
| Espejo Excel | OK (36 pedidos, 65 ítems) |
| SESION_NEXT | Actualizado |
| ESTADO_ECOSISTEMA | Actualizado |
| Caja Negra | Actualizado |
| Bitácora | Actualizado |
| Informe Histórico | Este documento |

**Commits pendientes (requieren PIN 1974):**
- D: ALFA.md/ALFA_OLD.md rm --cached + .gitignore + router.py:266 fix #51
- P: pdf_debug.txt rm --cached
