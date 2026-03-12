# ARQUITECTURA Y DOCTRINA - SONIDO LÍQUIDO V5
**Clasificación:** INTELIGENCIA DE SISTEMA (LÍNEA BASE)
**Fecha de Corte:** 2025-11-25
**Versión:** 5.2 (Snapshot)

---

## 1. LA DOCTRINA (Reglas de Negocio Inquebrantables)

### 1.1. Smart CUIT y "Libertad Vigilada"
En contraposición a la rigidez tradicional de bases de datos, Sonido Líquido V5 implementa una política de **"Libertad Vigilada"** respecto a la unicidad de los CUITs.

*   **El Problema:** Entidades masivas (ej: UBA, Gobiernos, Grandes Corporaciones) comparten un único CUIT para múltiples dependencias (Facultades, Ministerios, Sucursales) que operan como clientes financiera y logísticamente independientes.
*   **La Solución:** El sistema **PERMITE** la creación de múltiples fichas de cliente con el mismo CUIT.
*   **El Mecanismo:**
    1.  Al detectar un CUIT duplicado, el sistema advierte al operador pero **NO BLOQUEA** la operación.
    2.  El nuevo cliente se crea con el flag `requiere_auditoria = True`.
    3.  Visualmente, estas fichas aparecen marcadas (alerta amarilla) en los listados hasta que un supervisor las "Valida" (`requiere_auditoria = False`).

### 1.2. Higiene de Datos: Borrado Físico vs. Lógico
Para mantener la integridad referencial sin acumular basura digital, se aplican dos niveles de eliminación:

*   **Borrado Lógico (Soft Delete):**
    *   **Acción:** Setear `activo = False`.
    *   **Uso:** Para cualquier entidad que tenga historial (ventas, movimientos, vínculos).
    *   **Efecto:** La entidad desaparece de los selectores y listados "Activos", pero permanece en la base de datos para consultas históricas.
*   **Borrado Físico (Hard Delete):**
    *   **Acción:** `DELETE FROM table WHERE id = ...`
    *   **Uso:** Exclusivamente para errores de carga inmediata (ej: crear un cliente por error y borrarlo a los 5 segundos).
    *   **Restricción:** El backend impide (vía Foreign Keys) el borrado físico si existen registros dependientes.

### 1.3. Semántica: SEGMENTO vs. RUBRO
Es vital no confundir la clasificación de sujetos con la de objetos.

*   **SEGMENTO (Clientes):** Define la actividad comercial del CLIENTE (ej: "Gastronomía", "Educación", "Salud", "Hogar"). Se usa para segmentación comercial y reportes de ventas por canal.
*   **RUBRO (Productos):** Define la categoría del PRODUCTO (ej: "Audio Pro", "Iluminación", "Cables"). Se usa para listas de precios y control de stock.

### 1.4. Lógica de Precios (Coeficientes)
Sonido Líquido V5 abandona las listas de precios fijas en favor de una arquitectura dinámica basada en **Listas Base + Coeficientes**.

*   **Lista Base:** El costo o precio base del producto.
*   **Listas de Venta:** No contienen precios fijos, sino un coeficiente (decimal) que se aplica sobre la base.
    *   *Ejemplo:* "Lista Mayorista" = Base * 1.21; "Lista Gremio" = Base * 1.15.
*   **Ventaja:** Al actualizar el costo base de un producto, todas las listas de venta se actualizan automáticamente.

---

## 2. DICCIONARIO DE DATOS (Estructura Actual)

A continuación, se detallan los modelos maestros que constituyen la columna vertebral del sistema.

### 2.1. Cliente (`clientes`)
La entidad central del sistema.
*   `id`: UUID (PK).
*   `razon_social`: String. Nombre legal o principal.
*   `nombre_fantasia`: String (Opcional). Nombre comercial.
*   `cuit`: String(11). **NO ÚNICO**. Clave fiscal.
*   `condicion_iva_id`: Integer (FK).
*   `lista_precios_id`: UUID (FK). Lista asignada por defecto.
*   `activo`: Boolean. Default `True`.
*   `requiere_auditoria`: Boolean. Flag para duplicados de CUIT.
*   `contador_uso`: Integer. Métrica de "frecuencia" para ranking (Speed Dial).

