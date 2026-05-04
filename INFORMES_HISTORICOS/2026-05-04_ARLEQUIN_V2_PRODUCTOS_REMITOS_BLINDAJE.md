# Informe de Sesión: ARLEQUÍN V2 — Productos, Deduplicación y Blindaje de Ingesta

**Fecha:** 2026-05-04
**Entorno:** D (Sonido_Liquido_V5) — OF
**Estado:** NOMINAL — MERGE PENDIENTE EN CA
**Arquitecto:** Sonnet
**Ejecutor:** Claude Code (Haiku)
**Rama:** feature/arleq-v2-productos
**Hash final:** 26b7c68a

## 1. Objetivo de la Sesión

Completar la rama feature/arleq-v2-productos iniciada en sesión anterior.
Tres ejes: unificar semántica Bit 1 en productos, implementar deduplicación BOW 
con nombre_canon, y rediseñar el blindaje de create_from_ingestion() bajo 
doctrina de solo lectura.

## 2. Intervenciones Técnicas

### A. Semántica Bit 1 — ProductoFlags
Renombre IS_VIRGIN → HAS_ACTIVITY en constants.py y service.py.
Inversión lógica en hard_delete_producto(): 0=virgen/borrable, 1=tocado/bloqueado.
Eliminadas constantes huérfanas LEVEL_NEW y LEVEL_OPERATIONAL.

### B. nombre_canon — Deduplicación BOW
Hallazgo: normalize_name() y check_duplicate_name() existían en service.py
pero nombre_canon nunca se agregó al modelo ni a la DB. Código dormido desde origen.
Implementación completa:
- Column nombre_canon agregada a Producto (models.py)
- ALTER TABLE + backfill de 35 productos existentes
- check_duplicate_name() activado en create_producto()
- Algoritmo BOW puro: len(token) >= 2, sin excepciones de talles
Decisión documentada: tokens de 1 char (L, S, M, X) excluidos por ambigüedad
semántica — el freno humano es la barrera correcta para variantes de talle.
Feature Linaje de Productos diferida a V6.

### C. Consolidación SURGIBAC
Backfill reveló 3 registros duplicados (IDs 200, 204, 205 — SKUs consecutivos,
creados en lote por error).
- PedidoItem 36 migrado de producto 205 → 200
- ID 204 (virgen): hard delete con Papelera
- ID 205 (post-migración virgen): hard delete con Papelera
- ID 200 queda como canónico con historial completo (pedidos 14 y 21)

### D. Blindaje create_from_ingestion() — Doctrina Solo Lectura
Decisión arquitectónica mayor surgida de análisis de flujo:
La ingesta nunca debe crear productos automáticamente.
Un producto desconocido en un PDF debe darse de alta desde el módulo de
Productos antes de reintentar la ingesta.
Una factura sin pedido vinculado no puede procesarse — el pedido es obligatorio.
Implementación:
- Eliminadas ~100 líneas del bloque GY (auto-create productos y pedidos)
- Reemplazadas por ValueError("PEDIDO_REQUERIDO:...")
- Router actualizado: HTTP 409 con payload estructurado

Features pendientes documentadas:
- F1: Conciliación factura vs pedido con discrepancias (importes, descripciones)
- F2: Entregas parciales — bit ENTREGA_PARCIAL en pedidos
- F3: Facturas huérfanas — flag + cola de revisión supervisor

### E. Decisiones arquitectónicas diferidas a V6
- Feature Linaje de Productos: bifurcación de SKUs con padre_id y bit RENOMBRADO
- Modelo de variantes (talle/presentación) como atributos explícitos
- Slowly Changing Dimension Tipo 2 para historia de renombres

## 3. Métricas

- Commits en rama: 7
- Archivos críticos modificados: 6
- Productos backfilled con nombre_canon: 35
- Duplicados consolidados: 2 (204, 205 → 200)
- Líneas eliminadas de remitos/service.py: ~100
- Export quirúrgico: _ARLEQ_V2_EXPORT/ (7 archivos, 1731 líneas)

## 4. Estado y Pendientes

Rama pusheada a origin. Merge NO ejecutado — la rama acumula 166 archivos
de trabajo previo no relacionado. Merge quirúrgico manual programado para CA
usando _ARLEQ_V2_EXPORT/ como referencia.

Pendiente CA:
1. Pull en P (commits del finde, hash 484ab0bb)
2. Merge quirúrgico de 6 archivos críticos
3. Canario LAVIMAR en P post-merge (flags_estado = 13)
4. Actualizar OMEGA de P con protocolo push verificado
5. Limpiar rastro de error histórico: LAVIMAR flags_estado = 8205
   (valor incorrecto propagado por error de IA anterior — correcto es 13)
6. Unificar Omegas P y D en versión canónica

## 5. Notas de Sesión

El trabajo técnico fue superado en volumen por el trabajo arquitectónico.
La conversación sobre flujos de ingesta, parciales, linaje de productos
y el período transitorio ARCA produjo decisiones de diseño que hubieran
tardado semanas en emerger desde el código.

El error histórico LAVIMAR 8205 fue identificado y explicado: una IA anterior
confundió índice de bit con valor de bit (2^13 = 8192 + 13 = 8205).
Corrección pendiente en CA.

**Sello de cierre:** PIN 1974 — Sesión OF 2026-05-04 — NOMINAL
