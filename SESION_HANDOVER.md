# Protocolo de Transición (Handover)
**Fecha:** 11 de Diciembre de 2025
**Estado:** Sistema Piloto Operativo / Diseño de Cargador Aprobado

## Estado Situacional
1.  **Piloto V5 (`BUILD_PILOTO`):**
    *   **DB:** `produccion.db` (SQLite) operativa con datos limpios de Clientes y Productos.
    *   **IOWA (Cloud):** Sincronizada y actualizada con `scripts/migrate_to_iowa.py`.
    *   **Backup:** Carpeta `SEMILLAS_MAESTRAS` generada con `scripts/export_master_seeds.py`.

2.  **Nueva Funcionalidad (En Cola):**
    *   **Cargador Táctico (Grid V5):** Diseño aprobado en `DISEÑO_CARGADOR_TACTICO.md`.

## Próxima Tarea (Immediate Next Action)
**Objetivo:** Iniciar Fase 1 del Cargador Táctico.
**Referencia:** Tarea ID 33 en `task.md`.

### Pasos Sugeridos:
1.  Crear `frontend/src/views/Ventas/GridLoader.vue`.
2.  Implementar el Layout base (Cabecera + Grilla vacía).
3.  Configurar la ruta en `frontend/src/router/index.js`.
4.  Crear `frontend/src/stores/pedidoStore.js`.

> [!NOTE]
> El usuario prefiere trabajar en "Modo Híbrido". Si trabaja en casa, usará IOWA. Si trabaja en oficina, usa Local y sincroniza. Comprueba siempre estado de migración si cambias de lugar.
