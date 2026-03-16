# 📘 MANUAL TÉCNICO V5: "INDEPENDENCIA"
**Versión:** 1.2 Release (Updated V14.7 Genoma)
**Fecha:** 10-03-2026

## 1. DOCTRINA DE PRECIOS: "LA ROCA Y LA MÁSCARA"
El sistema V5 implementa una estrategia psicológica de precios:
* **La Roca (Precio Objetivo):** Es el valor real de rentabilidad que la empresa necesita cobrar (Backend). Es inamovible.
* **La Máscara (Precio de Lista):** Es el valor público ("inflado") sobre el cual se aplican bonificaciones.
* **Objetivo:** El sistema permite llegar a "La Roca" aplicando descuentos sobre "La Máscara", generando en el cliente la satisfacción de "ganar" una bonificación, mientras la empresa asegura su margen.

## 2. ARQUITECTURA DE CLIENTES (V5.4) - "UNA PLANTA = UN CLIENTE" [LEGACY]
* **Nota de Evolución:** Este modelo 1:1 ha sido superado por la **Bóveda Universal V5**. Aunque la base de datos permite duplicar CUITs para representar plantas, la arquitectura recomendada ahora es usar **Vínculos Geográficos** sobre un único maestro de CUIT.

## 14. BÓVEDA UNIVERSAL DE DOMICILIOS (VANGUARD VAULT V5)
Implementada en Marzo 2026, esta arquitectura desacopla los domicilios físicos de las entidades comerciales.
* **Modelo N:M**: Una entidad (`CLIENTE`, `PERSONA`, `TRANSPORTE`) puede tener N domicilios, y un domicilio puede pertenecer a N entidades.
* **Genoma de Relación**: La tabla `vinculos_geograficos` almacena el rol de la dirección mediante una máscara de bits:
    - **Bit 0 (1):** Fiscal.
    - **Bit 1 (2):** Principal / Entrega.
    - **Bit 3 (8):** Temporal / Excepcional.
* **Resolución de Domicilio**: El `RemitosService` ahora consulta la Bóveda para determinar el destino legal y físico del envío, eliminando la dependencia de columnas fijas en la tabla `pedidos`.

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

    *   **Razón:** El backend espera la dirección física en `calle`. Si solo se llenaba `calle_entrega`, el registro quedaba "vacío" a nivel lógico.

## 9. PROTOCOLO PUENTE RAR-V5 (ARCA)
Incorporado en V6.3, este módulo conecta V5 con el legacy RAR V1 para validación fiscal.
*   **Arquitectura:** `AfipBridgeService` carga dinámicamente el módulo `Conexion_Blindada.py` de RAR.
*   **Puente Multi-Identidad (CUIT 20/30):** Debido a discrepancias en permisos fiscales, el puente conmuta automáticamente entre certificados:
    *   **Identidad Personal (20132967572):** Utilizada para servicios de Consulta de Padrón A13.
    *   **Identidad Empresa (30715603973):** Utilizada para servicios de Emisión (MTXCA/WSFE).
*   **Dependencias Críticas:** Requiere las librerías `zeep` y `lxml` en el entorno virtual (`venv`) del backend.
*   **Manejo de Errores:**
    *   Si RAR falla (timeout, sin internet), el backend captura la excepción y retorna un JSON con `error`, evitando caídas 500.
    *   **Archivos Temporales:** Se usan UUIDs para los XML de firma (`temp_auth_*.xml`) para evitar colisiones en entornos concurrentes.

## 10. ARQUITECTURA DE CLIENTES HÍBRIDOS (INFORMAL VS FORMAL)
Implementado en V6.3, el sistema permite la convivencia de dos tipos de clientes:
*   **Formal (Verde/Amarillo):** Tiene CUIT válido (11 dígitos). Requiere Domicilio Fiscal estricto. Validado contra ARCA.
*   **Informal (Rosa Chicle):** Sin CUIT o CUIT genérico. No requiere Domicilio Fiscal estricto (puede ser solo Entrega).
    *   **UX Pink Mode:** Se identifica visualmente con texto Fucsia y brillo neón en listados y fichas.
    *   **Transición:** Si un cliente Informal carga un CUIT, el sistema activa automáticamente el puente ARCA para completar sus datos fiscales y formalizarlo.
*   **Infiltración Vanguard (Verification Firewall):** La interfaz `AfipComparisonOverlay.vue` actúa como un cortafuegos visual:
    *   **Detección de Cambios:** Compara campo por campo (Razón Social, IVA, Dirección) y resalta inconsistencias en amarrillo neón.
    *   **Confirmación Requerida:** Los datos de AFIP solo se inyectan en el formulario local si el usuario presiona "Infiltrar Datos".
    *   **Domicilios Split:** El formulario de alta permite llenar solo la sección "Logística" (Derecha) y el sistema auto-completa la sección "Fiscal" (Izquierda) para evitar bloqueos de validación.

## 11. PERSISTENCIA INTELIGENTE (ARCA SYNC)
* **Problema:** El sistema protege los domicilios en actualizaciones (`UPDATE`) para evitar sobrescrituras accidentales.
* **Solución (Biotenk Fix):** En `ClienteInspector.vue`, se implementó una actualización explícita manual del domicilio fiscal dentro de la función `save()`. Si el formulario detecta cambios (vía infiltración ARCA), se dispara un `updateDomicilio` independiente antes de persistir los cambios generales del cliente.
* **Excepción:** Cuando se ejecuta una validación ARCA exitosa, el frontend activa una bandera `forceAddressSync`.
* **Comportamiento:** Al guardar, si esta bandera está activa, `saveCliente` incluye explícitamente el objeto `domicilios` en el payload, forzando al backend a actualizar la dirección fiscal con la "Verdad Oficial" de AFIP.

