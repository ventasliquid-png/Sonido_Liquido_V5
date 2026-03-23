# 📘 MANUAL TÉCNICO V5: "INDEPENDENCIA"
**Versión:** 1.4 Release (Updated V15.1.5 Blindado)
**Fecha:** 19-03-2026

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

## 15. SISTEMA DE PAPELERA GLOBAL & PROTECCIÓN HISTÓRICA (GENOMA 14.8.1)
Implementada para prevenir la pérdida irreversible de datos comerciales por errores humanos en "Utilidades Maestras".
* **Papelera de Registro**: La tabla `papelera_registros` actúa como un búfer de seguridad. Antes de cualquier `DELETE` físico en el backend, el objeto es serializado recursivamente a JSON (limpiando tipos `Decimal`, `UUID` y `datetime`) y persistido en esta tabla.
* **Blindaje de Historial**: El sistema identifica registros históricos mediante el Bit 1 de `flags_estado` (0 = Histórico). 
    - **Prohibición**: El backend rechaza (403 Forbidden) cualquier solicitud de eliminación física para estos registros.
    - **Visualización**: En la interfaz de Utilidades Maestras, estos registros aparecen "grisados" (opacidad 60%) y con el botón de borrado deshabilitado.
* **Mecanismo de Rescate**: Aunque el borrado está bloqueado, la funcionalidad de reactivación ("Rescate") permanece disponible, permitiendo devolver registros históricos de la baja lógica sin comprometer la integridad de la base de datos principal.

## 16. SOBERANIA OPERATIVA V14.8.4 (PIN 1974)
Implementada el 18-03-2026. El criterio humano de carga prevalece sobre ARCA/AFIP.

### Promocion Automatica 15->13 (Veterano de Facto)
Si un cliente posee los 4 Pilares de Integridad de Carga al guardar, el sistema lo promueve automaticamente:
- **Bit 1 OFF** (`IS_VIRGIN = 2`): Quita el estado Virgen. El cliente pasa de Nivel 15 a Nivel 13 (Veterano Operado).
- **Bit 20 OFF** (`PENDIENTE_REVISION = 1048576`): Limpia el estado Amarillo.

**Los 4 Pilares:** razon_social + lista_precios_id + segmento_id + domicilio_fiscal.calle (>2 chars).

### Escudo Doble
- **Frontend** (`ClientCanvas.vue`): Opera antes de `payload.flags_estado = currentFlags` en `saveCliente`.
- **Backend** (`service.py`): Verifica 4 Pilares post-setattr en `update_cliente` y fuerza la mutacion.

### Color Independiente de AFIP
`getClientColorMode` ya no depende de `estado_arca`. Color blanco = `!(flags & 1048576)`. La lupa AFIP ya no es el unico camino al blanco.

### Lupa No Destructiva
`consultarAfip` muestra confirm() antes de sobreescribir una direccion fiscal manual con dato de ARCA. Si cancela, conserva la correccion manual.

## 17. REMITO MANUAL (SERIE 0015-)
Implementado el 19-03-2026 para permitir logística sin facturación previa (Clientes Rosa/Informales).

### Arquitectura de Creación:
*   **Ghost Pedidos**: El sistema genera un `Pedido` interno con `origen='MANUAL'` para mantener la integridad de la base de datos.
*   **Numeración**: Los remitos manuales utilizan la serie `0015-`, iniciando en `00003001` (Criterio de Continuidad Carlos).
*   **Resolución de Clientes**: Soporta clientes existentes o creación "al vuelo" mediante el modal `ClientCanvas`.
*   **Endpoints**:
    *   `POST /remitos/manual`: Recibe `ManualRemitoPayload`.
    *   `GET /remitos/{id}/pdf`: Genera el PDF oficial sobre la serie 0015.

## 18. EDICIÓN TÁCTICA DE INGESTA (EDITABLE GRID)
Mejora al motor OCR para permitir corrección humana de errores de lectura.
*   **Frontend**: `IngestaFacturaView.vue` utiliza una tabla de inputs reactivos conectada al `parsedData.items`.
## 19. SEGURIDAD DE SINCRONIZACIÓN: PROTOCOLO OMEGA V5.2 (BLINDADO)
Implementado el 19-03-2026 para evitar desincronías entre los entornos de la Oficina y Casa.
*   **Ojo de Halcón (`audit_v5.py`)**: Herramienta de auditoría física que rastrea cambios en disco en las últimas 12 horas.
*   **Bloqueo de PIN 1974**: El sistema tiene prohibido solicitar el PIN de cierre si existen discrepancias entre el estado de Git y los cambios físicos detectados en el disco.
*   **Certificación de Salida**: Es obligatorio ejecutar `git show --name-only HEAD` tras cada push para validar la inyección física de los commits.

## 20. MEMORIA DE SESIÓN (PROTOCOLO ALFA)
*   **Staging Early Check**: Al iniciar, el agente debe declarar la lista `ARCHIVOS_SESION` basándose en el `git status -s` inicial.
*   **Protección de Rama**: El sistema valida estrictamente la permanencia en `atenea-v5-vault-final`. Cualquier derivación no autorizada activa una ALERTA ROJA.

## 21. EDICIÓN DE REMITOS ADMITIDOS (RESTORE V5.2)
Implementado el 20-03-2026 para permitir correcciones en remitos ya generados (especialmente de ingesta).
*   **Backend**: 
    *   `PATCH /remitos/{id}`: Soporta actualización de cabecera (`numero_legal`, `cae`, `vto_cae`, `transporte_id`, `domicilio_entrega_id`).
    *   **Restricción**: Solo permitido para remitos en estado `BORRADOR`.
*   **Frontend**:
    *   `RemitoListView.vue`: Captura `@dblclick` sobre la fila del remito.
    *   **Modal de Edición**: Carga dinámicamente los domicilios del cliente asociado al pedido del remito.
*   **Parche Incompleto (Deuda Técnica)**: 
    *   Falta edición de bultos y valor declarado.
    *   Falta edición de ítems (cuerpo) post-generación.
    *   SISTEMA EN ESTADO CRÍTICO (BIT 3) por deuda de integridad en logística.

## 22. SOBERANÍA DEL ADDRESS HUB (V5.2.1)
Implementada el 23-03-2026 para consolidar la independencia de los domicilios.
*   **Seeding Protocol**: Uso de `seed_hub.py` para migración masiva.
*   **Deduplicación Semántica**: El sistema agrupa direcciones idénticas bajo un único ID del Hub, incrementando el `usage_count`.
*   **Vínculos (Bit 21)**: Los domicilios migrados se marcan con el Bit 21 en `domicilios_clientes` para indicar que son espejos de datos legacy.
*   **Registry Unification**: Se prohíbe la importación de `Base` sin el prefijo `backend.`. Todas las tablas deben converger en el registro de `backend.core.database` para evitar errores de mapeo circular.
