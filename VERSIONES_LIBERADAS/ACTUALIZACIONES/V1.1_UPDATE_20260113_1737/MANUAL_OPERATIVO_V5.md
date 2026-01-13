# MANUAL OPERATIVO V5 - SONIDO LÃ�QUIDO
**VersiÃ³n del Documento:** 1.0
**Estado:** VIGENTE
**CÃ³digo de Doctrina:** DEOU-2025

---
# Manual Operativo V5

## Control de Cambios
- **V5.3 (Vector Update):** ImplementaciÃ³n de Historial Vectorial y Toggle de Excel en Carga TÃ¡ctica.
- **V6.0 (Hybrid Engine):** Motor de Precios HÃ­brido, JerarquÃ­a de Rendimiento, BÃºsqueda por SKU y Protocolo de Higiene de Datos.

## 1. Carga TÃ¡ctica (Tactical Loader)
El mÃ³dulo de carga rÃ¡pida (`/ventas/loader`) permite la creaciÃ³n Ã¡gil de pedidos.

### Nuevas Funcionalidades
1.  **Historial de Cliente (Widget Reloj):**
    - Al pasar el mouse sobre el Ã­cono de reloj (o clic derecho), se despliega el historial de los **Ãºltimos 5 pedidos**.
    - Este historial es "vivo" y se actualiza instantÃ¡neamente con cada nueva compra.
    
2.  **ExportaciÃ³n Excel Opcional:**
    - Casilla de verificaciÃ³n: **"Generar Comprobante (Excel)"**.
    - Permite elegir si se desea descargar el archivo fÃ­sico `.xlsx` al guardar el pedido. Ideal para cargas masivas donde no se requiere imprimir comprobantes uno por uno.

### Teclas RÃ¡pidas
- **F3:** Buscar Cliente.
- **F4 / "+" :** Agregar Producto.
- **F10:** Guardar Pedido.

## CAPÃ�TULO 1: LA DOCTRINA DE INTERFAZ (DEOU)

El sistema V5 se rige por la **Doctrina de Eficiencia Operativa Unificada (DEOU)**, diseÃ±ada para maximizar la velocidad de operaciÃ³n y reducir la carga cognitiva del usuario.

### 1.1 Layout TrÃ­ptico
La interfaz principal se divide en tres zonas funcionales que permanecen constantes en todos los mÃ³dulos operativos:

1.  **Sidebar (NavegaciÃ³n):** Panel izquierdo colapsable/fijo. Contiene el acceso a los mÃ³dulos principales y herramientas globales.
2.  **Lista (ExploraciÃ³n):** Zona central. Muestra los registros en formato Grilla (Tarjetas) o Lista (Renglones). Soporta filtrado y ordenamiento rÃ¡pido.
3.  **Inspector (EdiciÃ³n):** Panel derecho deslizante. Permite la ediciÃ³n en detalle del registro seleccionado sin perder el contexto de la lista.

### 1.2 Atajos de Combate
El teclado es el dispositivo primario de operaciÃ³n. Los siguientes atajos son globales y obligatorios:

*   **F10 (Guardar y Cerrar):** Confirma la operaciÃ³n actual en cualquier formulario o inspector. Si es exitoso, cierra el panel.
*   **F3 (Buscar):** Pone el foco inmediatamente en la barra de bÃºsqueda global del mÃ³dulo actual.
*   **F4 (Stack / Nuevo):**
    *   En Listas: Abre el formulario de "Nuevo Registro".
    *   En Formularios (Combos): Abre el ABM rÃ¡pido de la entidad relacionada (ej: Crear un nuevo Rubro desde el selector de Rubros).
*   **ESC (Cancelar/Cerrar):** Cierra el inspector o modal actual sin guardar cambios.
*   **Ctrl + K:** Abre la Paleta de Comandos Global (NavegaciÃ³n rÃ¡pida).

### 1.3 SemÃ¡ntica Visual
El sistema utiliza un cÃ³digo de colores estricto para diferenciar contextos y evitar errores operativos:

