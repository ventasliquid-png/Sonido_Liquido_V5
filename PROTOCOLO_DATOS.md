# PROTOCOLO DE GESTIÓN DE DATOS (Fase Piloto V5)

**Fecha:** 11/12/2025
**Versión:** 1.0
**Estado:** VIGENTE

## 1. Introducción
Este documento normaliza los procedimientos técnicos y operativos para la ingesta, validación, persistencia y sincronización de datos maestros (Clientes y Productos) durante la fase piloto del sistema Sonido Líquido V5.

## 2. Arquitectura de Datos

### 2.1. Fuente de Verdad ("Golden Record")
Debido a la volatilidad de la base de datos operativa (`pilot.db`) durante el desarrollo, se establece que la **Fuente de Verdad** reside en archivos planos CSV inmutables/auditables:

*   **Clientes:** `BUILD_PILOTO/data/clientes_master.csv`
*   **Productos:** `BUILD_PILOTO/data/productos_master.csv`

Estos archivos actúan como el repositorio "eterno" y portable de los datos validados.

### 2.2. Base de Datos Operativa
*   **Motor:** SQLite (`pilot.db`)
*   **Ubicación:** `c:\dev\Sonido_Liquido_V5\pilot.db`
*   **Función:** Soporte transaccional para la aplicación V5. Se considera "desechable" o regenerable a partir de los Master CSV.
*   **Generación de Defaults:**
    *   Al importar un Cliente, se genera automáticamente un `Domicilio` legal ("A DEFINIR").
    *   Al importar un Producto, se genera automáticamente un `ProductoCosto` base (Costo 0).

### 2.3. Nube (IOWA)
*   **Motor:** PostgreSQL
*   **Función:** Respaldo remoto y futuro entorno de producción.
*   **Sincronización:** Unidireccional (Push) desde Local (Master CSV) hacia Nube al cierre de sesión.

## 3. Flujo de Trabajo (Data Intelligence)

### 3.1. Ingesta (Harvest)
Los datos crudos se obtienen de fuentes externas (Excel, Nube anterior) y se depositan como `_raw.csv`.

### 3.2. Limpieza y Validación (Data Cleaner)
El módulo `DataCleaner.vue` es la interfaz de operación.
*   **Corrección:** El operador normaliza nombres, CUITs y alias.
*   **Validación CUIT:** Algoritmo estricto (módulo 11). Input soporta guiones (15 caracteres) pero se guardan solo dígitos.
*   **Estado "Sucio" (Dirty State):** Cualquier edición en un registro (Nombre/CUIT) cambia su estado a `IMPORTAR`, habilitando su procesamiento incluso si fue ignorado previamente.

### 3.3. Importación Inteligente (Smart Update)
Al ejecutar el commit (`F10`), el sistema aplica la siguiente lógica de negocio:

1.  **Búsqueda:** Se busca el registro en la BD por su clave única (CUIT en Clientes, Nombre en Productos).
2.  **Coincidencia Exacta:** Si el registro existe y el Nombre coincide 100% -> Se marca como `EXISTENTE` y se omite.
3.  **Coincidencia Parcial (Corrección):** Si el registro existe (mismo CUIT) pero el Nombre difiere -> Se interpreta como una CORRECCIÓN. El sistema ejecuta un `UPDATE` sobre el registro existente.
4.  **Nuevo Registro:** Si no existe -> Se ejecuta un `INSERT`.

### 3.4. Persistencia del Estado
El resultado del procesamiento (IMPORTADO, EXISTENTE, ACTUALIZADO) se escribe de vuelta en el archivo CSV de origen (`_clean.csv`) para evitar bucles de reprocesamiento en futuras ejecuciones.

## 4. Estrategia de Resguardo

1.  **Cierre de Sesión:**
    *   Verificación de integridad de `_master.csv`.
    *   Ejecución de script `push_pilot_to_cloud.py`.
2.  **Backup:**
    *   La carpeta `BUILD_PILOTO/data` (conteniendo los CSVs) debe ser resguardada en Google Drive / Nube personal al finalizar el día.

---
**Firmado:** Equipo de Desarrollo V5 (Agente Antigravity)
