-- ============================================================
-- DISEÑO PENDIENTE: Orígenes de Pedido (2026-04-15)
-- Acordado en sesión 791. Implementación requiere PIN 1974.
-- ============================================================
--
-- Problema: La ingesta de facturas creaba pedidos en $0 en silencio
-- para satisfacer el NOT NULL de remitos.pedido_id. Diseño incorrecto.
--
-- Solución acordada: usar bits libres de flags_estado en pedidos.
-- El Remito SIEMPRE tiene pedido padre (real o forzado).
-- No hay tabla separada de huérfanos.
--
-- Bits a asignar (verificar disponibilidad con audit_v5.py):
--   BIT_ORIGEN_FACTURA = 2^?  → Pedido creado por ingesta de factura AFIP
--                               Con respaldo contable. Advertir antes de anular.
--   BIT_ORIGEN_REMITO  = 2^?  → Pedido creado por remito sin pedido previo
--                               Sin respaldo contable. Pendiente de facturar.
--
-- Campo origen (ya existe en pedidos):
--   origen = 'FORZADO_FACTURA'  (ex 'INGESTA_PDF')
--   origen = 'FORZADO_REMITO'
--
-- NO requiere ALTER TABLE si solo se usan bits de flags_estado + campo origen ya existente.
-- Solo requiere refactor de RemitosService.create_from_ingestion() en service.py.
-- ============================================================

-- SQL Migration: Logistics Expansion (V10)
-- Adding Support for Delivery Address and Transport to Orders

ALTER TABLE pedidos ADD COLUMN domicilio_entrega_id UUID;
ALTER TABLE pedidos ADD COLUMN transporte_id UUID;

-- Optional: Add Foreign Key constraints if the database supports them (e.g., PostgreSQL)
-- In SQLite, we rely on application-level integrity for Dynamic UUIDs.

-- ALTER TABLE pedidos ADD CONSTRAINT fk_pedido_domicilio FOREIGN KEY (domicilio_entrega_id) REFERENCES domicilios(id);
-- ALTER TABLE pedidos ADD CONSTRAINT fk_pedido_transporte FOREIGN KEY (transporte_id) REFERENCES empresas_transporte(id);
