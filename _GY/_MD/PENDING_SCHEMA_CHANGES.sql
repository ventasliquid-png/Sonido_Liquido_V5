-- ==========================================
-- ARCHIVO DE MIGRACIONES PENDIENTES (Protocolo Amnesia)
-- ==========================================
-- OBJETIVO: Acumular sentencias SQL para replicar cambios de esquema
-- en la Base de Datos de Producción.
--
-- REGLA: Cada modificación en models.py DEBE tener su contraparte aquí.
-- ------------------------------------------

-- [PENDING] Inserte sus sentencias ALTER TABLE aquí...
-- [2026-01-14] Agregado campo 'venta_minima' a productos
ALTER TABLE productos ADD COLUMN venta_minima FLOAT DEFAULT 1.0;

-- [2026-01-14] DOCTRINA ROCA SÓLIDA (Pricing V2)
-- Renombrado margen_mayorista -> rentabilidad_target
ALTER TABLE productos_costos RENAME COLUMN margen_mayorista TO rentabilidad_target;
-- Agregado precio_roca
ALTER TABLE productos_costos ADD COLUMN precio_roca FLOAT DEFAULT 0;
-- [OPCIONAL] Limpieza de campos legacy (precio_fijo_override, cm_objetivo)
-- ALTER TABLE productos_costos DROP COLUMN precio_fijo_override;
-- ALTER TABLE productos_costos DROP COLUMN cm_objetivo;

-- [2026-01-14] SANITIZACIÓN (Error 500 Fix)
-- Nota: Schemas de Producto ajustados para tolerar valores 0.0 (Sanitización) para tenerlo en cuenta en futuras migraciones.
-- No requiere SQL DDL, es validación a nivel aplicación (Pydantic), pero se documenta aquí por protocolo.

-- [2026-01-15] Add 'nivel' column to 'segmentos' table for V5 Pricing Engine
ALTER TABLE segmentos ADD COLUMN nivel INTEGER DEFAULT 1;

-- [2026-01-15] Add 'orden_calculo' to 'listas_precios' for Hard Logic Pricing
ALTER TABLE listas_precios ADD COLUMN orden_calculo INTEGER;