*   **ðŸ”µ CLIENTES (Hawe):** Tonos **Azul / Cyan**. Representa la entidad comercial y la venta.
*   **ðŸ”´ PRODUCTOS (Manufactura):** Tonos **BordÃ³ / Rose**. Representa el inventario, costos y producciÃ³n.
*   **ðŸŸ  LOGÃ�STICA (Transportes):** Tonos **Naranja**. Representa el movimiento fÃ­sico de mercaderÃ­a.
*   **ðŸŸ¢ MAESTROS (Segmentos):** Tonos **Verde / Emerald**. Representa las clasificaciones y configuraciones.
*   **ðŸŸ£ AGENDA (Contactos):** Tonos **Rosa / Pink**. Representa a las personas y vÃ­nculos humanos.

---

## CAPÃ�TULO 2: MÃ“DULO CLIENTES (HAWE)

El mÃ³dulo "Hawe" centraliza la gestiÃ³n de la cartera de clientes, enfocÃ¡ndose en la velocidad de acceso y la integridad de los datos logÃ­sticos.

### 2.1 Ficha del Cliente
La ficha es el nÃºcleo de la informaciÃ³n comercial. Se compone de:
*   **Datos Identitarios:** RazÃ³n Social, CUIT, CondiciÃ³n IVA.
*   **Estado:** Activo / Inactivo (con interruptor visual).
*   **Contador de Uso:** MÃ©trica de popularidad que ordena automÃ¡ticamente a los clientes mÃ¡s frecuentes al tope de la lista.

### 2.2 Domicilios y LogÃ­stica
Un cliente puede tener mÃºltiples domicilios, pero se clasifican estrictamente en:
*   **Domicilio Fiscal:** DirecciÃ³n legal asociada al CUIT.
*   **Domicilio de Entrega:** DirecciÃ³n fÃ­sica donde se recibe la mercaderÃ­a.
*   **LogÃ­stica Asociada:** Cada domicilio tiene vinculado un **Transporte** predeterminado (ej: "Expreso Lo Bruno", "Retiro en Local").

### 2.3 Concepto de Segmentos
Los clientes se agrupan en **Segmentos** (anteriormente "Ramos").
*   Permite clasificar la cartera por canal de venta o tipo de negocio.
60: *   Es un filtro primario en el explorador de clientes.
61: 
62: ### 2.4 AdministraciÃ³n de Segmentos
63: El mÃ³dulo de Segmentos permite crear y editar las clasificaciones de la cartera.
64: *   **UbicaciÃ³n:** MenÃº Lateral > Grupo CLIENTES > Segmentos.
65: *   **Interfaz Split-Pane:** La pantalla se divide en dos:
66:     *   **Izquierda (Lista):** Muestra los segmentos existentes.
67:     *   **Derecha (Inspector):** Panel fijo de ediciÃ³n.
68: *   **OperaciÃ³n:**
69:     *   Al seleccionar un segmento de la lista, se carga en el panel derecho.
70:     *   Para crear uno nuevo, presione el botÃ³n **+ NUEVO (INS)** o la tecla `Insert`.
71:     *   Para guardar, presione **Guardar (F10)**.
72: 
73: ---

## CAPÃ�TULO 3: MÃ“DULO PRODUCTOS (MANUFACTURA)

El mÃ³dulo de Manufactura gestiona el catÃ¡logo de artÃ­culos, sus costos y su lÃ³gica de abastecimiento.

### 3.1 Identidad e IdentificaciÃ³n
*   **SKU (Stock Keeping Unit):** Identificador Ãºnico interno. El sistema lo genera automÃ¡ticamente (Secuencia "AUTO") pero permite overrides manuales.
*   **CÃ³digo Visual:** CÃ³digo corto de uso cotidiano (ej: "JL-500" para JabÃ³n LÃ­quido 5L).
*   **Es Kit:** Indicador para productos compuestos (Combos).

### 3.2 ClasificaciÃ³n: Rubros
*   **JerarquÃ­a:** Los productos se organizan en un Ã¡rbol de **Rubros** (CategorÃ­as).
*   **Regla de "No Orfandad":** Todo producto debe pertenecer a un rubro.

