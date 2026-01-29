# MANUAL HAWE (V5)

## Filosofía de Diseño
HAWE (Cielo/Espacio en Ona) es la nueva interfaz inmersiva de Sonido Líquido V5.
Se aleja del diseño tradicional de "Tablas y Formularios" para abrazar un enfoque de "Exploración y Lienzos".

### Principios Clave
1.  **Inmersión:** Interfaz oscura (`#165078`), minimalista y sin distracciones.
2.  **Contexto:** La información aparece donde se necesita (Inspectores laterales) sin bloquear la vista principal.
3.  **Objetos Inteligentes:** Las entidades (Clientes, Pedidos) son objetos vivos con historia, no solo filas en una base de datos.

## Componentes del Sistema

### 1. El Explorador (Overpass)
Es la vista principal (`/hawe`).
- **Fichas (Cards):** Representación visual de las entidades.
- **Filtros Inmediatos:** Segmentación y Estado (Activo/Inactivo) a un clic.
- **Búsqueda Inteligente:** Insensible a acentos y errores comunes.

### 2. El Lienzo (Canvas)
Es el espacio de trabajo de una entidad (`/hawe/cliente/:id`).
- **Navegación:** Se accede con **Doble Click** desde el explorador.
- **Estructura:**
    - **Izquierda:** Propiedades Duras (Datos fiscales, Clasificación).
    - **Centro:** Línea de Tiempo y Acciones (Notas, Domicilios, Historial).
    - **Centro:** Línea de Tiempo y Acciones (Notas, Domicilios, Historial).
    - **Derecha:** Vínculos (Contactos, Relaciones).

### 3. Mejoras de Usabilidad (UX V5.6)
- **Autofocus:** Al abrir una ficha, el cursor se sitúa automáticamente en el campo "Razón Social" para agilizar el ingreso.
- **Domicilio Pendiente:** Se identifica claramente (en gris e itálica) cuando un cliente no tiene domicilio fiscal asignado, reduciendo el ruido visual.

## Atajos de Teclado
- **F10:** Guardar cambios en el Lienzo.
- **ESC:** Volver al Explorador (desde el Canvas).

## Hoja de Ruta Técnica
- [x] Prototipo Visual (Dark Mode)
- [x] Explorador de Clientes (Filtros, Búsqueda)
- [x] Canvas de Edición (Estructura Base)
- [ ] Ordenamiento Avanzado (ABC, Movimiento)
- [ ] Módulo de Productos (Galería Visual)
- [ ] Módulo de Pedidos (Objeto Inteligente)

### 4. Agenda Global (Contactos)
Módulo centralizado para la gestión de personas (/agenda/contactos).
- **Concepto:** Google Contacts Style. Tarjetas limpias con iniciales y roles.
- **Canvas Lateral:** Edición rápida sin perder el contexto de la grilla.
- **Simetría:** Los contactos pueden vincularse a un Cliente (Comercial) o a una Empresa de Transporte (Logística).
