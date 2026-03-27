# CAJA NEGRA: Sesión Perfección Soberana V5.5 GOLD (2026-03-26 Parte 2)

## 1. Movimiento de Bits y Genoma
- **Bit 6 (OC_REQUIRED)**: Implementación de Poka-Yoke visual (Neon Blue) y validación en PedidoCanvas.
- **Bitwise Logic**: Calibración en Frontend para diferenciar obligatoriedad de asterisco vs borde neón.

## 2. Intervención en el Núcleo (Backend)
- **Decimal Fix**: Refactorización de 8 puntos en `backend/pedidos/router.py` usando `Decimal(str(item.cantidad))` para evitar TypeErrors con floats.
- **ProductoCosto Extensions**: Inyección de `costo_reposicion` y `margen_sugerido` en modelos y esquemas Pydantic.

## 3. Persistencia Física y UI
- **PedidoCanvas (Ficha #ID)**: Transformación en "Ficha del Pedido" con título dinámico e hidratación mejorada.
- **Rentabilidad Dinámica**: Panel F8 migrado de estático a dinámico con lógica de cálculo viva sobre `items`.
- **Keyboard Optimization**: Secuencia de foco `Cliente -> OC -> SKU` (Hoja de cálculo mode).
- **Hotfix**: Blindaje de `RentabilidadPanel.vue` con guardas contra `undefined reduce`.

---
**Marcador de Sesión**: 2026-03-26_OMEGA_GOLD_SYNC_V8_6
**Agente**: Gy (Antigravity V5 - Atenea)

# CAJA NEGRA: Sesión Perfección Soberana V5.2 GOLD (2026-03-25 Parte 3)

## 1. Movimiento de Bits y Genoma
- **Bindings N/M**: Planeamiento estratégico documentado en `ANALISIS_TRANSPORTE_LOGISTICA.md` para integrar `EmpresaTransporte` y `NodoTransporte` en los domicilios del `Cliente`.

## 2. Intervención en el Núcleo (Backend)
- **Pydantic Property Forcing**: Implementación de `@property cliente_id` expuesta llanamente en `RemitoResponse` para bypassear las limitaciones de lazy-load de SQLAlchemy sin incurrir en N+1 Queries.
- **Client Mapping Fix**: Mapeo riguroso de `payload.cliente.id` en el Router de ingesta de facturas, eliminando la creación colateral de cuentas "Desconocido".
- **Cascaded Eradication**: Adición de `DELETE /remitos` con purga lógica del remito e interceptación física de eliminación en cascada para su Pedido de origen (sólo si es `INGESTA_PDF`).

## 3. Persistencia Física
- Cambios frontend directos en `RemitoListView.vue` inyectando botones de estado (Imprimir) y cierre (Trash) con reestructuración visual Poka-Yoke.

---
**Marcador de Sesión**: 2026-03-25_OMEGA_GOLD_SYNC_V3
**Agente**: Gy (Antigravity V5 - Atenea)