### 2.2. Transporte (`logistica_empresas`)
Empresas logísticas externas.
*   `id`: UUID (PK).
*   `nombre`: String.
*   `web_tracking`: String (URL). Para seguimiento de envíos.
*   `telefono_reclamos`: String.
*   `requiere_carga_web`: Boolean. Indica si hay que cargar el envío en la web del transporte.
*   `activo`: Boolean.

### 2.3. Segmento (`segmentos`)
Clasificación comercial del cliente.
*   `id`: UUID (PK).
*   `nombre`: String (ej: "Gastronomía").
*   `descripcion`: String.
*   `activo`: Boolean.

### 2.4. Vendedor (`maestros_vendedores`)
Agentes comerciales.
*   `id`: UUID (PK).
*   `nombre`: String.
*   `comision_porcentaje`: Decimal.
*   `activo`: Boolean.

### 2.5. Lista de Precios (`maestros_listas_precios`)
Definiciones de reglas de precios.
*   `id`: UUID (PK).
*   `nombre`: String (ej: "Mayorista A").
*   `coeficiente`: Decimal (ej: 1.21). Multiplicador sobre el costo base.
*   `activo`: Boolean.

---

## 3. MAPA DE COMPONENTES (Frontend)

La interfaz de usuario (UI) sigue la **Norma DEOU** (Diseño Eficiente Orientado al Usuario), priorizando la velocidad y la claridad.

### 3.1. Estructura Híbrida de Listado
Para los ABM principales (Clientes), se utiliza un diseño híbrido:
1.  **Speed Dial (Top):** Una grilla horizontal con los registros más utilizados/recientes ("Top Clients"). Permite acceso instantáneo al 80% de la operatoria diaria.
2.  **Data Grid (Bottom):** Tabla tradicional paginada y filtrable para acceder al "Long Tail" (el resto del padrón).

### 3.2. Modales Apilados ("In-Context")
El sistema evita la navegación entre páginas (routers) para la carga de datos.
*   **Filosofía:** "Nunca pierdas el contexto de lo que estabas haciendo".
*   **Implementación:** Si estás creando un Cliente y necesitas un Transporte que no existe, presionas `F4` en el combo de transporte. Esto abre un **Segundo Modal** (Transporte) *encima* del primero. Al guardar y cerrar el segundo, vuelves al primero con el dato ya cargado.

### 3.3. Stack Tecnológico
*   **Framework:** Vue 3 (Composition API + `<script setup>`).
*   **Estado:** Pinia (Stores modulares).
*   **Estilos:** Tailwind CSS v3.
    *   *Tema:* Light Mode predominante.
    *   *Color Brand:* `#54cb9b` (Verde Sonido Líquido).
*   **Iconos:** Heroicons (SVG).

### 3.4. Estandarización de Filtros
*   **Ubicación:** Los filtros de estado ("Todos", "Activos", "Inactivos") deben ubicarse siempre alineados a la **derecha** en la barra de herramientas superior.
*   **Feedback:** Deben mostrar el conteo de registros filtrados a su izquierda.

---

## 4. ESTADO DE SITUACIÓN

### 4.1. Operativos (En Producción / Testing)
*   **Módulo Clientes:** Completo. ABM, Domicilios, Vínculos, Validación CUIT.
*   **Módulo Logística (Transportes):** Completo. ABM Empresas y Nodos.
*   **Módulo Maestros:**
    *   Segmentos: Completo.
    *   Vendedores: Completo.
    *   Listas de Precios: Completo.

### 4.2. En Construcción (Satélites)
*   **Agenda (Personas):** Backend operativo. Frontend integrado.
*   **Filtros Globales:** Completo. Estandarizados a la derecha en todos los módulos.

### 4.3. Pendientes ("La Gran Conexión")
*   **Módulo Rubros/Productos:** Próximo gran hito. Requiere implementar la lógica de precios y stock.
*   **Pedidos:** El núcleo transaccional que unirá Clientes, Productos y Logística.

---
*Fin del Documento - Generado por CLIO (AI Agent)*
