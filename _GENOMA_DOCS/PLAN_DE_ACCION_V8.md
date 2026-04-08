# PLAN DE ACCIÓN V8 (Consolidación Post-ARCA)

## 1. Mantenimiento Preventivo
- [ ] **Monitoreo de Lotes:** Verificar semanalmente que no queden clientes en estado "PENDIENTE" de validación ARCA.
- [ ] **Auditoría de Duplicados:** Revisar periódicamente la tabla de clientes para detectar CUITs duplicados no intencionales.

## 2. Expansión Funcional (Fase 2)
### A. Gestión de Notas de Crédito
- Implementar lógica de anulación fiscal vinculada a facturación electrónica (cuando se active).

### B. Integración Profunda con Stock
- Vincular la validación de clientes con reglas de bloqueo de despacho (ej: no despachar a clientes con CUIT inválido o deuda).

## 3. Deuda Técnica
- [ ] Refactorizar el módulo de `Productos` para alinearlo con la arquitectura V6 de Clientes (Autonomía de Guardado).
- [ ] Migrar el módulo de `Proveedores` a la nueva estructura de Agenda Global.

---
**Estado:** PLANIFICADO
**Prioridad:** MEDIA
