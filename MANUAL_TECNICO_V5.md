# 📘 MANUAL TÉCNICO V5: "INDEPENDENCIA"
**Versión:** 1.0 Release (Updated V5.4)
**Fecha:** 25-01-2026

## 1. DOCTRINA DE PRECIOS: "LA ROCA Y LA MÁSCARA"
El sistema V5 implementa una estrategia psicológica de precios:
* **La Roca (Precio Objetivo):** Es el valor real de rentabilidad que la empresa necesita cobrar (Backend). Es inamovible.
* **La Máscara (Precio de Lista):** Es el valor público ("inflado") sobre el cual se aplican bonificaciones.
* **Objetivo:** El sistema permite llegar a "La Roca" aplicando descuentos sobre "La Máscara", generando en el cliente la satisfacción de "ganar" una bonificación, mientras la empresa asegura su margen.

## 2. ARQUITECTURA DE CLIENTES (V5.4) - "UNA PLANTA = UN CLIENTE"
* **Definición:** En clientes multi-sede (ej: Nestlé), cada planta industrial o punto de entrega se modela como un "Cliente ID" independiente en la base de datos.
* **Justificación:** Simplifica la asignación de transportes, horarios de recepción y contactos específicos sin complejizar el modelo de datos con sub-tablas de "Sedes".
* **Consistencia:** Todos operan con la misma Razón Social y CUIT (Duplicidad permitida y validada con advertencia), pero con "Dirección de Entrega" única.

## 3. ARQUITECTURA DE DESPLIEGUE
* **Modo Instalación:** Se despliega el paquete completo con base de datos vacía.
* **Modo Actualización:** Se reemplazan solo carpetas `frontend` y `backend`. NUNCA se toca el archivo `.db` del usuario ni el archivo `.env`.

## 4. SOPORTE TÉCNICO Y GEM
El soporte de Nivel 1 es realizado por el Agente IA "Ayuda HAWE".
* **Fuente de Verdad:** El Agente lee este manual directamente desde Google Drive.
* **Instrucción al Usuario:** Ante cualquier error (pantalla blanca, error 500), el usuario debe copiar el mensaje y pegarlo en el chat de Ayuda.

## 5. RUTAS Y VARIABLES (.ENV)
* `DATABASE_URL`: Apunta a la base local (SQLite).
* `PATH_DRIVE_BACKUP`: Ruta absoluta a la carpeta de Google Drive Desktop del usuario. Es vital para la Regla 4/6 (Backup automático cada 4 sesiones).

## 6. ARQUITECTURA DE CONTACTOS (V5.6)
* **Modelo Unificado:** La entidad `Contacto` actúa como nexo entre una persona física y una organización (Cliente o Transporte).
* **Gestión de Estado (Frontend):** Se utiliza `storeToRefs` (Pinia) obligatoriamente para garantizar reactividad en selects dinámicos (Cliente/Transporte).
* **Prevención de Fallos (Backend):** Las propiedades computadas como `contacto_principal_nombre` deben implementar bloques `try/except` para aislar fallos de integridad en registros individuales y evitar caídas en listados masivos (Error 500).

## 7. LOGÍSTICA TÁCTICA V7 (SPLIT ORDERS)
* **Concepto:** Un `Pedido` es una intención comercial (Reserva de Stock). Un `Remito` es una ejecución física (Movimiento de Mercadería).
* **Cardinalidad:** Un Pedido puede tener N Remitos (Entregas Parciales).
* **Gatekeeper Financiero:**
    * El sistema impide generar remitos oficiales si el Pedido no tiene el flag `liberado_despacho`.
    * Excepción: Usuarios con permisos pueden forzar el desbloqueo bajo su responsabilidad (Audit Log).
* **Safety Net:** La exportación a Excel detecta automáticamente si un pedido tiene logística simple (1 destino) o múltiple, adaptando la columna "Logística" para evitar errores de interpretación.

## 8. HUB LOGÍSTICO V5.7 (SPLIT VIEW)
* **Arquitectura Híbrida:** Se separa la dirección en dos entidades conceptuales:
    * **Fiscal (Panel Izquierdo):** Datos legales validados. Solo editable con Flag Fiscal.
    * **Logística (Panel Derecho):** Datos operativos del punto de entrega.
* **Mapeo de Datos:**
    * Para evitar inconsistencias, si un domicilio NO es fiscal, el sistema **copia automáticamente** los datos del panel logístico (Calle Entrega, Número Entrega) a los campos nucleares de la base de datos (`calle`, `numero`).
    * **Razón:** El backend espera la dirección física en `calle`. Si solo se llenaba `calle_entrega`, el registro quedaba "vacío" a nivel lógico.

