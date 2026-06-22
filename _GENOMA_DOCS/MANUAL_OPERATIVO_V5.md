# MANUAL OPERATIVO V5 - SONIDO LÍQUIDO
**Versión del Documento:** 1.10 (Fixes Rosa/Blanco + Tablero Ambos/Fucsia — 829 OF, 2026-06-18)
**Estado:** VIGENTE
**Código de Doctrina:** DEOU-2025

### 📢 Actualización Sesión 832 OF (2026-06-22)
- **SmartSelect Contacto Responsable (Panel Logistica):** En la pestana de logistica de un pedido, si el cliente tiene contactos con rol logistico o decisor, aparece el selector "Contacto Responsable". Cambiar el contacto actualiza el pedido en tiempo real. Solo visible cuando hay vinculos cargados.
- **SmartSelect Nodo / Sucursal (Panel Logistica):** Si la empresa de transporte asignada tiene sucursales/nodos (Bit 6 activado en su ficha), aparece el selector de nodo de entrega. Solo visible para empresas con Bit 6.
- **Sin cambios visibles para el operador en P/MT:** Estas features requieren que Tomy ejecute git pull y reconstruya el frontend.

### 📢 Actualización Sesión 829 OF (2026-06-18)
- **Motor Silencioso Rosa (PedidoInspector línea 570):** El sistema diferencia automáticamente entre pedidos Rosa (sin documentos fiscales) y Blanco (con documentos). Un operador que carga un pedido Rosa verá la operación sin avisos de borrador/remito — circuito INTERNO soberano.
- **ClienteSummary.flags_estado:** Nuevo campo en la respuesta backend que permite al frontend validar la condición de cliente (Bit 4 = Rosa) antes de decidir si crear documentos. Validación bifurcada y anticipada.
- **Tablero Pedidos — Botón "Ambos" (Default):** Nueva vista default que muestra todos los pedidos (Oficial + Interno) con gradiente esmeralda→fucsia. El botón "Circuito Interno" cambió a rosa/fucsia (bg-pink-600) para diferenciación visual clara. Filas Rosa mostradas con fondo pink-950/30 y borde izquierdo fucsia.
- **Validación Flexible de Segmento:** La validación Rosa ahora acepta `segmento.id` (objeto anidado) además de `segmento_id` (string), maximizando compatibilidad con distintos formatos de respuesta backend.

### 📢 Actualización Sesión 825 CA (2026-06-14)
- **Fix Card #51 (transparente para operador):** Corrección de bug latente en el módulo de ingesta — un pedido viejo podía quedar con dos estados de ciclo de vida activos simultáneamente (Firme + Anulado). El sistema ahora aplica correctamente la transición de estado. No se detectaron casos activos en producción. No requiere acción del operador.
- **BOARD V5 actualizado hasta Card #70:** Se incorporaron 11 cards nuevas (#60-#70) relacionadas con infraestructura de protocolos, Canario 2.0, Radar de Flota y mejoras al Board. Ver BOARD_V5.xlsx en el Silo Drive.
- **Entorno CA sincronizado:** Los repositorios D y P en Casa fueron sincronizados con la versión de Oficina. Estado NOMINAL GOLD.

