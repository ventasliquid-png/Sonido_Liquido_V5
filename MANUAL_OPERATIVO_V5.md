# MANUAL OPERATIVO V5 - SONIDO LÍQUIDO
**Versión del Documento:** 1.0
**Estado:** VIGENTE
**Código de Doctrina:** DEOU-2025

---

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
*   **Domicilio de Entrega:** Dirección física donde se recibe la mercadería.
*   **Logística Asociada:** Cada domicilio tiene vinculado un **Transporte** predeterminado (ej: "Expreso Lo Bruno", "Retiro en Local").

### 2.3 Concepto de Segmentos
Los clientes se agrupan en **Segmentos** (anteriormente "Ramos").
*   Permite clasificar la cartera por canal de venta o tipo de negocio.
*   Es un filtro primario en el explorador de clientes.

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
