# MANUAL OPERATIVO V5 - SONIDO LÍQUIDO
**Versión del Documento:** 1.0
**Estado:** VIGENTE
**Código de Doctrina:** DEOU-2025

---
# Manual Operativo V5

## Control de Cambios
- **V5.3 (Vector Update):** Implementación de Historial Vectorial y Toggle de Excel en Carga Táctica.
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
*   **Logística Asociada:** Cada domicilio tiene vinculado un **Transporte** predeterminado (ej: "Expreso Lo Bruno", "Retiro en Local").

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

### 6.2 Cargador Táctico (GridLoader)
Interfaz de alta velocidad para la toma de pedidos. Visualmente similar a una hoja de cálculo.
*   **Navegación:** Diseñada para usarse sin mouse (Enter para nueva fila, Flechas para navegar).
*   **Inteligencia de Precios:** Al seleccionar un cliente y un producto, el sistema busca automáticamente la **última venta** de ese producto a ese cliente y sugiere ese precio (respetando la historia comercial real).
*   **Consumidor Final:** Lógica especial que omite validaciones estrictas de CUIT/Domicilio para ventas rápidas de mostrador.
*   **Exportación:** Generación instantánea de Excel con el detalle del pedido para procesar en sistemas legacy o enviar por mail.



### 6.3 Herramientas de Gestión de Sesión
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

### 12.3 Flujo de Anulación
Para anular un pedido:
1. Cambie el estado a **ANULADO** usando el selector.
2. El sistema eliminará el IVA y cambiará el tema a Rojo.
3. El pedido dejará de sumar en los reportes de deuda fiscal.