### 📢 Actualización Sesión 822 (2026-06-04)
- **Excel Espejo de Pedidos operativo:** El botón naranja **"📊 Exportar Excel"** en la barra superior (junto a "+ Nuevo") genera `PEDIDOS_ESPEJO.xlsx` directamente en el Silo Drive (`Q:\Mi unidad\V5_Silo_Claude\`). No requiere abrir el ERP para consultar pedidos — el archivo es una copia de consulta offline.
- **Formato:** Un bloque por pedido con colores según estado (🟢 Pendiente / 🟡 Cumplido / 🔴 Anulado / 🟣 Presupuesto). Incluye costos (cuando disponibles) y notas del pedido. IVA discriminado solo para clientes Responsables Inscriptos — clientes CF/informal/Circuito Negro aparecen sin fila IVA o con IVA $0.
- **Si el archivo está abierto:** el sistema genera automáticamente `PEDIDOS_ESPEJO_HHMMSS.xlsx` sin interrumpir. Cerrar el original y volver a exportar para mantener el nombre canónico.
- **Bugs Tomy detectados en producción:** 4 issues en P/MT (Card #46 ALTA). Ver BOARD_V5.xlsx.

### 📢 Actualización Sesión 820 (2026-05-30)
- **Sistema de Ingesta:** Operativo para caso "feliz" (factura ARCA = BORRADOR). El visor de discrepancias existe pero NO tiene acciones. Si hay diferencia entre lo facturado y el pedido, el operador debe resolverlo manualmente hasta que se implemente Card #43.
- **Clientes Rosa:** Domicilio con calle vacía ahora permitido (Opción B implementada, Card #41 CERRADO). Talonario Rosa = Picking Ticket interno, pendiente de implementar (Card #40, Nike dictamen).
- **Bit PENDIENTE_AJUSTE_DOCUMENTAL:** Dictaminado en Bit 46 por Nike. No bloquea logística. Pendiente de implementar (Card #42).
- **Banderas Rojas activas:** Ver BOARD_V5.xlsx hoja BANDERAS_ROJAS. Script rescate V5_LS_MASTER.db pendiente para lunes OF (Bit5+Bit16 en Lácteos y Centro Pet, PIN 1974 autorizado).
- **ALFA/OMEGA + Board:** Cards #45 documenta la deuda de integrar el Board en los protocolos ALFA y OMEGA. Pendiente modificar ALFA.md y OMEGA.md.

### 📢 Actualización Sesión 819 (2026-05-29)
- **Identidad Entorno P:** Título de pestaña ahora dice "Sonido Líquido V5 - Mando" (anteriormente "DESARROLLO - D"). Favicon actualizado a diseño púrpura corporativo.
- **Genoma Pedidos V6.0:** En desarrollo. Nuevos estados ES_ENTREGADO (logístico) y Bit COBRADO (contable) para modelar claramente la diferencia entre "mercadería entregada" y "pago cobrado". Ver BOARD_V5.xlsx cards 29-30.
- **Excel Snapshot:** Feature V5.9 en BACKLOG — generador de reportes Excel de pedidos solo lectura (card 31).

---

### ⚠️ MOTOR BIPOLAR — IVA Y CIRCUITO FISCAL (Doctrina 809)
El cálculo de IVA en pedidos responde al **Bit 12 (NO_FISCAL_FORCE)** del pedido, no al tipo de cliente.

| Bit 12 pedido | Circuito | Comportamiento |
|---|---|---|
| 0 (apagado) | OFICIAL / con AFIP | Aplica 21% IVA, genera factura borrador, genera remito puente |
| 1 (encendido) | INTERNO / sin AFIP | Sin IVA, sin documentos fiscales, emitir remito manual |

**Nota UI (Interfaz):** En la interfaz de Ventas (`PedidoCanvas`), el circuito INTERNO se denomina operativamente **"CIRCUITO LISTA 2"** y transforma la interfaz completa a una paleta visual **Magenta/Rosa (pink-500)** para alertar al operador de que no habrá tratamiento fiscal AFIP.

**Cliente Rosa** (OPERATOR_OK, Bit 4): siempre opera en circuito interno. El sistema vincula automáticamente el domicilio de entrega Roseti 1482 si no tiene domicilio propio.

---

### ⚠️ DIAGNÓSTICO: PRECIOS EN $0 (STRICT MODE)
Si al navegar o cotizar un producto el sistema muestra `$0` o `LISTA_0`, se debe a la activación del **Strict Mode** del Motor V5. 

**Causas y Solución:**
1. **Falta de Costo de Reposición**: El motor no puede calcular la cascada de 7 listas si el producto no tiene un costo base. 
   - *Solución*: Ingresar al **Inspector de Producto (F2)** -> Pestaña **Costos** -> Cargar **Costo de Reposición**.
2. **Falta de Segmentación del Cliente**: Si el cliente no tiene asignado un Segmento (Retail, Premium, etc.) o una Lista de Precios, el sistema no puede determinar qué nivel de la cascada aplicar.
   - *Solución*: Ingresar a la ficha del cliente y asignar **Segmento** y **Lista de Precios**.

**Contexto Producción**: Se ha detectado que una gran parte de la base de datos en Producción (V5-LS) no posee costos cargados tras el trasplante del Polizón. Se recomienda auditoría masiva de costos antes de operar.

---

# Manual Operativo V5

## Control de Cambios
- **V5.3 (Vector Update):** Implementación de Historial Vectorial y Toggle de Excel en Carga Táctica.
- **V5.8 (Omega Intelligence):** Cimientos del Pedido Inteligente, OC Fluo, Foco UX y Rentabilidad Dinámica.
- **V6.0 (Hybrid Engine):** Motor de Precios Híbrido, Jerarquía de Rendimiento, Búsqueda por SKU y Protocolo de Higiene de Datos.

## 1. Carga Táctica (Tactical Loader)
El módulo de carga rápida (`/ventas/loader`) permite la creación ágil de pedidos.

### Nuevas Funcionalidades
1.  **Historial de Cliente (Widget Reloj):**
    - Al pasar el mouse sobre el ícono de reloj (o clic derecho), se despliega el historial de los **últimos 5 pedidos**.
    - Este historial es "vivo" y se actualiza instantáneamente con cada nueva compra.
    
2.  **Exportación Excel Opcional:**
    - Casilla de verificación: **"Generar Comprobante (Excel)"**.
    - Permite elegir si se desea descargar el archivo físico `.xlsx` al guardar el pedido. Ideal para cargas masivas donde no se requiere imprimir comprobantes uno por uno.

### Teclas Rápidas
- **F3:** Buscar Cliente.
- **F4 / "+" :** Agregar Producto.
- **F10:** Guardar Pedido.

### Edición de Pedidos Existentes (v5.9)
Para modificar un pedido ya creado, abrirlo desde la lista y hacer clic en Editar. El sistema carga todos los datos y al guardar **actualiza el pedido original** — no crea uno nuevo. Para agregar una nota de anulación, buscar el ícono ✏ en el panel derecho del inspector (siempre visible).

### Clientes Rosa / Sin CUIT — Doctrina Arlequín V2 (v5.9 → 806)
Clientes informales (**sello Rosa**, Bit 4 encendido) aparecen como **AUDITADO** (verde) en el selector de pedidos aunque no tengan CUIT ni domicilio fiscal. El sistema los reconoce automáticamente por su Bit 4 (`OPERATOR_OK`) y no bloquea la operación.

El sello Rosa se infiere automáticamente si el cliente tiene segmento asignado pero carece de CUIT real. **Excepción:** si el cliente fue creado sin segmento, la inferencia no dispara — el operador debe notificarlo para asignación manual del sello (requiere acceso técnico con PIN 1974). Al crear un pedido para un cliente Rosa, el sistema activa automáticamente el circuito **INTERNO** (sin IVA) y muestra precios netos.

**Consumidor Final / MOSTRADOR:** El CUIT `00000000000` está reservado exclusivamente para el cliente MOSTRADOR/GENÉRICO. El sistema bloquea cualquier intento de asignarlo a otro cliente.

## CAPÍTULO 1: LA DOCTRINA DE INTERFAZ (DEOU)

El sistema V5 se rige por la **Doctrina de Eficiencia Operativa Unificada (DEOU)**, diseñada para maximizar la velocidad de operación y reducir la carga cognitiva del usuario.

### 1.1 Layout Tríptico
La interfaz principal se divide en tres zonas funcionales que permanecen constantes en todos los módulos operativos:

1.  **Sidebar (Navegación):** Panel izquierdo colapsable/fijo. Contiene el acceso a los módulos principales y herramientas globales.
2.  **Lista (Exploración):** Zona central. Muestra los registros en formato Grilla (Tarjetas) o Lista (Renglones). Soporta filtrado y ordenamiento rápido.
3.  **Inspector (Edición):** Panel derecho deslizante. Permite la edición en detalle del registro seleccionado sin perder el contexto de la lista.

### 1.2 Atajos de Combate
El teclado es el dispositivo primario de operación. Los siguientes atajos son globales y obligatorios:

*   **F10 (Guardar y Cerrar):** Confirma la operación actual en cualquier formulario o inspector. Si es exitoso, cierra el panel.
*   **F3 (Buscar):** Pone el foco inmediatamente en la barra de búsqueda global del módulo actual.
*   **F4 (Stack / Nuevo):**
    *   En Listas: Abre el formulario de "Nuevo Registro".
    *   En Formularios (Combos): Abre el ABM rápido de la entidad relacionada (ej: Crear un nuevo Rubro desde el selector de Rubros).
*   **ESC (Cancelar/Cerrar):** Cierra el inspector o modal actual sin guardar cambios.
*   **Ctrl + K:** Abre la Paleta de Comandos Global (Navegación rápida).

### 1.3 Semántica Visual
El sistema utiliza un código de colores estricto para diferenciar contextos y evitar errores operativos:

*   **🔵 CLIENTES (Hawe):** Tonos **Azul / Cyan**. Representa la entidad comercial y la venta.
    *   **Blanco (Esmeralda):** Cliente validado o soberano. Se activa mediante la **Regla Dual V5.2**: Bit 13 (8192 - Calibrado/LAVIMAR) o Bit 20 (1048576 - Soberanía V15).
    *   **Azul (Sello):** Cliente con CUIT compartido (Multi-Sede).
    *   **Rosa (Power Pink):** Cliente informal (Bit 19 - 524288) o validado manualmente (Niveles 9/11).
    *   **Amarillo (Alerta):** Cliente pendiente de validación o auditoría.
*   **🔴 PRODUCTOS (Manufactura):** Tonos **Bordó / Rose**. Representa el inventario, costos y producción.
*   **🟠 LOGÍSTICA (Transportes):** Tonos **Naranja**. Representa el movimiento físico de mercadería.
*   **🟢 MAESTROS (Segmentos):** Tonos **Verde / Emerald**. Representa las clasificaciones y configuraciones.
*   **🟣 AGENDA (Contactos):** Tonos **Rosa / Pink**. Representa a las personas y vínculos humanos.

---

## CAPÍTULO 2: MÓDULO CLIENTES (HAWE)

El módulo "Hawe" centraliza la gestión de la cartera de clientes, enfocándose en la velocidad de acceso y la integridad de los datos logísticos.

### 2.1 Ficha del Cliente
La ficha es el núcleo de la información comercial. Se compone de:
*   **Datos Identitarios:** Razón Social, CUIT, Condición IVA.
*   **Estado:** Activo / Inactivo (con interruptor visual).
*   **Contador de Uso:** Métrica de popularidad que ordena automáticamente a los clientes más frecuentes al tope de la lista.

### 2.2 Domicilios y Logística
Un cliente puede tener múltiples domicilios, pero se clasifican estrictamente en:
*   **Domicilio Fiscal:** Dirección legal asociada al CUIT.
    *   **Gestión:** Para modificar o dar de baja el domicilio fiscal, utilice el menú de opciones (tres puntos) o clic derecho sobre la tarjeta.
    *   **Ley de Conservación:** El sistema impedirá borrar el domicilio fiscal si no existe otra dirección activa que pueda tomar su lugar.
*   **Domicilio de Entrega:** Dirección física donde se recibe la mercadería.
*   **Gestión de Alta Capacidad (AddressSelector):**
    *   **Drag & Drop Swap:** Arrastre cualquier sucursal a la "Tarjeta Principal" para promoverla.
    *   **Edición Directa:** Clic en cualquier tarjeta para abrir el formulario de edición detallada.
    *   **Baja Logística:** Icono de papelera (Trash) para desactivar direcciones o limpiar duplicados.
    *   **Omnisearch:** Buscador reactivo integrado para localizar sucursales por calle, localidad o alias.
*   **Logística Asociada:** Cada domicilio tiene vinculado un **Transporte** predeterminado.

### 2.3 Concepto de Segmentos
Los clientes se agrupan en **Segmentos** (anteriormente "Ramos").
*   Permite clasificar la cartera por canal de venta o tipo de negocio.
*   Es un filtro primario en el explorador de clientes.

### 2.4 Administración de Segmentos
El módulo de Segmentos permite crear y editar las clasificaciones de la cartera.
*   **Ubicación:** Menú Lateral > Grupo CLIENTES > Segmentos.
*   **Interfaz Split-Pane:** La pantalla se divide en dos:
    *   **Izquierda (Lista):** Muestra los segmentos existentes.
    *   **Derecha (Inspector):** Panel fijo de edición.
*   **Operación:**
    *   Al seleccionar un segmento de la lista, se carga en el panel derecho.
    *   Para crear uno nuevo, presione el botón **+ NUEVO (INS)** o la tecla `Insert`.
    *   Para guardar, presione **Guardar (F10)**.

    *   Para guardar, presione **Guardar (F10)**.

### 2.5 Validación Fiscal (Lupa ARCA)
El sistema integra un puente directo con **AFIP/ARCA** para validar la identidad y condición tributaria.
*   **Botón Lupa:** Ubicado junto al CUIT. Al presionarlo, consulta los padrones oficiales.
*   **Feedback:**
    *   ✅ **Éxito:** Completa automáticamente Razón Social, Categoría de IVA y Domicilio Fiscal.
    *   ⚠️ **CUITs Genéricos:** Para "Consumidor Final" (`00000000000`) o "Sujeto No Categorizado" (`11111111119`), el sistema **omite** la consulta a AFIP (para evitar errores) y permite la carga manual inmediata.
*   **Regla:** Siempre intente validar los CUITs reales para evitar facturas rechazadas.

---

## CAPÍTULO 3: MÓDULO PRODUCTOS (MANUFACTURA)

El módulo de Manufactura gestiona el catálogo de artículos, sus costos y su lógica de abastecimiento.

### 3.1 Identidad e Identificación
*   **SKU (Stock Keeping Unit):** Identificador único interno. El sistema lo genera automáticamente (Secuencia "AUTO") pero permite overrides manuales.
*   **Código Visual:** Código corto de uso cotidiano (ej: "JL-500" para Jabón Líquido 5L).
*   **Es Kit:** Indicador para productos compuestos (Combos).

### 3.2 Clasificación: Rubros
*   **Jerarquía:** Los productos se organizan en un árbol de **Rubros** (Categorías).
*   **Regla de "No Orfandad":** Todo producto debe pertenecer a un rubro.

### 3.3 Precios: La Fórmula 1.105
El sistema calcula los precios de venta en cascada partiendo del costo:

1.  **Costo Reposición (Neto):** Valor de compra al proveedor.
2.  **Precio Mayorista:** `(Costo + Margen%) + IVA`.
3.  **Precio Distribuidor:** `Precio Mayorista * 1.105`.
4.  **Precio Minorista:** `(Precio Distribuidor / 0.90) * 1.105`.

*El simulador de precios en el inspector permite visualizar estos valores en tiempo real al ajustar costos o márgenes.*

### 3.4 Logística Industrial
Para soportar la compra y el stock, se definen dos unidades:
*   **Unidad de Stock:** Cómo se cuenta en el inventario (ej: "Unidad", "Litro").
*   **Unidad de Compra:** Cómo se pide al proveedor (ej: "Caja", "Tambor").
*   **Factor de Conversión:** Relación numérica entre la unidad de compra y la de stock (ej: 1 Caja = 12 Unidades).

### 3.5 Satélites
*   **Proveedores:** Entidades que abastecen los productos (vinculados como "Proveedor Habitual").
*   **Depósitos Internos:** Ubicaciones físicas o virtuales donde reside el stock (ej: "Central", "Móvil").

---

## CAPÍTULO 4: MÓDULO AGENDA & MAESTROS

Este capítulo abarca las entidades transversales que dan soporte a los módulos operativos.

### 4.1 Agenda de Contactos
Gestiona a las **Personas** físicas, independientemente de si son clientes, proveedores o empleados.
*   **Vínculos:** Una persona puede estar vinculada a múltiples entidades (ej: Un contacto puede ser "Vendedor" en la empresa y "Comprador" en un Cliente).
*   **Tipos de Contacto:** Roles definibles (Dueño, Encargado, Vendedor, Chofer).
*   **Cargos y Roles:** Al elegir un cargo (ej: Compras) en la ficha de contacto, el sistema actualiza automáticamente la tarjeta en el Dashboard. Si el cambio no se refleja, verificar que se haya presionado el botón de guardado del vínculo específico.

### 4.2 Unidades de Medida
Tabla maestra que define las magnitudes físicas permitidas en el sistema:
*   **UN:** Unidad (Discreto).
*   **LT:** Litro (Volumen).
*   **KG:** Kilogramo (Peso).
*   **MT:** Metro (Longitud).

### 4.3 Tasas de IVA
Configuración centralizada de alícuotas impositivas para asegurar consistencia fiscal:
*   **21.0%:** IVA General.
*   **10.5%:** IVA Reducido.
*   **27.0%:** IVA Diferencial.
*   **0.0%:** Exento / No Gravado.

---

### Capítulo 4 — Adenda Arlequín V2 (2026-05-04)
El sistema bloquea productos duplicados por nombre canónico (BOW).
Si al crear un producto el sistema reporta "nombre equivalente existe",
verificar el catálogo antes de insistir — puede ser el mismo producto
con tipeo diferente.
Variantes de talle/presentación son productos distintos — darlos de alta
con nombres que incluyan el diferenciador explícito (ej: "Guante Nitrilo L x100").

---

## CAPÍTULO 5: ESTRATEGIA DE DATOS Y CONTINGENCIA

Para garantizar la operación continua incluso sin conexión a internet o ante fallos del servidor central (IOWA), el sistema V5 implementa la **Doctrina de Blindaje de Datos**.

### 5.1 Modo Híbrido (Offline First)
La operación diaria no depende de la nube.
*   **Trinchera (Local):** La facturación, carga de pedidos y gestión se realizan sobre una base de datos local de alta velocidad (`pilot.db`).
*   **Respaldo (Nube):** La sincronización con el servidor central es asíncrona. Se suben los datos cuando la conexión es estable, pero no bloquea el trabajo si se corta internet.


### 5.2 Semillas Maestras (Golden Seeds)
Son el mecanismo de seguridad último ("Arca de Noé").
*   Al final de cada sesión o hito importante, el sistema exporta el conocimiento clave (Clientes, Productos, Deudas) a archivos **CSV planos e inmutables**.
*   **Recuperación:** Si la base de datos local se corrompe y la nube es inaccesible, el sistema puede "Resetearse" y reconstruirse por completo en segundos importando estas semillas.
*   **Ubicación:** Carpeta `BUILD_PILOTO/data`.

---

## CAPÍTULO 6: MÓDULO VENTAS (TACTICAL LOADER)

El módulo de ventas está diseñado para la velocidad ("Excel Killer"). Prioriza la carga rápida mediante teclado y la inteligencia contextual.

### 6.1 Dashboard de Pedidos
El centro de control de ventas (`Tablero Pedidos`) ofrece una vista densa y rápida del estado del negocio.
*   **Semáforo de Estados:**
    *   🟢 **PENDIENTE (Verde):** Pedido en proceso, borrador o recién ingresado. Requiere acción.
    *   🟡 **CUMPLIDO (Amarillo):** Pedido finalizado, entregado o facturado. Ciclo cerrado.
    *   🔴 **ANULADO (Rojo):** Pedido cancelado (baja lógica).
    *   🟣 **INTERNO:** Pedidos administrativos o de movimiento interno.
*   **Filtros:** Barra superior para filtrar rápidamente por estado.

### 6.2 Cargador Táctico / Ficha del Pedido
Interfaz de alta velocidad para la toma de pedidos. Evolucionada de una grilla simple a una **Ficha Soberana**.
*   **Identidad Dinámica**: El encabezado muestra **"FICHA DEL PEDIDO #ID"** al consultar pedidos existentes, permitiendo una rápida auditoría visual.
*   **Navegación Mouse-Free (Foco UX)**:
    - Selección de Cliente -> Salto automático a campo **OC**.
    - `ENTER` sobre OC -> Salto automático al primer **SKU** del cuerpo.
    - `ENTER` sobre SKU -> Salto a **Cantidad**.
*   **Inteligencia de Precios**: Al seleccionar un cliente y un producto, el sistema busca automáticamente la **última venta** real de ese producto a ese cliente y sugiere ese precio (respetando la historia comercial real).
*   **Análisis de Rentabilidad (F8)**: Panel dinámico que calcula Utilidad Bruta y Margen por ítem en tiempo real basándose en el **Costo de Reposición** actual.
*   **Consumidor Final**: Lógica especial que omite validaciones estrictas de CUIT/Domicilio para ventas rápidas de mostrador.
*   **Exportación**: Generación instantánea de Excel con el detalle del pedido para procesar en sistemas legacy o enviar por mail.

### 6.3 Tablero Pedidos — Vista "Ambos" + Circuito Interno Visible (Sesión 829)

El tablero ahora presenta una vista unificada por defecto:

*   **Botón "Ambos" (Default):** Seleccionado automáticamente al abrir el tablero. Muestra todos los pedidos sin filtro, diferenciando visualmente cuáles son Oficiales (Blanco) y cuáles Internos (Rosa).
    - **Styling:** Gradiente `emerald-600 → pink-600` para indicar riqueza visual (cobertura total).
    
*   **Botón "Circuito Oficial":** Filtra solo pedidos con IVA (Blanco, RI, CUIT real).
    - **Styling:** `bg-emerald-600` (verde).
    
*   **Botón "Circuito Interno":** Filtra solo pedidos sin IVA (Rosa, informal, Bit 12 encendido).
    - **Styling:** `bg-pink-600` (fucsia). Cambio visual desde sesión 829 para claridad operativa.
    - **Indicador de fila:** Los pedidos Rosa aparecen con fondo sutilmente oscuro (`bg-pink-950/30`) y borde izquierdo rosa (`border-l-2 border-pink-500/40`) para identificación instantánea.

**Caso de uso:** Al inicio de la jornada, el operador ve el tablero completo ("Ambos"). Si necesita enfocarse solo en rosa (facturación manual) o solo en oficial (ARCA), usa los botones de filtro sin perder contexto.

### 6.4 Herramientas de Gestión de Sesión
Para evitar errores por datos persistentes ("Datos viejos"), se incorporaron controles explícitos en el pie de página:

1.  **Limpiar Pantalla (Icono Papelera):**
    - Este botón realiza un "Hard Reset" del formulario.
    - Borra todos los ítems, deselecciona el cliente y **elimina la memoria temporal** del navegador.
    - Úselo si nota que el sistema carga información de un pedido anterior.


2.  **Generar Excel (Toggle):**
    - Ubicado junto al botón Guardar.
    - Si está activo (Verde), al guardar el pedido se descargará automáticamente una copia en Excel.

---

## CAPÍTULO 7: MOTOR DE PRECIOS V5 (LA ROCA Y LA MÁSCARA)

El sistema V5 abandona las listas de precio estáticas en favor de un cálculo dinámico basado en costos y estrategias.

### 7.1 Filosofía de Cálculo
El precio sugerido se construye en tres capas:
1.  **"La Roca" (Precio Piso):** Es el valor mínimo técnico. `(Costo Reposición * (1 + Margen))` o el **Precio Fijo Manual** si existe (Prioridad Divina).
2.  **"K-Factor" (Estrategia):** Multiplicador según el perfil del cliente.
    *   **Mayorista Fiscal:** Aplica IVA Discriminado (21% / 10.5%).
    *   **Mayorista X:** Aplica IVA Compartido ("Saborizado").
    *   **MELI Clásico:** Aplica Markup (+40%) y Costo Fijo por venta.
3.  **"La Máscara" (Ingeniería Inversa):** El sistema muestra un **Precio de Lista Inflado** calculado matemáticamente para que, tras aplicar el descuento visual prometido al cliente (ej: 20%), el precio final coincida exactamente con el objetivo de rentabilidad.

### 7.2 Herramienta "Magic Math"
En el Cargador Táctico, los campos numéricos (Cantidad y Precio) funcionan como una calculadora inteligente (estilo Excel).
*   **Suma rápida:** Escriba `10 + 5` → Resultado: `15`.
*   **Cálculo de IVA:** Escriba `100 * 1.21` → Resultado: `121`.
*   **División:** Escriba `5000 / 3` → Resultado: `1666.67`.
*   *Indicador visual:* Aparecerá un símbolo `fx` azul mientras escribe una fórmula.

### 7.3 Overrides (Excepciones)
Si un producto tiene asignado un **Precio Fijo Override**, el motor ignorará cualquier cálculo de costo/margen y usará ese valor como base inamovible ("La Roca"). Esto es útil para ofertas puntuales o productos con precio regulado.

### 7.4 Motor Híbrido V6 (Jerarquía de Poder)
La versión 6 introduce el **CM Objetivo (Contribución Marginal)** y la **Propuesta por Rubro. La jerarquía de decisión del motor es:**

1.  **PRECIO FIJO MANUAL:** Si hay un valor en `precio_fijo_override`, se usa sin preguntar.
2.  **CM OBJETIVO (Artesanal):** Si no hay precio fijo, pero hay un `% CM Objetivo` en el producto, el sistema despeja el precio para garantizar ese margen sobre el costo.
3.  **MARGEN POR RUBRO:** Si el producto no tiene CM propio, usa el `% Margen Default` del Rubro al que pertenece (ej: Todos los Guantes al 35%).
4.  **MARGEN PRODUCTO (Legacy):** Si todo lo anterior falla, usa el margen mayorista individual de la ficha.

---

## CAPÍTULO 11: PROTOCOLO DE HIGIENE DE DATOS (ANTI-FRANKENSTEIN)

Para evitar la desincronización de datos entre la PC local y la nube (IOWA), se deben seguir estas reglas de oro:

### 11.1 El Local manda
La base `pilot.db` es la fuente de verdad de la **operación diaria** y los **precios**. La nube (IOWA) es la fuente de verdad del **maestro purgado** (Rubros y SKUs).

### 11.2 Sincronización Obligatoria
Antes de iniciar una carga masiva o después de cambios estructurales en rubros, ejecute el script de reconciliación:
```bash
python scripts/reconcile_master_data.py
```
Este script asegura que:
1.  Los rubros locales coincidan con los de la nube.
2.  Los productos nuevos en local se informen a la nube.
3.  Los SKUs se mantengan alineados.

### 11.3 Prevención de Duplicados
Al cargar productos nuevos, siempre verifique el **SKU**. No cree productos con el mismo nombre y SKU diferente; el sistema lo detectará como una anomalía en el próximo reporte de auditoría.

---

## CAPÍTULO 8: ACCESO REMOTO MULTIJUGADOR (LAN)

### 8.1 Concepto
El sistema V5 permite que múltiples usuarios (ej: Administración + Ventas + Depósito) trabajen simultáneamente sobre la misma base de datos desde distintas computadoras de la red local (WiFi o Cable), sin necesidad de Internet.

### 8.2 Cómo Iniciar (Lanzador Automático)
Para habilitar el modo red, **NO use el comando habitual**.
1. En la PC Principal (Servidor), cierre todas las ventanas negras.
2. Abra una sola terminal y ejecute:
   `.\scripts\run_lan.ps1`
3. El sistema abrirá automáticamente el Servidor y la Web configurados para la red.

### 8.3 Conexión desde otras PC
El script mostrará una dirección IP (ej: `http://192.168.0.X:5173`).
Ingrese esa dirección exacta en el navegador de las otras computadoras.

**Usuarios Disponibles:**
*   Administrador: `admin` / `admin123`
*   Operador de Carga: `operador` / `operador123` (Rol restringido).

### 8.4 Solución de Problemas
*   **"Error al conectar":** Generalmente es el Firewall de Windows en la PC Principal. Ejecute el script `scripts\fix_access.ps1` como Administrador para abrir los puertos 8000 y 5173.
*   **"Sitio no carga":** Verifique que ambas PC estén en la misma red WiFi.

---

## CAPÍTULO 9: PROTOCOLO UNIVERSAL DE ARRANQUE (CROSS-PLATFORM)

A partir de la fase de estandarización, el sistema abandona la dependencia exclusiva de PowerShell (`.ps1`) para el arranque del backend.

### 9.1 Lanzamiento en Windows
Abre una terminal (PowerShell o CMD) y ejecuta:
```powershell
python scripts/run_dev.py
```
*Tip: Puedes hacer clic derecho sobre `run_dev.py` y seleccionar "Abrir con PowerShell".*

### 9.2 Lanzamiento en Mac / Linux
Abre la **Terminal** (CMD + Espacio > "Terminal") y ejecuta:
```bash
python3 scripts/run_dev.py
```
*Nota: En Mac, usualmente el comando es `python3` en lugar de `python`.*

### 9.3 Respaldos Cross-Platform
Los comandos de respaldo también son universales:
*   **Local:** `python3 scripts/backup.py`
*   **Drive:** `python3 scripts/backup_drive.py`

### 9.4 El Frontend
Se lanza con el nuevo script universal:
```bash
python scripts/run_front.py
```
*Tip: Al igual que el backend, puedes hacer botón derecho sobre `run_front.py` y correrlo con Python.*

### 9.5 Acceso Remoto (Modo LAN)
Para que otros se conecten, el servidor debe estar en modo LAN. 
*   **Acceso Rápido:** Use el icono **LAN_SERVER_V5.bat** creado en su Escritorio.
*   **Manual:** Ejecute `python scripts/run_lan.py` desde la raíz.
*   *Nota:* Este script configura automáticamente las IPs para que Tomás u otros operadores puedan ingresar desde sus puestos.

---

## CAPÍTULO 10: DOCTRINA DE PEDIDOS (V5 TÁCTICO)

El nuevo Módulo de Pedidos integra la filosofía de alta velocidad del Comandante.

### 10.1 Cargador Táctico (Speed-Grid)
Diseñado para la toma de pedidos telefónica o presencial ultra-veloz.
- **Magic Math:** El sistema autocompleta el precio basándose en la **última venta real** a ese cliente.
- **Navegación:** Arreglo vertical optimizado para uso exclusivo del teclado.

### 10.2 Identidad de Estados
- **Verde Esmeralda:** Pedidos normales/pendientes.
- **Rosa Chicle Fluo:** Alerta de **Entrega Comprometida a Futuro**. No pasar por alto en la logística diaria.
- **Facturación:** Selector explícito entre Interno (X) y Fiscal (Facturable) integrado en el inspector.



---

## CAPÍTULO 11: GESTIÓN DE DOCUMENTOS (ETIQUETADO PDF)

El sistema V5 incluye herramientas para la intervención de documentos generados por sistemas externos (como AFIP/ARCA) que requieren datos de gestión adicionales.

### 11.1 Etiquetador Express de OC/PO
Esta utilidad permite 'sellar' números de Orden de Compra o Purchase Order en facturas PDF que vienen bloqueadas para edición.

*   **Ubicación de Acceso:** Carpeta `tools/arca_oc_stamper/` (**ETIQUETADOR_PDF.bat**).
*   **Operación:**
    1. Seleccione el archivo PDF original.
    2. Elija el prefijo deseado (OC o PO).
    3. Ingrese el número de referencia.
    4. El sistema generará una copia con el sufijo _etq en el nombre.
*   **Lógica de Posicionamiento:** El dato se inserta en la esquina superior derecha del documento (Original), alineado con la cabecera fiscal, asegurando visibilidad clínica sin interferir con la validez del comprobante.

---

## APÉNDICE: HERRAMIENTAS DE ALTA VELOCIDAD (V5.2)
### 1. Búsqueda en Maestros (Cantera)
- Si un producto o cliente no aparece en la búsqueda local, haga clic en el botón naranja **'Buscar en Maestros'**.
- Esto consultará la 'Cantera' (base de datos masiva). Al seleccionar un registro, el sistema lo importará automáticamente a su operativa local.

### 2. Lanzador Multijugador
- Use el ícono **'LAN_SERVER_V5'** para permitir que otros puestos de la oficina se conecten.
- El script abrirá dos ventanas: una para el servidor de datos y otra para la interfaz web.

---

## CAPÍTULO 12: DOCTRINA FISCAL Y ESTADOS TÁCTICOS (V6.7)

### 12.1 Doctrina "Fiscal First"
El sistema opera bajo la premisa de que **todos los pedidos son Fiscales (IVA 21%)** por defecto.
- **Estado PENDIENTE (Verde):** Asume Factura B (Consumidor Final) y calcula IVA automáticamente.
- **Auto-Curación:** Al abrir un pedido viejo que no tenía IVA calculado, el sistema lo corregirá automáticamente.

### 12.2 Código de Colores y Semántica
La interfaz ha sido ajustada para evitar errores operativos visuales:

- **PEDIDO FIRME (Verde Esmeralda):** Pedido activo con deuda fiscal generada.
- **INTERNO / SIN IVA (Rosa Vibrante/Magenta):** Pedido interno que **NO** genera deuda fiscal visual. El IVA se elimina del total.
- **ANULADO (Rojo Profundo):** Pedido cancelado. No genera deuda y queda inactivo.
- **PRESUPUESTO (Púrpura):** Cotización formal con IVA proyectado.

### APÉNDICE S: CONSCIENCIA SITUACIONAL (PROTOCOLO 4-BYTES)
**Implementado:** v14-B (Feb-2026)

Para evitar la desincronización de código y datos al saltar entre terminales (Casa / Oficina / Notebook), el sistema utiliza un tablero de bits de estado persistente.

1. **session_status.bit:** Archivo binario en `C:\dev\` que almacena el "último rastro" de consciencia del sistema.
2. **Detección de Origen:** El sistema identifica automáticamente el host actual. Si el host detectado no coincide con el último origen guardado, el cargador `DESPERTAR_DOBLE.bat` activará una **Alerta de Desincro**, obligando a realizar un Git Pull y verificar la paridad de la base de datos (428 KB).
3. **Carta Momento Cero:** Si el Bit 2 está activo, existe un mensaje prioritario en `CARTA_MOMENTO_CERO.md` que debe ser leído antes de iniciar cualquier operación táctica.

### 12.3 Utilidades Maestras: Protección de Historial
Para garantizar la integridad de los datos, el sistema implementa una protección automática sobre clientes que ya han operado (registros históricos).
- **Grisado Visual**: Los registros protegidos aparecen en color gris en la lista de bajas.
- **Bloqueo de Borrado**: No es posible eliminar físicamente un cliente que tenga historial comercial. El botón de eliminación aparecerá deshabilitado.
- **Rescate de Registros**: Si necesita volver a operar con un cliente que fue dado de baja, use el botón **RESCATAR**. Esto lo devolverá a la lista activa sin riesgos de pérdida de datos.

---
**ESTADO DE DOCTRINA:** VANGUARD (V14.8.4)

### 12.4 Soberania Operativa V14.8.4 (Actualizacion 18-03-2026)
A partir de esta version, el sistema actua como un Escudo Proactivo. El color y estado del cliente dependen de la calidad de la carga del operador, no de la validacion AFIP.

**Promocion Automatica al Estado Veterano:**
Al guardar un cliente con los siguientes 4 pilares completos, el sistema lo promueve automaticamente a "Veterano" (color blanco):
1. Nombre (Razon Social)
2. Domicilio Fiscal con calle
3. Lista de Precios asignada
4. Segmento comercial asignado

El cliente deja de ser "Virgen" y pasa a ser reconocido como operativo por el solo hecho de tener la carga completa, **sin necesidad de usar la lupa AFIP**.

**Lupa AFIP - Comportamiento Actualizado:**
Si el cliente ya tiene una direccion fiscal cargada manualmente, la lupa ahora muestra una confirmacion antes de sobreescribirla con el dato oficial de ARCA. Esto protege las correcciones que el operador haya hecho (ej: "Av Cordoba" vs "Cordoba Av" que devuelve AFIP).
- **Aceptar**: Usa el dato de ARCA.
- **Cancelar**: Conserva la correccion manual. Solo se actualizan datos fiscales (IVA, Razon Social).


---

## CAPÍTULO 13: REMITOS MANUALES Y EDICIÓN DE INGESTA

### 13.1 Remito Manual (Serie 0015)
Diseñado para envíos de mercadería que no poseen una factura electrónica asociada (ej: Clientes Rosa).
*   **Ubicación**: Menú Lateral > GRUPO PEDIDOS > Remito Manual.
*   **Operación**:
    1. Seleccione el Cliente (o cree uno nuevo con el botón "+").
    2. Elija la dirección de entrega (el sistema carga automáticamente los domicilios del cliente).
    3. Cargue los productos y cantidades.
    4. Presione "Emitir y Descargar". El PDF saldrá con la serie 0015.

### 13.2 Corrigiendo la Ingesta Automática
Si al subir una factura el sistema lee mal un nombre o cantidad:
*   **Edición Directa**: Haga clic sobre la descripción o cantidad en la tabla de resultados para corregirla.
*   **Agregar Ítems**: Use el botón "Agregar Ítem Manual" si falta algún producto en la detección.
*   **Eliminar**: Use la "X" roja para quitar líneas que no desea remitir.
## CAPÍTULO 14: SEGURIDAD Y CIERRE (OMEGA 5.2)
A partir de Marzo 2026, las sesiones de desarrollo y carga crítica se rigen por el **Protocolo Blindado**.

### 14.1 Auditoría de Ojo de Halcón
- Antes de cerrar, el sistema ejecuta el script `audit_v5.py`.
- **Regla de Oro**: No se permite el cierre si el disco físico tiene cambios que no han sido registrados en el control de versiones (Git).

### 14.3 Protocolo ALFA-LITE (V5.7 Speed)
Para optimizar el flujo de trabajo en sesiones de mantenimiento menor, se ha habilitado la **Vía Rápida (ALFA-LITE)**:
- **Cuándo aplica**: Ajustes de interfaz, correcciones de texto o bugfixes que no toquen el esquema de la base de datos.
- **Ventaja**: Omite la ejecución completa del Canario, basándose en la última certificación de integridad lograda en la sesión previa.
- **Activación**: Se solicita explícitamente al agente GY al inicio de la jornada.

### 14.4 El Ticket de Salida
- Tras finalizar la subida de datos, el sistema emite un **Ticket de Salida** físico (`git show`). Este documento certifica que el trabajo está a salvo en el servidor y listo para ser "despertado" en otra terminal (Oficina/Casa).

### 13.3 Edición de Remitos Emitidos (Doble Clic)
Si necesita corregir datos de un remito que ya fue emitido pero aún no ha salido del depósito (estado **BORRADOR**):
1.  Vaya a **LOGÍSTICA > Remitos**.
2.  Busque el remito en la lista y haga **doble clic** sobre el renglón.
3.  Se abrirá el modal de **Soberanía Total** donde podrá corregir:
    - **Número Legal**: Para corregir errores de tipeado.
    - **CAE / Vto CAE**: Datos fiscales.
    - **Bultos y Valor Declarado**: Datos logísticos críticos.
    - **Transporte y Dirección**: Destino del envío.
4.  **Confirmación**: Presione "Actualizar Remito" para persistir los cambios. El sistema actualizará el PDF automáticamente en la próxima descarga.

### 13.4 Sovereign Address Hub (V5.2 GOLD)
El padrón de domicilios ahora es independiente y soberano, funcionando como una base de datos centralizada de logística.
*   **Siembra Inicial**: El sistema ha sido cargado con todos los domicilios históricos.
*   **Ubicación**: Accesible desde **Maestros > Soberano Hub**.
*   **Logística Maps**: 
    - **Pins Dinámicos**: Los domicilios muestran un PIN de mapa. Si es **Cian**, el link fue verificado manualmente. Si es **Esmeralda**, fue autogenerado por el sistema.
    - **Validar en Mapa**: Dentro del diálogo de edición, el botón de lupa permite una verificación visual inmediata antes de guardar.
*   **Gestor de Relaciones (N:M)**: 
    - Al hacer clic en el contador de **Vínculos**, se abre un gestor que permite "Enganchar" múltiples clientes a una misma dirección física.
    - Ideal para sucursales compartidas o grupos empresarios (ej: Poblet y Gelato compartiendo fiscalía).
*   **SEO Doctrine (F10)**: En cualquier formulario de domicilio, presione **F10** para guardar y cerrar instantáneamente.

## CAPÍTULO 15: CIMIENTOS DEL PEDIDO INTELIGENTE (V5.8)
A partir de la versión 5.8, el sistema incorpora inteligencia logística basada en el genoma de 64 bits.

### 15.1 El Observador de Oficina (Poka-Yoke Roseti)
El sistema ahora reconoce automáticamente el "Centro de Gravedad" operativo (**Roseti 1482**).
- **Activación**: Al seleccionar un domicilio marcado como oficina (Bit 7), el panel de logística se configura instantáneamente en modo **Retiro en Planta**.
- **Beneficio**: Elimina el error humano de cargar fletes externos o transportes para retiros locales, colapsando el árbol de selección de transporte para mayor claridad.

### 15.2 Mandato de Orden de Compra (OC)
Para clientes con requisitos administrativos estrictos (Bit 6), el sistema actúa como un guardián:
- **Alerta Neón Blue**: Si un cliente requiere OC obligatoria y el campo está vacío, el campo mostrará un **borde azul cian fluo** con sombra pulsante. El asterisco rojo indica obligatoriedad persistente.
- **Validación**: Esta marca es crítica para asegurar que no se emitan remitos que luego sean rechazados por falta de referencia legal.

### 15.3 Herencia Logística y Sello de Confianza
- **Transporte Habitual**: El perfil del cliente ahora permite definir un transportista predeterminado. Al crear un pedido, el sistema lo selecciona automáticamente.
- **Los Albertos (Certificados)**: Los transportes recomendados (Bit 3) aparecen destacados con un sello de confianza ("Alberto") en los buscadores dinámicos.

## 16. F4 CONTEXTUAL EN PEDIDO CANVAS (V5.9 — 14/04/2026)
La tecla F4 en la pantalla de carga de pedidos tiene comportamiento inteligente según el contexto del cursor:

| Foco activo | Acción de F4 |
|---|---|
| Campo SKU o Descripción del ítem | Abre formulario de **Alta de Producto** |
| Resultado de búsqueda de producto visible | Abre formulario de **Alta de Producto** |
| Campo de cliente | Abre modal de **Búsqueda de Cliente** |
| Cualquier otro campo | Sin acción (no abre nada por defecto) |

**Regla de prioridad**: La búsqueda de producto tiene precedencia. Solo si el foco está explícitamente en el campo de cliente se abre el modal de cliente.

## 17. RUBRO OBLIGATORIO EN FICHA DE PRODUCTO (V5.9 — 14/04/2026)
El campo **Rubro** en `ProductoInspector` es obligatorio para guardar un producto.

* **Indicador visual**: Asterisco rojo `*` en el label del selector.
* **Validación**: Si se intenta guardar sin rubro, el selector muestra un ring rojo (`ring-1 ring-rose-500`) y un mensaje de error debajo.
* **Estado reactivo**: `rubroError` se limpia automáticamente al seleccionar un rubro válido.

### Capítulo 13 — Adenda Arlequín V2 (2026-05-04)
La ingesta de facturas PDF es READ-ONLY para productos.
Flujo obligatorio:
1. Si la factura tiene pedido → vincular (VINCULAR_EXISTENTE)
2. Si no tiene pedido → crear pedido primero → volver a ingestar
3. Si un producto del PDF no existe en catálogo → darlo de alta
   desde Módulo Productos → volver a ingestar
El sistema nunca crea productos automáticamente desde una factura.

## 18. MODAL RESOLVER ÍTEMS DE FACTURA (Sesión 798-OF, 2026-05-07)

Al ingresar una factura PDF que contiene ítems, el sistema abre el modal **RESOLVER ÍTEMS DE FACTURA** para vincular cada ítem al catálogo interno.

### Operación del modal

1. El modal muestra un ítem por vez con su descripción, cantidad, precio y subtotal como referencia (read-only).
2. El campo buscador inicia vacío. El operador puede:
   - Tipear libremente SKU o descripción para filtrar el catálogo.
   - Hacer click en el ícono copy junto a la descripción para copiarla al buscador automáticamente.
3. Al seleccionar un producto de la lista, el ítem queda vinculado y el modal avanza al siguiente.
4. Al completar todos los ítems, se cargan en el pedido para revisión antes de guardar.

### Atajos de teclado en el modal

| Tecla | Acción |
|-------|--------|
| **F4** | Abre ventana satélite de Alta de Producto con el término de búsqueda actual |
| **ESC** | Cancela la resolución y vuelve a la vista de ingesta |

### Nota operativa

Si un producto de la factura no existe en el catálogo, usar F4 para darlo de alta desde la ventana satélite. Al guardar el producto nuevo, volver al modal y buscarlo por SKU o descripción.

---

## 19. DETECCIÓN DE FACTURA DUPLICADA EN INGESTA (Sesión 799-CA, 2026-05-08)

Cuando el operador sube un PDF de factura a través de la pantalla de ingesta, el sistema verifica **antes de procesar** si esa factura ya existe en la base de datos, identificándola por el par único `punto de venta + número de comprobante`.

### ¿Qué ve el operador?

Si la factura ya está registrada, el sistema **no la procesa de nuevo**. En cambio, muestra un mensaje de advertencia indicando:

- Que la factura ya existe en el sistema.
- El identificador del registro existente (para poder localizarlo).

El operador puede entonces navegar al comprobante ya registrado para revisarlo o continuar con otra operación. **No se genera un duplicado.**

### ¿Por qué ocurre esto?

El caso típico es cuando una factura fue procesada en una sesión anterior y el operador vuelve a subir el mismo PDF por error (archivo repetido, copia del PDF, etc.). El sistema protege la integridad del registro evitando duplicados silenciosos.

### ¿Qué hacer si aparece este mensaje?

1. **Verificar** que el PDF que se intenta subir no es el mismo que ya fue ingresado.
2. Si es un comprobante diferente pero con igual número (ej: un proveedor reusó un número), **contactar al proveedor** — es una irregularidad fiscal.
3. Si se trató de un error propio: cerrar el diálogo y seleccionar el PDF correcto.

### Código técnico del evento

El sistema devuelve código `FACTURA_DUPLICADA` (HTTP 409). Este código es diferente a otros errores de conflicto (como pedidos duplicados) — cada uno tiene su mensaje y navegación específicos.

---

## CAPÍTULO 20: MANTENIMIENTO E INDEPENDENCIA OPERATIVA (Sesión 801, 2026-05-10)

Para garantizar que cada terminal operativa (como la máquina de Tomy) cuente con la última versión del sistema sin requerir intervenciones técnicas complejas de nivel administrador, se ha implementado el workflow de **Actualización Autónoma**.

### 20.1 Actualización con un click (ACTUALIZAR_V5.bat)

En la carpeta raíz del sistema (`C:\dev\Sonido_Liquido_V5` o equivalente), se encuentra el archivo **ACTUALIZAR_V5.bat**.

**Procedimiento:**
1. Cerrar todas las ventanas del sistema (Backend, Frontend y Navegador).
2. Ejecutar (doble click) el archivo **ACTUALIZAR_V5.bat**.
3. El sistema realizará automáticamente un `git fetch` y `git pull` desde la rama principal de Desarrollo (`main`).
4. Si la actualización es exitosa, aparecerá el mensaje `[OK] Sistema actualizado correctamente`.
5. Si ocurre un error (usualmente por cambios locales sin guardar que generan conflicto), el script mostrará una `[ALERTA]` — en este caso, contactar a soporte técnico.

**Frecuencia recomendada:** Ejecutar al inicio de cada jornada laboral para asegurar la paridad con los últimos bugfixes de Desarrollo.

### 20.2 Diagnóstico de Repositorios
Se ha detectado que existen instancias que operan sobre repositorios de GitHub independientes (ej: `v5-ls-Tom` para producción y `Sonido_Liquido_V5` para desarrollo). 
- El script de actualización está configurado para el repositorio local actual. 
- Para verificar en qué repositorio se encuentra la terminal, consulte el rastro en la **Caja Negra** de la sesión.

---

## CAPÍTULO 21: DOCTRINA ARLEQUÍN V2 — JERARQUÍA DE CLIENTES (Nike 806, 2026-05-13)

### 21.1 El semáforo de colores de clientes

El sistema clasifica cada cliente según su genoma (`flags_estado`) en tiempo real:

| Color | Condición | Qué puede hacer |
|---|---|---|
| **Blanco/Esmeralda** | Bit 2 encendido (`GOLD_ARCA`) | Operar con IVA, ARCA, factura electrónica completa |
| **Rosa** | Bit 4 encendido (`OPERATOR_OK`) | Operar sin CUIT ni domicilio fiscal. Circuito INTERNO automático |
| **Amarillo** | Sin Bit 2 ni Bit 4 | Incompleto. El sistema exige completar datos para operar |
| **Azul** | Bit 5 (`MULTI_CUIT`) | CUIT compartido / multi-sucursal |

### 21.2 ¿Cuándo se infiere Rosa automáticamente?

El sistema asigna el sello Rosa sin intervención del operador cuando:
- El cliente **no es Gold** (Bit 2 apagado)
- Tiene un **segmento asignado**
- **No tiene CUIT válido** (menos de 10 dígitos)

Esto ocurre al guardar la ficha del cliente. Una vez asignado, el sello Rosa no se quita aunque después se cargue un CUIT — la transición Rosa→Blanco requiere validación ARCA explícita.

### 21.3 MOSTRADOR / Consumidor Final

El cliente **MOSTRADOR/GENÉRICO** usa el CUIT especial `00000000000` y es el único autorizado a tenerlo. Si un operador intenta crear o modificar otro cliente con ese CUIT, el sistema lo bloquea con un error explicativo.

El Consumidor Final nace directamente como **Blanco** (Gold) — nunca pasa por el estado Rosa.

### 21.4 Cómo completar un cliente Amarillo

Si un cliente aparece en amarillo (badge incompleto), abrir su ficha y completar:
1. **CUIT** válido (11 dígitos)
2. **Condición IVA**
3. **Segmento** comercial
4. **Domicilio Fiscal** activo

Al guardar con los 4 campos completos, el sistema lo promueve automáticamente y habilita el circuito fiscal.

---

## Clientes Rosa / OPERATOR_OK (Bit 4)
*Sellado: Sesión 808 — 2026-05-15*

Los clientes marcados con Bit 4 (`OPERATOR_OK`) son clientes informales sin CUIT ni circuito AFIP (ej: Rosa). Al guardar un pedido para estos clientes:

- **No se genera borrador de factura** — no tienen CUIT, no pueden tener comprobante AFIP.
- **No se crea remito puente automático** — el operador emite remito manual si corresponde.
- El sistema muestra una notificación de advertencia recordando la situación.
- El botón "Guardar e Imprimir" no aparece en su flujo (no hay factura que imprimir).

Para identificar un cliente OPERATOR_OK: `flags_estado & 16 == 16`.

---

## CAPÍTULO 22: ALTA RÁPIDA F4 DESDE PEDIDOS (Sesión 811, 2026-05-19)

Al presionar F4 con el campo Cliente en foco desde PedidoCanvas, se abre el formulario de alta
de cliente en modo modal. El cliente creado queda correctamente:
- **Activo** (Bit 0 encendido, `activo=True`).
- **Con CUIT null** (no vacío) si no tiene CUIT real — el campo llega limpio al backend.
- **Con sello Rosa** si corresponde (el backend infiere `OPERATOR_OK` automáticamente).

El cliente se selecciona automáticamente en el pedido al cerrar el modal.

---

## CAPÍTULO 23: CUIT AUTOMÁTICO PARA CONSUMIDOR FINAL (Sesión 811, 2026-05-19)

Al crear o actualizar un cliente con condición IVA "Consumidor Final" sin CUIT, el backend
asigna automáticamente el CUIT genérico `00000000000`.

No es necesario que el operador lo ingrese manualmente. El sistema lo aplica en silencio
antes de calcular los flags de identidad.

---

## CAPÍTULO 24: CONTROL DE PEDIDOS CERRADOS Y FIX DE ALTURA (Sesión 817 OF, 2026-05-27)

### 24.1 Badge de Estado en Ficha del Pedido
En el Cargador Táctico (`PedidoCanvas.vue`), al cargar un pedido existente, la cabecera muestra ahora un badge de estado reactivo al lado del título principal (ej: "PENDIENTE", "CUMPLIDO" o "ANULADO").
- El badge se colorea según el estado para una fácil auditoría visual rápida (Verde para PENDIENTE, Amarillo para CUMPLIDO, Rojo para ANULADO).

### 24.2 Poka-Yoke para Pedidos Cerrados (CUMPLIDO / ANULADO)
Para resguardar la consistencia histórica de las operaciones, el sistema bloquea cualquier intento de edición en pedidos que ya han alcanzado el estado de ciclo cerrado:
1. **Banner de Advertencia de Solo Lectura:** Se muestra un banner destacado en la parte superior del canvas ("Este pedido está CUMPLIDO/ANULADO y no puede editarse. MODO LECTURA").
2. **Bloqueo de Controles en la Interfaz (UI):** Los botones "Guardar Pedido" y "Guardar e Imprimir" se deshabilitan automáticamente si el pedido está en un estado cerrado.
3. **Bloqueo del Atajo de Teclado:** El atajo global de teclado **F10** (Guardar) queda desactivado e ignorado cuando el pedido está cerrado.
4. **Salvaguarda Preventiva en Código (Early-Abort):** Si por alguna anomalía se intenta disparar la persistencia, el backend/frontend interrumpe la función `savePedido()` inmediatamente y emite una notificación de error en pantalla.

### 24.3 Adaptación de Altura de Contenedor (Fix Taskbar Windows)
Se reemplazaron las directivas rígidas de altura basadas en el viewport (`min-h-screen` / `h-screen`) por directivas fluidas (`min-h-full` / `h-full`) en la estructura del canvas. Esto previene que el panel del TOTAL FINAL y los botones operativos queden recortados o cubiertos por la barra de tareas de Windows, adaptando la interfaz perfectamente al tamaño real del contenedor.