### 3.3 Precios: La FÃ³rmula 1.105
El sistema calcula los precios de venta en cascada partiendo del costo:

1.  **Costo ReposiciÃ³n (Neto):** Valor de compra al proveedor.
2.  **Precio Mayorista:** `(Costo + Margen%) + IVA`.
3.  **Precio Distribuidor:** `Precio Mayorista * 1.105`.
4.  **Precio Minorista:** `(Precio Distribuidor / 0.90) * 1.105`.

*El simulador de precios en el inspector permite visualizar estos valores en tiempo real al ajustar costos o mÃ¡rgenes.*

### 3.4 LogÃ­stica Industrial
Para soportar la compra y el stock, se definen dos unidades:
*   **Unidad de Stock:** CÃ³mo se cuenta en el inventario (ej: "Unidad", "Litro").
*   **Unidad de Compra:** CÃ³mo se pide al proveedor (ej: "Caja", "Tambor").
*   **Factor de ConversiÃ³n:** RelaciÃ³n numÃ©rica entre la unidad de compra y la de stock (ej: 1 Caja = 12 Unidades).

### 3.5 SatÃ©lites
*   **Proveedores:** Entidades que abastecen los productos (vinculados como "Proveedor Habitual").
*   **DepÃ³sitos Internos:** Ubicaciones fÃ­sicas o virtuales donde reside el stock (ej: "Central", "MÃ³vil").

---

## CAPÃ�TULO 4: MÃ“DULO AGENDA & MAESTROS

Este capÃ­tulo abarca las entidades transversales que dan soporte a los mÃ³dulos operativos.

### 4.1 Agenda de Contactos
Gestiona a las **Personas** fÃ­sicas, independientemente de si son clientes, proveedores o empleados.
*   **VÃ­nculos:** Una persona puede estar vinculada a mÃºltiples entidades (ej: Un contacto puede ser "Vendedor" en la empresa y "Comprador" en un Cliente).
*   **Tipos de Contacto:** Roles definibles (DueÃ±o, Encargado, Vendedor, Chofer).

### 4.2 Unidades de Medida
Tabla maestra que define las magnitudes fÃ­sicas permitidas en el sistema:
*   **UN:** Unidad (Discreto).
*   **LT:** Litro (Volumen).
*   **KG:** Kilogramo (Peso).
*   **MT:** Metro (Longitud).

### 4.3 Tasas de IVA
ConfiguraciÃ³n centralizada de alÃ­cuotas impositivas para asegurar consistencia fiscal:
*   **21.0%:** IVA General.
*   **10.5%:** IVA Reducido.
*   **27.0%:** IVA Diferencial.
*   **0.0%:** Exento / No Gravado.

---

## CAPÃ�TULO 5: ESTRATEGIA DE DATOS Y CONTINGENCIA

Para garantizar la operaciÃ³n continua incluso sin conexiÃ³n a internet o ante fallos del servidor central (IOWA), el sistema V5 implementa la **Doctrina de Blindaje de Datos**.

### 5.1 Modo HÃ­brido (Offline First)
La operaciÃ³n diaria no depende de la nube.
*   **Trinchera (Local):** La facturaciÃ³n, carga de pedidos y gestiÃ³n se realizan sobre una base de datos local de alta velocidad (`pilot.db`).
*   **Respaldo (Nube):** La sincronizaciÃ³n con el servidor central es asÃ­ncrona. Se suben los datos cuando la conexiÃ³n es estable, pero no bloquea el trabajo si se corta internet.


### 5.2 Semillas Maestras (Golden Seeds)
Son el mecanismo de seguridad Ãºltimo ("Arca de NoÃ©").
*   Al final de cada sesiÃ³n o hito importante, el sistema exporta el conocimiento clave (Clientes, Productos, Deudas) a archivos **CSV planos e inmutables**.
*   **RecuperaciÃ³n:** Si la base de datos local se corrompe y la nube es inaccesible, el sistema puede "Resetearse" y reconstruirse por completo en segundos importando estas semillas.
*   **UbicaciÃ³n:** Carpeta `BUILD_PILOTO/data`.

