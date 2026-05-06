# ARLEQUÍN V2 — Export Completo

## Contenido

Extracción de cambios críticos de la rama `feature/arleq-v2-productos` para:
1. Auditoría
2. Documentación
3. Replicación en entorno P (V5-LS)

---

## Archivos

### Backend Productos

**constants.py** (1.5K)
- Cambio semántico: `VIRGINITY` → `HAS_ACTIVITY`
- Eliminación de `LEVEL_NEW`, `LEVEL_OPERATIONAL`
- Bit 1 con inversión lógica (0=virgen, 1=tocado)

**models.py** (5.5K)
- Agregada: `nombre_canon = Column(String(300), nullable=True, index=True)`
- Campo de deduplicación BOW para productos
- Indexed para queries rápidas

**service.py** (16K)
- `normalize_name()` — Tokenización BOW pura (len >= 2)
- `check_duplicate_name()` — Validación en create_producto()
- `create_producto()` — Activado: calcula nombre_canon, valida duplicados
- `hard_delete_producto()` — Actualizado: usa HAS_ACTIVITY en lugar de VIRGINITY

### Backend Remitos

**remitos_service.py** (31K)
- **BREAKING CHANGE:** Ingestion ahora es READ-ONLY
- Eliminadas 100 líneas: CREATE PEDIDO, RESOLVE ITEMS, auto-create
- Agregadas: modo_ingesta lógica (VINCULAR_EXISTENTE, VINCULAR_CUMPLIDO)
- Nueva: `create_puente_factura()` — Bridge Factura → Remito
- Guard clauses: Anti-ghosting, anti-zombie

**remitos_router.py** (14K)
- Mejorado: Exception handling para ValueError
- Nuevo: HTTP 409 Conflict para "PEDIDO_REQUERIDO"
- Nuevo: Endpoint POST /puente/desde_factura/{factura_id}

### Documentación

**MERGE_PENDING.md** (3.6K)
- Audit trail completo de Arlequín V2
- 5 fases ejecutadas bajo PIN 1974
- Consolidación de duplicados SURGIBAC (IDs 200, 204, 205)
- Hard-delete con LEY DE VIRGINIDAD
- Breaking changes documentados

---

## Cambios Clave

### Productos

| Aspecto | Antes | Después |
|---------|-------|---------|
| Deduplicación | ILIKE name search | BOW + nombre_canon |
| Bit 1 semántica | IS_VIRGIN | HAS_ACTIVITY |
| Hard-delete | Inverted logic | Direct check |
| DB schema | Sin nombre_canon | +nombre_canon indexed |

### Remitos

| Aspecto | Antes | Después |
|---------|-------|---------|
| Auto-crear Pedido | ✅ Sí | ❌ No (READ-ONLY) |
| Auto-crear Producto | ✅ Sí | ❌ No |
| Pedido requerido | ❌ Opcional | ✅ Obligatorio |
| Error si falta | HTTP 400 | HTTP 409 |
| Flujo | PDF → Auto-create | PDF → Link o error |

---

## Implementación (Cuando mergear a P)

1. **Backup DB:**
   ```bash
   cp V5_LS_MASTER.db V5_LS_MASTER.db.bak.pre-arlequin-v2
   ```

2. **Actualizar código:**
   - Copiar archivos críticos
   - Reemplazar en backend/

3. **Migración DB (si necesaria):**
   ```bash
   python
   import sqlite3
   conn = sqlite3.connect('V5_LS_MASTER.db')
   cur = conn.cursor()
   cur.execute("ALTER TABLE productos ADD COLUMN nombre_canon VARCHAR(300)")
   conn.commit()
   ```

4. **Backfill (si necesaria):**
   - Ejecutar normalize_name() en todos los productos existentes
   - Guardar en nombre_canon

5. **Test:**
   - Verificar Canario LAVIMAR
   - Test ingesta: debe exigir pedido vinculado
   - Test productos: check_duplicate_name() activo

---

## Notas

- **PIN 1974:** Todos los cambios requirieron PIN 1974 para ejecución
- **Commits:** 6 commits totales (Bit1, BOW, Talles, Revert, Remitos, Docs)
- **Branch:** `feature/arleq-v2-productos` (estable para PR)
- **Merge:** Requiere aprobación de Carlos + Sonnet

---

*Export generado: 2026-05-04*
*Rama: feature/arleq-v2-productos*
