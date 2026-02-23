# INFORME DE SISTEMAS: OPERACIÓN "LIMADO PDF Y ABM CLIENTES"

**Fecha:** 23 de Febrero de 2026
**Objetivo:** Estabilizar y perfeccionar el flujo de ingesta de facturas PDF, el enrutamiento automático hacia el alta de nuevos clientes y la sincronización de estados con el padrón AFIP/ARCA.

A continuación se detalla el resumen técnico de los incidentes resueltos y los parches aplicados en la sesión actual, listos para revisión de Arquitectura.

---

## 1. Corrección en la Extracción del Número de Factura (Punto de Venta)
*   **Problema:** El sistema estaba asignando un prefijo estático harcodeado (`0016-`) a todos los números de comprobante extraídos de los PDFs cargados, ignorando el Punto de Venta real de la factura.
*   **Solución:** Se implementó una rutina de extracción con Expresiones Regulares (Regex) en el módulo `backend/remitos/pdf_parser.py`.
*   **Resultado:** El motor ahora busca dinámicamente el patrón `"Punto de Venta: \d+"`, lo extrae, lo formatea (ej. `0001`) y lo concatena con el número de comprobante para generar un identificador preciso (ej. `0001-00002314`).

## 2. Doctrina de Miembro Pleno (Autovalidación de Clientes Ingestados)
*   **Problema:** Los clientes nuevos que nacían a partir de la ingesta de un PDF se creaban por defecto en un estado "Pendiente/Virgen" (Estado 15 - Inactivo), lo cual obligaba a una validación manual posterior innecesaria, ya que los datos provenían de una factura oficial.
*   **Solución Frontend (`ClientCanvas.vue`):** Se inyectó lógica para que, si el cliente proviene del flujo automático del PDF (`autoAfip=true`), el payload nazca con `flags_estado = 13` (Validado, Gold, Activo).
*   **Solución Backend (`service.py`):** Se descubrió que la función `create_cliente` ignoraba el campo `flags_estado` enviado por el frontend. Se parcheó para que persista correctamente el genoma enviado en el momento del Alta.
*   **Resultado:** Todo cliente nacido de un PDF se guarda directamente como operativo y activo.

## 3. Reparación del Toggle "Activar/Desactivar" Cliente
*   **Problema:** El interruptor de "Baja Lógica / Activar" en la grilla dinámica (`HaweView.vue`) y dentro del inspector (`ClienteInspector.vue`) no guardaba su estado. El cliente volvía a aparecer inactivo tras intentar activarlo.
*   **Solución:** Se depuró la función `update_cliente` en el backend (`service.py`). El frontend enviaba el nuevo booleano `activo`, pero también enviaba el viejo `flags_estado`. El backend convertía el booleano al bitmap correcto, pero luego iteraba sobre el payload y pisaba el bitmap recién calculado con el genoma obsoleto. Se implementó una **sincronización bidireccional prioritaria** del genoma antes de la asignación general de atributos.
*   **Resultado:** La interfaz gráfica (tanto listas como modales) ahora guarda instantáneamente las bajas lógicas y reactivaciones con éxito total.

## 4. Blindaje del Puente AFIP (Caída por `NoneType: formaJuridica`)
*   **Problema:** Al consultar a la AFIP por personas físicas (Ej. CUIT 27304037976), el servidor colapsaba arrojando un Error 500 y devolviendo "'NoneType' object has no attribute 'upper'".
*   **Causa:** La AFIP envía el nodo `formaJuridica` como `null` para personas físicas. El módulo satélite `rar_core.py` (RAR V1) intentaba ejecutar `.upper()` ciegamente sobre ese valor vacío.
*   **Solución Core:** Se parcheó `rar_core.py` incorporando un fallback seguro: `forma_juridica = (datos.get('formaJuridica') or '').upper()`.
*   **Solución Memoria Caché:** Como el servidor de FastAPI mantenía la librería fallida cacheada en memoria RAM, se inyectó una instrucción `importlib.reload(rar_core)` en el `afip_bridge.py` para obligar al servidor a consumir las correcciones de código instantáneamente en caliente, sin necesidad de reiniciarlo.
*   **Observación Técnica (Arquitectura):** Se detectó que el Web Service A13 de AFIP oculta los datos impositivos (`datosRegimenGeneral`) para individuos por leyes de secreto fiscal. Debido a esto, la heurística deduce "CONSUMIDOR FINAL" por descarte para personas físicas, requiriendo que el operador asigne "Responsable Inscripto" manualmente si fuera el caso, pero trayendo los demás datos a salvo (Nombre, Domicilio, Localidad, etc.).

## 5. Doctrina de Preservación Fiscal (Personas Físicas)
*   **Problema:** Al procesar un PDF de una persona física (CUITs `20-`, `23-`, `24-`, `27-`), la AFIP oculta su condición de IVA (como Responsable Inscripto) por leyes de secreto fiscal, forzando a nuestro sistema a rebajarla erróneamente a "Consumidor Final". Sin embargo, el PDF sí contenía la condición correcta.
*   **Solución:** Se implementó una barrera de contención en el frontend (`ClientCanvas.vue` y `ClienteInspector.vue`). 
*   **Resultado:** Si el sistema detecta que el cliente es una persona física y ya cuenta con una condición de IVA pre-cargada (proveniente de la extracción del PDF original), el radar de ARCA/AFIP respetará ese dato y no lo sobrescribirá con el "Consumidor Final" por defecto.

---
*Informe generado por Protocolo de Asistencia Técnica - Estado de los módulos: OPERATIVO.*