---

## CAPÃ�TULO 6: MÃ“DULO VENTAS (TACTICAL LOADER)

El mÃ³dulo de ventas estÃ¡ diseÃ±ado para la velocidad ("Excel Killer"). Prioriza la carga rÃ¡pida mediante teclado y la inteligencia contextual.

### 6.1 Dashboard de Pedidos
El centro de control de ventas (`Tablero Pedidos`) ofrece una vista densa y rÃ¡pida del estado del negocio.
*   **SemÃ¡foro de Estados:**
    *   ðŸŸ¢ **PENDIENTE (Verde):** Pedido en proceso, borrador o reciÃ©n ingresado. Requiere acciÃ³n.
    *   ðŸŸ¡ **CUMPLIDO (Amarillo):** Pedido finalizado, entregado o facturado. Ciclo cerrado.
    *   ðŸ”´ **ANULADO (Rojo):** Pedido cancelado (baja lÃ³gica).
    *   ðŸŸ£ **INTERNO:** Pedidos administrativos o de movimiento interno.
*   **Filtros:** Barra superior para filtrar rÃ¡pidamente por estado.

### 6.2 Cargador TÃ¡ctico (GridLoader)
Interfaz de alta velocidad para la toma de pedidos. Visualmente similar a una hoja de cÃ¡lculo.
*   **NavegaciÃ³n:** DiseÃ±ada para usarse sin mouse (Enter para nueva fila, Flechas para navegar).
*   **Inteligencia de Precios:** Al seleccionar un cliente y un producto, el sistema busca automÃ¡ticamente la **Ãºltima venta** de ese producto a ese cliente y sugiere ese precio (respetando la historia comercial real).
*   **Consumidor Final:** LÃ³gica especial que omite validaciones estrictas de CUIT/Domicilio para ventas rÃ¡pidas de mostrador.
*   **ExportaciÃ³n:** GeneraciÃ³n instantÃ¡nea de Excel con el detalle del pedido para procesar en sistemas legacy o enviar por mail.



### 6.3 Herramientas de GestiÃ³n de SesiÃ³n
Para evitar errores por datos persistentes ("Datos viejos"), se incorporaron controles explÃ­citos en el pie de pÃ¡gina:

1.  **Limpiar Pantalla (Icono Papelera):**
    - Este botÃ³n realiza un "Hard Reset" del formulario.
    - Borra todos los Ã­tems, deselecciona el cliente y **elimina la memoria temporal** del navegador.
    - Ãšselo si nota que el sistema carga informaciÃ³n de un pedido anterior.


2.  **Generar Excel (Toggle):**
    - Ubicado junto al botÃ³n Guardar.
    - Si estÃ¡ activo (Verde), al guardar el pedido se descargarÃ¡ automÃ¡ticamente una copia en Excel.

---

## CAPÃ�TULO 7: MOTOR DE PRECIOS V5 (LA ROCA Y LA MÃ�SCARA)

El sistema V5 abandona las listas de precio estÃ¡ticas en favor de un cÃ¡lculo dinÃ¡mico basado en costos y estrategias.

### 7.1 FilosofÃ­a de CÃ¡lculo
El precio sugerido se construye en tres capas:
1.  **"La Roca" (Precio Piso):** Es el valor mÃ­nimo tÃ©cnico. `(Costo ReposiciÃ³n * (1 + Margen))` o el **Precio Fijo Manual** si existe (Prioridad Divina).
2.  **"K-Factor" (Estrategia):** Multiplicador segÃºn el perfil del cliente.
    *   **Mayorista Fiscal:** Aplica IVA Discriminado (21% / 10.5%).
    *   **Mayorista X:** Aplica IVA Compartido ("Saborizado").
    *   **MELI ClÃ¡sico:** Aplica Markup (+40%) y Costo Fijo por venta.
3.  **"La MÃ¡scara" (IngenierÃ­a Inversa):** El sistema muestra un **Precio de Lista Inflado** calculado matemÃ¡ticamente para que, tras aplicar el descuento visual prometido al cliente (ej: 20%), el precio final coincida exactamente con el objetivo de rentabilidad.

