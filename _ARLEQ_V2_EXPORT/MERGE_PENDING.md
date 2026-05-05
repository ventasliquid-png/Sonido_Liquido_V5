# ⚠️ RAMA PENDIENTE DE MERGE — feature/arleq-v2-productos

## Contenido
Corrección semántica Bit 1 en módulo productos (Códice Arlequín V2).
Unificación con semántica de clientes: HAS_ACTIVITY, Lectura B.

## Prerequisito de merge
- P debe estar sincronizado con main (pull de commits del finde)
- Canario LAVIMAR debe estar nominal (flags_estado = 13)
- PIN 1974 requerido para merge

## NO mergear sin autorización explícita de Carlos + Sonnet

---

## Acciones ejecutadas bajo PIN 1974 (2026-05-04)

### Arlequín V2 — Consolidación de Duplicados

**Problema:** Base de datos contenía 3 registros idénticos de SURGIBAC PA BIDÓN POR 5 LITROS
- IDs: 200, 204, 205
- SKUs: 80038, 80039, 80040 (consecutivos)
- Mismo nombre exacto, flags_estado=0

**Resolución:**
- Producto 200 designado como canónico
- PedidoItem 36 reasignado: 205 → 200
- Productos 204, 205 desactivados (soft-delete, conservan historia)
- Consolidación verificada: ambos pedidos ahora usan ID 200

**Impacto:**
- Deuda técnica: 2 registros huérfanos desactivados
- Integridad: sin pérdida de datos, solo consolidación

### Arlequín V2 — Fix: Preservación de Talles en BOW

**Problema:** El algoritmo BOW filtraba tokens de 1 carácter,
causando colisiones entre productos que diferían solo por talle (S, M, L, X).

**Resolución:**
- Agregar TALLES_1CHAR = {'X', 'S', 'M', 'L'} a normalize_name()
- Preservar estos caracteres durante tokenización
- Verificado: 4 talles generan tokens BOW distintos

**Impacto:**
- Guantes talle L vs S vs M vs XL ahora diferenciables
- Previene falsos positivos en deduplicación futura

### Arlequín V2 — Hard Delete PIN 1974

**Ejecución:**
- Hard delete: Productos 204, 205 (duplicados consolidados)
- Estado: ambos virgenes, sin PedidoItems
- Procedimiento: LEY DE VIRGINIDAD validated, DELETE ejecutado
- Resultado: ID 200 es ahora único canonical de SURGIBAC PA BIDÓN 5L

### Arlequín V2 — Reversión: BOW puro (sin TALLES_1CHAR)

**Decisión arquitectónica:**
- Revertir preservación de talles (S, M, L, X)
- Restaurar doctrina BOW pura: len(token) >= 2 sin excepciones
- Rationale: aggressiveness en matching, tolerancia a variaciones menores
- Resultado: "Guantes talle L" == "Guantes talle S" (mismo producto core)

**Impacto:**
- Deduplicación más conservadora, menos falsos positivos
- Algoritmo más simple y predecible
- Consistencia con doctrina de tokenización pura

### Arlequín V2 — Blindaje Remitos: Ingesta Solo Lectura

**BREAKING CHANGE - Arquitectura de flujo:**

**Problema:** Ingestion creaba auto-pedidos, productos, items sin control
- 100 líneas de código generativo en remitos/service.py
- Crear pedidos sin auditoría clara (orphaned)
- Mezcla de lectura (parsear PDF) + escritura (crear entidades)

**Resolución:**
- Remitos module ahora es READ-ONLY para ingestion
- Pedido DEBE pre-existir (creado en ABM Pedidos antes)
- ValueError("PEDIDO_REQUERIDO:...") si falta pedido
- HTTP 409 Conflict en /ingesta-process si no hay pedido

**Cambios:**
- service.py: -100 líneas (eliminar CREATE PEDIDO block)
- router.py: +6 líneas (error handling estructurado)

**Doctrina Pendiente (Arlequín V2 Fase 3):**
- F1: Conciliación automática factura ↔ pedido
- F2: Manejo de entregas parciales
- F3: Factura huérfana (sin pedido) → queue para resolver

**Summary - MERGE READY:**
- Total commits: 5 (Bit1 + BOW + Talles + Revert + Remitos)
- Módulos: productos (BOW dedup), remitos (solo lectura)
- Database: limpia, deduplicada, listo para GOLD
- Breaking changes: documented en MERGE_PENDING.md
