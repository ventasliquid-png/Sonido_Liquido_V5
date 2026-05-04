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
- Ready for merge: feature/arleq-v2-productos