### 7.2 Herramienta "Magic Math"
En el Cargador TÃ¡ctico, los campos numÃ©ricos (Cantidad y Precio) funcionan como una calculadora inteligente (estilo Excel).
*   **Suma rÃ¡pida:** Escriba `10 + 5` â†’ Resultado: `15`.
*   **CÃ¡lculo de IVA:** Escriba `100 * 1.21` â†’ Resultado: `121`.
*   **DivisiÃ³n:** Escriba `5000 / 3` â†’ Resultado: `1666.67`.
*   *Indicador visual:* AparecerÃ¡ un sÃ­mbolo `fx` azul mientras escribe una fÃ³rmula.

### 7.3 Overrides (Excepciones)
Si un producto tiene asignado un **Precio Fijo Override**, el motor ignorarÃ¡ cualquier cÃ¡lculo de costo/margen y usarÃ¡ ese valor como base inamovible ("La Roca"). Esto es Ãºtil para ofertas puntuales o productos con precio regulado.

### 7.4 Motor HÃ­brido V6 (JerarquÃ­a de Poder)
La versiÃ³n 6 introduce el **CM Objetivo (ContribuciÃ³n Marginal)** y la **Propuesta por Rubro**. La jerarquÃ­a de decisiÃ³n del motor es:

1.  **PRECIO FIJO MANUAL:** Si hay un valor en `precio_fijo_override`, se usa sin preguntar.
2.  **CM OBJETIVO (Artesanal):** Si no hay precio fijo, pero hay un `% CM Objetivo` en el producto, el sistema despeja el precio para garantizar ese margen sobre el costo.
3.  **MARGEN POR RUBRO:** Si el producto no tiene CM propio, usa el `% Margen Default` del Rubro al que pertenece (ej: Todos los Guantes al 35%).
4.  **MARGEN PRODUCTO (Legacy):** Si todo lo anterior falla, usa el margen mayorista individual de la ficha.

---

## CAPÃ�TULO 11: PROTOCOLO DE HIGIENE DE DATOS (ANTI-FRANKENSTEIN)

Para evitar la desincronizaciÃ³n de datos entre la PC local y la nube (IOWA), se deben seguir estas reglas de oro:

### 11.1 El Local manda
La base `pilot.db` es la fuente de verdad de la **operaciÃ³n diaria** y los **precios**. La nube (IOWA) es la fuente de verdad del **maestro purgado** (Rubros y SKUs).

### 11.2 SincronizaciÃ³n Obligatoria
Antes de iniciar una carga masiva o despuÃ©s de cambios estructurales en rubros, ejecute el script de reconciliaciÃ³n:
```bash
python scripts/reconcile_master_data.py
```
Este script asegura que:
1.  Los rubros locales coincidan con los de la nube.
2.  Los productos nuevos en local se informen a la nube.
3.  Los SKUs se mantengan alineados.

### 11.3 PrevenciÃ³n de Duplicados
Al cargar productos nuevos, siempre verifique el **SKU**. No cree productos con el mismo nombre y SKU diferente; el sistema lo detectarÃ¡ como una anomalÃ­a en el prÃ³ximo reporte de auditorÃ­a.

---

## CAPÃ�TULO 8: ACCESO REMOTO MULTIJUGADOR (LAN)

### 8.1 Concepto
El sistema V5 permite que mÃºltiples usuarios (ej: AdministraciÃ³n + Ventas + DepÃ³sito) trabajen simultÃ¡neamente sobre la misma base de datos desde distintas computadoras de la red local (WiFi o Cable), sin necesidad de Internet.

### 8.2 CÃ³mo Iniciar (Lanzador AutomÃ¡tico)
Para habilitar el modo red, **NO use el comando habitual**.
1. En la PC Principal (Servidor), cierre todas las ventanas negras.
2. Abra una sola terminal y ejecute:
   `.\scripts\run_lan.ps1`
3. El sistema abrirÃ¡ automÃ¡ticamente el Servidor y la Web configurados para la red.

