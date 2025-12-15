# BITACORA DEV - SESIÓN 2025-12-15
## Refinamiento de UX en Carga de Pedidos (Táctico)

### Resumen
Jornada enfocada en resolver problemas críticos de usabilidad (UX) en la pantalla de Carga Táctica (`GridLoader`), reportados por el usuario durante pruebas de aceptación.

### Problemas Detectados y Soluciones

#### 1. Visibilidad de Inputs (White-on-White)
**Problema:** Los campos de texto "O.C." y "Observaciones" (tanto en el pie de página como el Textarea superior) se volvían invisibles (texto blanco sobre fondo blanco) debido a la inferencia de estilos del navegador (Autofill agents) y herencia de colores incorrecta.
**Solución:**
- Se implementó un esquema de "Alto Contraste" para los inputs críticos.
- Se cambió el fondo a `bg-slate-200` (Gris claro) y el texto a `text-slate-900` (Negro) con `!important` para forzar la legibilidad sobre cualquier estilo de agente del navegador.
- Se aplicó lo mismo al Textarea de comentarios internos.

#### 2. Lógica de Etiqueta Logística
**Problema:** El sistema mostraba "Retira en Local" incluso cuando el cliente tenía domicilio de entrega cargado, si no se había especificado una empresa de transporte (Transportista = null).
**Solución:**
- Se creó una propiedad computada `logisticsLabel` que prioriza la existencia de `domicilio_entrega`.
- Lógica: Si hay domicilio -> "Envío a Domicilio" (aunque sea con flete genérico). Solo si no hay domicilio -> "Retira en Local".

#### 3. Persistencia de Datos ("Fantasma del Borrador")
**Problema:** Al recargar la página (F5), los datos de un pedido anterior o malformado reaparecían debido al `autosaveDraft`, impidiendo limpiar la pantalla.
**Solución:**
- Se agregó un botón explícito de **"Limpiar / Reset" (Icono Papelera)** en la barra de herramientas.
- Este botón borra el estado de la aplicación (`form`, `items`, `client`) y elimina la clave `tactical_draft` del `localStorage`.

#### 4. Artefactos Visuales (Ventana Blanca)
**Problema:** El switch de "Generar Excel" estaba posicionado absolutamente (`absolute bottom-16`) causando solapamiento y un efecto de "ventana blanca fltante" sobre el botón Guardar.
**Solución:**
- Se movió el control de Excel a la barra de herramientas flex (`footer`), alineado con los botones de acción, eliminando el posicionamiento absoluto y los conflictos visuales.

### Próximos Pasos (Agendados)
- Generar listado de pedidos (Backend/Frontend).
- Instrumentación de flujo de estados de pedidos (libertad de cambio de estado).
