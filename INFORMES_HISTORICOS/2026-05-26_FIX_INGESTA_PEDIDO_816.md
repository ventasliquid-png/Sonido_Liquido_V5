# INFORME HISTÓRICO SESIÓN 816 OF: Fix Ingesta/Pedido + Salvaguardas

**Fecha:** 2026-05-26  
**Locación:** OF  
**PIN:** 1974  
**Hash D:** 39309805  
**Estado:** NOMINAL GOLD  

---

## 1. Misión
Corregir los bugs críticos identificados en el módulo de ingesta y pedidos, realizar un análisis comparativo entre Producción (P) y Desarrollo (D) para garantizar la consistencia, e incorporar salvaguardas defensivas críticas.

---

## 2. Trabajo Realizado

### A. Corrección Flujo Ingesta/Pedido (Bugs en Cadena)
- **AttributeError en approve:** Se corrigió la sintaxis de acceso al objeto devuelto por `IngestaService.approve()` en `backend/ingesta/router.py`. Dado que la función retorna un diccionario, se cambió el acceso de tipo objeto (`procesada.id`) a accesos seguros de tipo diccionario (`procesada["id"]`, `procesada["estado"]`).
- **Vinculación Obligatoria:** Se modificó `backend/ingesta/service.py` para impedir que se apruebe una factura raw sin especificar un ID de pedido. Se valida explícitamente `pedido_id` contra la base de datos antes de proceder.
- **Frontend Sync (Modal & Flujo):** Se modificó `IngestaFacturaView.vue` para requerir obligatoriamente la selección de un pedido vinculante y enviar el payload con `pedido_id_vinculado`.
- **Limpieza de Endpoint Obsoleto:** Se eliminó el endpoint deprecado `/remitos/ingesta-process` del frontend y backend en favor del flujo oficial de aprobación de ingestas.

### B. Corrección de ImportError en Pedidos
- **Fallo en helper _aplica_iva:** Se eliminó la importación interna redundante de `PF` y `ClientFlags` dentro de la función helper `_aplica_iva` en `backend/pedidos/router.py` que intentaba importar de `backend.pedidos.constants` (donde `PF` no existe de forma directa, sino como alias global de `PedidoFlags`). Ahora utiliza la importación global al tope del archivo.

### C. Salvaguardas en Remitos
- Se importaron guardas defensivas desde P hacia D en `backend/remitos/router.py` dentro de la función `get_remito_pdf`. Si se intenta generar un PDF de un remito que carece de pedido o cuyo pedido carece de cliente, el sistema levanta excepciones HTTP 400 (`Remito sin pedido vinculado` / `Pedido sin cliente vinculado`) en lugar de arrojar excepciones de tipo `AttributeError` en runtime.

### D. Análisis Comparativo P vs D
- Se determinó que la raíz literal de P (`C:\dev\v5-ls-Tom\backend`) contiene solo 9 archivos de soporte. El código activo real de producción reside en `C:\dev\v5-ls-Tom\current\backend`.
- Al comparar D vs P (Current), se halló paridad estructural casi perfecta con una única diferencia: `backend/core/utils/text.py` existe únicamente en D.
- En cuanto a archivos clave:
  - `main.py`, `clientes/router.py` y `facturacion/router.py` están 100% idénticos.
  - `remitos/router.py` difería en las salvaguardas que ahora han sido sincronizadas en D.
  - `clientes/service.py` difiere debido a la lógica Nike de duplicidad de CUIT, normalización integrada localmente, y la Doctrina Rosa que se encuentra inactiva/eliminada en P (Current).

---

## 3. Estado del Ecosistema
- **Canario:** NOMINAL GOLD (flags=13).
- **WAL Checkpoint:** Ejecutado en `pilot_v5x.db`.
- **Silo de Respaldo:** Copia física de `pilot_v5x.db` resguardada exitosamente en `Q:\Mi unidad\V5_Silo_Claude\`.

---

## 4. Pendientes para Sesión 817 OF
1. **Despliegue P:** Pisar `C:\dev\v5-ls-Tom\current\` con la versión validada de D.
2. **Migraciones Base MT:** Ejecutar scripts de re-auditoría Bit 40, reparación de bits y alteración física de la tabla `pedidos` (adición de `fecha_vencimiento`).
3. **Mejoras UX / UI:** Ajustar cabeceras en Ingesta y corregir menú de cambio de estado.