### 8.3 ConexiÃ³n desde otras PC
El script mostrarÃ¡ una direcciÃ³n IP (ej: `http://192.168.0.X:5173`).
Ingrese esa direcciÃ³n exacta en el navegador de las otras computadoras.

**Usuarios Disponibles:**
*   Administrador: `admin` / `admin123`
*   Operador de Carga: `operador` / `operador123` (Rol restringido).

### 8.4 SoluciÃ³n de Problemas
*   **"Error al conectar":** Generalmente es el Firewall de Windows en la PC Principal. Ejecute el script `scripts\fix_access.ps1` como Administrador para abrir los puertos 8000 y 5173.
*   **"Sitio no carga":** Verifique que ambas PC estÃƒÂ©n en la misma red WiFi.

---

## CAPÃ�TULO 9: PROTOCOLO UNIVERSAL DE ARRANQUE (CROSS-PLATFORM)

A partir de la fase de estandarizaciÃ³n, el sistema abandona la dependencia exclusiva de PowerShell (`.ps1`) para el arranque del backend.

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
Los comandos de respaldo tambiÃ©n son universales:
*   **Local:** `python3 scripts/backup.py`
*   **Drive:** `python3 scripts/backup_drive.py`

### 9.4 El Frontend
Se lanza con el nuevo script universal:
```bash
python scripts/run_front.py
```
*Tip: Al igual que el backend, puedes hacer botÃ³n derecho sobre `run_front.py` y correrlo con Python.*

### 9.5 Acceso Remoto (Modo LAN)
Para que otros se conecten, el servidor debe estar en modo LAN. 
*   **Acceso RÃ¡pido:** Use el icono **LAN_SERVER_V5.bat** creado en su Escritorio.
*   **Manual:** Ejecute `python scripts/run_lan.py` desde la raÃ­z.
*   *Nota:* Este script configura automÃ¡ticamente las IPs para que TomÃ¡s u otros operadores puedan ingresar desde sus puestos.

---

## CAPÃ�TULO 10: DOCTRINA DE PEDIDOS (V5 TÃ�CTICO)

El nuevo MÃ³dulo de Pedidos integra la filosofÃ­a de alta velocidad del Comandante.

### 10.1 Cargador TÃ¡ctico (Speed-Grid)
DiseÃ±ado para la toma de pedidos telefÃ³nica o presencial ultra-veloz.
- **Magic Math:** El sistema autocompleta el precio basÃ¡ndose en la **Ãºltima venta real** a ese cliente.
- **NavegaciÃ³n:** Arreglo vertical optimizado para uso exclusivo del teclado.

### 10.2 Identidad de Estados
- **Verde Esmeralda:** Pedidos normales/pendientes.
- **Rosa Chicle Fluo:** Alerta de **Entrega Comprometida a Futuro**. No pasar por alto en la logÃ­stica diaria.
- **FacturaciÃ³n:** Selector explÃ­cito entre Interno (X) y Fiscal (Facturable) integrado en el inspector.



---

## CAPÃ�TULO 11: GESTIÃ“N DE DOCUMENTOS (ETIQUETADO PDF)

El sistema V5 incluye herramientas para la intervenciÃ³n de documentos generados por sistemas externos (como AFIP/ARCA) que requieren datos de gestiÃ³n adicionales.

### 11.1 Etiquetador Express de OC/PO
Esta utilidad permite 'sellar' nÃºmeros de Orden de Compra o Purchase Order en facturas PDF que vienen bloqueadas para ediciÃ³n.

*   **UbicaciÃ³n de Acceso:** Carpeta `tools/arca_oc_stamper/` (**ETIQUETADOR_PDF.bat**).
*   **OperaciÃ³n:**
    1. Seleccione el archivo PDF original.
    2. Elija el prefijo deseado (OC o PO).
    3. Ingrese el nÃºmero de referencia.
    4. El sistema generarÃ¡ una copia con el sufijo _etq en el nombre.
*   **LÃ³gica de Posicionamiento:** El dato se inserta en la esquina superior derecha del documento (Original), alineado con la cabecera fiscal, asegurando visibilidad clÃ­nica sin interferir con la validez del comprobante.

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
