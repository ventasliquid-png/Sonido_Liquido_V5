# Informe de Sesión: Saneamiento DB + Fixes Operativos + Paridad D/P

**Fecha**: 2026-04-14  
**ID de Sesión**: Omega-20260414  
**Agente**: Claude Code (Sonnet 4.6)  
**Estado del Sistema**: **NOMINAL GOLD**  
**Entorno**: OF

---

## 1. Punto de Partida

La sesión retomó con P (V5-LS) ya saneado del 13/04 (26 productos, DB certificada). D (pilot_v5x.db) todavía tenía los duplicados y NULL SKU sin tocar. El sistema de cantera import fallaba con 500 en P, y los fixes de frontend (F4, Rubro obligatorio) estaban pendientes de build y deploy.

---

## 2. Intervenciones

### 2.1 Cirugía DB — pilot_v5x.db

Misma lógica que P, adaptada a los IDs presentes en D (sin 196/197):

| Grupo | Defectivos | Survivor | Pedidos re-apuntados |
|---|---|---|---|
| Surgibac PA 1L | 156 | 179 | — |
| Surgibac PA Bidón 5L | 176, 186 | 172 | — |
| Guante Nitrilo M | 169 | 6 | — |
| Cofia | 170 | 149 | — |
| Guante Veterinario | 171 | 175 | 159→175 |
| Surgizime E2 | 173 | 177 | 173→177 |
| Toallas Super | 152 | 161 | — |

IDs 158, 159, 160 (NULL SKU, seeded desde cantera) eliminados físicamente.  
8 productos con flags=0/2 y sin movimientos, borrados en limpieza post-fusión.  
**Estado final: 23 productos.**

### 2.2 Fix Cantera Import — 500 → OK

Tres causas del 500 corregidas en `backend/cantera/router.py` (D y P):

1. **`flags_estado` ausente**: El modelo tiene `NOT NULL DEFAULT 0`, pero al insertar sin el campo con `DEFAULT 0` en SQLAlchemy requería el valor explícito. Solución: `flags_estado=3` (ACTIVE+VIRGIN).
2. **Campo renombrado**: `margen_mayorista` → `rentabilidad_target`. El modelo ya fue renombrado en ambos entornos pero el router no fue actualizado.
3. **Auto-SKU**: Cuando el mirror JSON trae SKU nulo, el router asignaba `None`. Ahora: `MAX(sku)+1` con piso 9001. Los SKUs de cantera quedan en rango 9001+ diferenciado de los manuales (10000+).

Adicionalmente: SKU parseado como `int(float(sku_raw))` para compatibilidad con mirrors que serializan enteros como floats (`"123.0"`).

### 2.3 Fixes Frontend

**PedidoCanvas.vue — F4:**  
El handler de F4 abría el modal de cliente cuando el foco estaba en cualquier otro lugar (incluyendo el cuerpo del documento). Fix: verificar primero si hay búsqueda de producto activa (`showProductResults || activeSku || activeDesc`). Modal de cliente solo si el foco está explícitamente en `clientInputRef`.

**ProductoInspector.vue — Rubro obligatorio:**  
- `<span class="text-rose-500">*</span>` en el label
- `rubroError = ref(false)` con ring condicional `ring-1 ring-rose-500` en `SelectorCreatable`
- Mensaje `⚠ El rubro es obligatorio para guardar` bajo el selector
- Validación: `rubroError.value = true/false` en el flujo de guardado

### 2.4 Infraestructura

**DESPERTAR.ps1:** Guard contra `.ParseExact(null, ...)` que causaba excepción .NET no capturada por `SilentlyContinue`. Agregado mensaje informativo cuando no hay `.bak` disponible.

**boot_system.py:** `--reload-dir backend` previene que uvicorn se reinicie por writes de la caché de Vite en `frontend/`. Polling de health check (`/docs`) reemplaza `sleep(5)` fijo — sistema listo en exactamente el tiempo que tarda, no 5 segundos de garantía.

**main.py (D y P):** `/` renombrada a `/health`. El catch-all `/{full_path:path}` ahora puede capturar correctamente la raíz y servir `index.html`, habilitando que el SPA funcione desde `/` en producción (fix para la pantalla en blanco de Tomy).

---

## 3. Métricas

| Métrica | Valor |
|---|---|
| Fusiones ejecutadas | 7 grupos |
| Pedidos re-apuntados | 2 (173→177, 159→175) |
| Productos eliminados físicamente | 11 (3 NULL SKU + 8 limpieza) |
| Estado final pilot_v5x.db | 23 productos |
| Archivos backend modificados | 2 (cantera/router.py, main.py) |
| Archivos frontend modificados | 2 (PedidoCanvas.vue, ProductoInspector.vue) |
| Archivos infra modificados | 2 (DESPERTAR.ps1, boot_system.py) |
| Entornos sincronizados | D y P — paridad confirmada |

---

## 4. Estado de Cierre

- **Sistema**: NOMINAL GOLD
- **Frontend**: Vite en 5173, sin errores
- **Backend**: uvicorn 8080 con --reload-dir backend
- **Rama activa D**: `stable-v5-of-20260330`
- **Rama activa P**: `main`
- **DB D**: `pilot_v5x.db` — 23 productos, sin modificaciones de schema
- **DB P**: `V5_LS_MASTER.db` — 26 productos, tabla `sistema_metadata` creada
