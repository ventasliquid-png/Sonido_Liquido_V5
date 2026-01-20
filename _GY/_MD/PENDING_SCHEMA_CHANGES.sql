-- SQL Migration: Logistics Expansion (V10)
-- Adding Support for Delivery Address and Transport to Orders

ALTER TABLE pedidos ADD COLUMN domicilio_entrega_id UUID;
ALTER TABLE pedidos ADD COLUMN transporte_id UUID;

-- Optional: Add Foreign Key constraints if the database supports them (e.g., PostgreSQL)
-- In SQLite, we rely on application-level integrity for Dynamic UUIDs.

-- ALTER TABLE pedidos ADD CONSTRAINT fk_pedido_domicilio FOREIGN KEY (domicilio_entrega_id) REFERENCES domicilios(id);
-- ALTER TABLE pedidos ADD CONSTRAINT fk_pedido_transporte FOREIGN KEY (transporte_id) REFERENCES empresas_transporte(id);
