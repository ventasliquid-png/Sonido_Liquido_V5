# Informe de Sesión: Arlequín V2 — Merge Quirúrgico CA + Doctrina Bit 1 Resuelta

**Fecha:** 2026-05-04
**Entorno:** CA (ambos repos — D y P)
**Estado:** NOMINAL GOLD
**Arquitecto:** Sonnet
**Ejecutor:** Claude Code (Haiku)
**Hash D:** f9ae409a
**Hash P:** 8ad0ad58

## 1. Objetivo

Traer a CA el trabajo de OF (Arlequín V2 productos/ingesta) y mergearlo
correctamente en D. Resolver la doctrina canónica del Bit 1 que quedó
ambigua entre sesiones.

## 2. Intervenciones

### A. Merge quirúrgico Arlequín V2 en D
Traído desde origin/feature/arleq-v2-productos via _ARLEQ_V2_EXPORT/.
5 archivos mergeados: productos/constants.py, models.py, service.py,
remitos/service.py, remitos/router.py.

### B. Correcciones post-merge
- Bug: ClientFlags.VIRGINITY → ClientFlags.HAS_ACTIVITY (línea 296 remitos/service.py)
- Bug: flags_estado default=0 → default=2 en productos/models.py (nace virgen)
- Bug: lógica hard_delete invertida → if not has_activity or has_history

### C. Doctrina Bit 1 — resolución definitiva
Ambigüedad resuelta entre dos sesiones independientes que llegaron
a la misma conclusión sin comunicarse:
  Bit 1 = 1 → virgen/borrable (nace encendido)
  Bit 1 = 0 → tocado/bloqueado (se apaga con primera operación)
Válido para CLIENTES y PRODUCTOS. Semántica idéntica.
LAVIMAR flags=13 confirma: Bit 1 apagado = cliente maduro con historia.
Error histórico 8205 documentado y eliminado definitivamente.

### D. OMEGA V2.2 — dos versiones soberanas
D: estructura completa 6 fases + FASE 7 Antigravity + git add . prohibido
P: igual pero sin FASE 7 + sello Pasaporte/Polizón + aviso Tomy
Ambos con canario LAVIMAR explícito en FASE 1.

## 3. Métricas

- Archivos mergeados en D: 5
- Bugs corregidos post-merge: 3
- Repos actualizados: 2 (D y P)
- Memoria del sistema actualizada: 3 registros

## 4. Pendientes

- Arlequín V2 aún no está en P (solo OMEGA V2.2)
- P recibirá Arlequín V2 en sesión futura
- _ARLEQ_V2_EXPORT/ queda en D como scaffolding temporal

**Sello de cierre:** PIN 1974 — Sesión CA 2026-05-04 — NOMINAL GOLD
