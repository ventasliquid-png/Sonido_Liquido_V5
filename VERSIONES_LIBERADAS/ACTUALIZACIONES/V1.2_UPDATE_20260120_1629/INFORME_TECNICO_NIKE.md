# INFORME TÉCNICO: DEPURACIÓN Y GENERACIÓN RELEASE V1.1
**Fecha:** 2026-01-13
**Destinatario:** Arq. Nike
**Responsable:** Gy (Antigravity)

## 1. Resumen Ejecutivo
Se ha completado la estabilización crítica de los flujos de alta manual en "Maestros", la corrección profunda de la lógica comercial de Pedidos y una reingeniería significativa de la **Experiencia de Usuario (UX)** en el módulo de Clientes. Se ha generado exitosamente el paquete de actualización **Release V1.1**.

## 2. Correcciones de UX y Funcionalidad (Actualización Final)

### A. Reingeniería de Alta de Clientes ("Central Canvas")
**Problemática:** El panel lateral ("Inspector") presentaba problemas de visualización en pantallas compactas, ocultando el botón crítico de "Guardar (F10)" y generando fricción en el flujo de alta.
**Solución Técnica:**
- Se migró la acción de "Nuevo Cliente" en `HaweView.vue` a un **Modal Central (Canvas)**.
- Este diseño garantiza que el pie de página con las acciones de guardado esté siempre visible y "pegado" (`sticky`) al borde inferior, independientemente del scroll.
- Se homogenizó la experiencia con el módulo de Pedidos, que ya utilizaba este patrón exitoso.

### B. Búsqueda Global Integrada (Pedidos + Cantera)
**Problemática:** El usuario no podía acceder a la base maestra ("Cantera") desde el buscador rápido del Táctico de Pedidos (`ClientLookup`), forzándolo a salir del flujo de venta para dar de alta un cliente existente.
**Solución Técnica:**
- Se actualizó `ClientLookup.vue` para incluir un botón **"Buscar en Cantera"** cuando la búsqueda local es infructuosa.
- Se implementó la importación y selección automática: al encontrar un cliente en Cantera (ej: "Petroplastic"), el sistema lo importa a la base operativa y lo selecciona inmediatamente para el pedido en curso.

### C. Corrección de Motor de Búsqueda (`SmartSelect`)
**Problemática:** El componente de selección ignoraba la "Razón Social" y el "CUIT" al filtrar resultados locales, causando falsos negativos.
**Solución Técnica:**
- Se parcheó `SmartSelect.vue` para indexar y filtrar explícitamente por `razon_social` y `cuit`.
- Se forzó la visualización de la opción de "Buscar en Cantera" siempre al final de la lista, permitiendo al usuario optar por la búsqueda remota incluso si existen coincidencias locales parciales.

---

## 3. Correcciones de Lógica de Negocio (Previas)

### A. Alta Manual de Maestros
- Habilitación de creación manual (`allowCreate="true"`) en inspectores de Clientes y Productos, permitiendo operar sin conexión a Cantera.

### B. Lógica de Clonado de Pedidos (Deep Copy)
- Refactorización de `backend/pedidos/router.py` para asegurar la copia profunda de todos los atributos económicos (descuentos, subtotales, notas) al clonar un pedido, garantizando integridad financiera.

## 4. Estrategia de Release V1.1

### A. Paquete Generado
- **Versión:** `v1.1`
- **Ubicación:** `VERSIONES_LIBERADAS/ACTUALIZACIONES/V1.1_UPDATE_20260113_1848`
- **Contenido:** Código fuente Backend/Frontend parcheado + Base de Datos Cantera (vía modificación en `build_release.py`).

## 5. Próximos Pasos (Protocolo Omega)
- Ejecutar cierre de sesión y actualización de bitácoras.
- Validar despliegue en entorno de pruebas.
