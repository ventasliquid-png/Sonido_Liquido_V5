# INFORME HISTÓRICO: PROTOCOLO OMEGA - REFACCIONAMIENTO UI Y MODALIZACIÓN DE CLIENTES
**Fecha:** 2026-02-27
**Agente:** Antigravity (Gy V14 - Gemini 3.1 Pro)
**Rama:** `feat/v5x-universal` (V5)

## 1. OBJETIVO LOGRADO
Resolver regresiones reportadas en la interfaz de usuario (desaparición de "Remitos" del menú lateral) y sustituir el componente simplificado `ClienteInspector` por la "Ficha de Cliente" completa y original (`ClientCanvas`) en los flujos de creación/edición asistida, como fue solicitado expresamente por el Comandante.

## 2. HITOS TÉCNICOS

### 2.1 Restauración de Visibilidad Logística (Remitos)
- **Problema:** El enlace a la vista de "Remitos Emitidos" había desaparecido del `AppSidebar` durante actualizaciones previas.
- **Solución:** Se reintrodujo la navegación en `AppSidebar.vue`, se creó una vista global robusta `RemitoListView.vue` y se conectó el servicio y store correspondientes (`remitos.js`) para permitir la consulta general de despachos.

### 2.2 Refactorización Dual de ClientCanvas
- **Problema:** En el flujo de "Ingesta Automática de Facturas", la intervención del Sabueso Oro disparaba un modal con `ClienteInspector.vue`. Sin embargo, la Doctrina de Consistencia exige la lupa de validación de ARCA situada en el header, característica exclusiva de `ClientCanvas.vue` (la ficha original).
- **Solución Arquitectónica:** En lugar de duplicar código, se refactorizó `ClientCanvas.vue` (1700+ líneas) para soportar uso dual. Mediante la inyección de `props` (`isModal`, `initialData`) y la emisión de eventos `@close` / `@save`, el lienzo ahora puede empotrarse como un modal interactivo sin perder su rol como vista autónoma de página completa.

### 2.3 Estandarización Multiplex (Propagación del Modal)
- **Ejecución:** Una vez validado el modal en `IngestaFacturaView`, se procedió a erradicar el uso de `ClienteInspector` en todo el sistema.
- **Alcance:** `PedidoTacticoView.vue`, `PedidoCanvas.vue` y `HaweView.vue` adoptaron el nuevo `<ClientCanvas :isModal="true" />`.
- **Beneficio:** Simplificación del árbol de componentes y exposición de todas las herramientas de inteligencia comercial + validación fiscal en cualquier punto del sistema donde se requiera dar de alta o asentar un cliente interactuando con ARCA.

## 3. ESTADO DEL SISTEMA
- **Regresiones:** Solucionadas.
- **Experiencia de Usuario:** La pantalla de carga preferida por el Operador ahora es ubicua.
- **Preparación Operativa:** Lista para comprobación por parte del Operador mediante el Protocolo Alfa o Pruebas de Humo en Sandbox.