## 12. MÓDULO DE INGESTA AUTOMÁTICA (PDF ENGINE V6.5)
Incorporado en V6.4 (2026-02-19) y consolidado en V6.5 (2026-02-28).
*   **Motor:** `pypdf` + `fpdf2` + Regex Heurística (Backend Python).
*   **Estrategia de Parseo:**
    *   **Encabezados Compactos:** Soporta formatos donde CUIT y Razón Social comparten línea (ej: Lavimar).
    *   **Ítems por Anclaje:** Utiliza palabras clave como "unidades" o "litros" para extraer descripciones y cantidades, ignorando saltos de línea rotos en tablas complejas.
*   **Lógica "Confianza Ciega" (Trust Protocol):**
    *   El sistema asume que la Factura es la verdad.
    *   **Get-or-Create:** Si el CUIT detectado no existe en la base, se crea un Cliente nuevo automáticamente con los datos del PDF.
    *   **Dirección:** Se asigna una dirección fiscal genérica para cumplir con el modelo de datos, permitiendo al operador corregirla post-ingesta.
*   **Manejo de Errores:**
    *   El backend captura trazas completas de error y las envía al frontend para que el usuario sepa exactamente por qué falló un PDF (ej: "Archivo vacío", "No es PDF de texto").
    *   **Actualización V6.5 (Upsert Inteligente):** El sistema ahora verifica existencia por CUIT. Si el cliente existe con status bajo (<13), se actualiza a **Flag 13** (Gold Candidate) y se elimina el flag 'Virgin'. Si es nuevo, se inserta directamente en Flag 13 con estado 'PENDIENTE_AUDITORIA'.
    *   **Corrección Regex:** Se modificó el motor para escanear el texto crudo (`raw_text`) antes de limpiar, solucionando fallos en facturas compactas (LAVIMAR).
    *   **Workflow Frontend Asistido:** Implementado en `IngestaFacturaView.vue`, el componente cruza la "Infiltración Vanguard". Cualquier cliente derivado del PDF cuya validación AFIP falte (Nivel < 13) fuerza la apertura perentoria de `ClienteInspector.vue`.
    *   **Doctrina de Evolución (4-Bytes):** A nivel backend (`service.py`), los clientes insertados on-the-fly (`estado_arca='PENDIENTE_AUDITORIA'`, Flag=15 Virgen) pierden la bandera Virginity (`& ~ClientFlags.VIRGINITY`) mutando al nivel 13 Gold al momento exacto de formular/confirmar la carga en remitos.


## 13. PROTOCOLO GENOMA V14 (BITMASK DE IDENTIDAD)
Implementado en V14.5 y saneado en V14.8 (Marzo 2026), el sistema gestiona la identidad comercial mediante una máscara de bits (Bitmask) simplificada:
- **Bit 0 (1):** `EXISTENCE` (Activo en DB).
- **Bit 1 (2):** `VIRGINITY` (1=Sin movimientos / 0=Operado).
- **Bit 2 (4):** `GOLD_ARCA` (Validado contra satélite RAR).
- **Bit 3 (8):** `V14_STRUCT` (Protocolo Apolo activo).
- **Bit 4 (16):** `SABUESO_ALERT` (Alerta de riesgo o deuda).

### Lógica de Dominancia Visual:
1. **Rosa (9 o 11):** Pao de Tandil / Informal (Bits 0+3 + Virginity opcional).
2. **Blanco Gold (13 o 15):** Validado por ARCA (Bits 0+2+3 + Virginity opcional).
3. **Amarillo:** Estado base (Pendiente de validación ARCA).
- **Bit 5 (32):** `MULTI_Sede` (Sello Azul / Compartición Legal). Se activa automáticamente si el cliente tiene más de un domicilio habilitado.
- **Bit 6 (64):** `CONSOLIDATED` (Sello de Purga V14). Indica que el registro ha pasado por el proceso de unificación de CUITs.

### Lógica de Dominancia:
El color visual de la ficha se determina por la jerarquía de bits:
1.  **Azul (32):** Multicliente (Máxima prioridad de alerta).
2.  **Blanco Gold (4):** Validado por ARCA.
3.  **Rosa (16):** Operador OK / CUIT Genérico.
4.  **Amarillo (8):** Estado Base (Pendiente).

### Consolidación de Base de Datos (Marzo 2026):
Se implementó la política de **1 CUIT = 1 Registro Maestro**. 
- El script `consolidate_clients_v64.py` se encarga de unificar duplicados, transfiriendo pedidos e historial al registro principal.
- Los domicilios secundarios se mantienen como "Sedes" vinculadas al mismo CUIT bajo el bit `MULTI_Sede`.

### Seguridad de Datos (Escudo de Virginidad):
Durante la validación de AFIP, el sistema preserva el estado del Bit 1. Un cliente que ya ha operado comercialmente (Bit 1 = 0) nunca volverá a recibir el estado "Virgen" por una inyección de datos externos.
