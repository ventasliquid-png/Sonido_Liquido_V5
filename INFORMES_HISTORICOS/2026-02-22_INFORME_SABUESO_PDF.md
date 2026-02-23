# 📄 INFORME TÉCNICO V14: RELEVAMIENTO DE INGESTA PDF (SABUESO LOCAL)

**Para:** Almirante (Comando Táctico)
**De:** Antigravity (Operaciones Gy)
**Fecha:** 2026-02-22
**Asunto:** Estado Actual y Cableado de la Ingesta de PDFs de ARCA.

---

## 1. ESTADO ACTUAL: ¿DEPENDENCIA EXTERNA?

Tras un barrido exhaustivo por el código fuente (`backend/remitos/pdf_parser.py`, `backend/scripts/miner.py`) y la bitácora histórica, he detectado un hecho táctico crucial: **Actualmente NO existe una dependencia activa de Google Vision, Document AI, ni Gemini para la lectura de PDFs.**

El sistema actual **ya es 100% local y soberano**, aunque se encuentra fragmentado en dos motores de extracción distintos. 

No hay llamadas a APIs externas en el flujo de `process_pdf_ingestion`.

## 2. PUNTOS DE CONEXIÓN (EL CABLEADO ACTUAL)

El flujo de la ingesta de un PDF desde el frontend opera de la siguiente manera:

1.  **Recepción (El Puerto):** El frontend (Vue) envía el PDF a través del endpoint `POST /remitos/ingesta-pdf` (ubicado en `backend/remitos/router.py`).
2.  **Procesamiento (La Aduana):** El router deriva el archivo (en memoria) a la función asíncrona `process_pdf_ingestion(file)` ubicada en `backend/remitos/pdf_parser.py`.
3.  **Extracción (El Sabueso Básico):** Dentro de `pdf_parser.py`, la función `extract_text_from_pdf` utiliza la librería **`pypdf`** para extraer el texto crudo.
4.  **Parseo (Heurística):** La función `parse_invoice_data(text)` aplica reglas de Expresiones Regulares (Regex) para identificar:
    *   CUITs y Razón Social (buscando patrones vecinos y saltando el CUIT emisor `30-71560397-3`).
    *   Datos del Comprobante (Punto de Venta, CAE, Vencimiento).
    *   Items (Cantidades seguidas de palabras clave como "unidades", "litros").

## 3. LÓGICA HEREDADA Y DEUDA TÉCNICA (EL VERDADERO SABUESO)

Al revisar los registros históricos (Específicamente el informe del 2026-02-19 sobre `FIX_MINER_Y_ESTRATEGIA_UPSERT`), encontramos un componente "Shadow" muy valioso: el script local **`scripts/miner.py`**.

Este script contiene heurísticas mucho más robustas que las que están conectadas a la ruta web actual, revelando una discrepancia de motores:

*   **Motor Web (`pdf_parser.py`):** Usa `pypdf`. Funciona rápido pero es propenso a errores de formato (une palabras, rompe CUITs) en facturas densas (ej. formato *Lavimar*).
*   **Motor Script (`miner.py`):** Utilizaba `pdfplumber`. Es mucho más preciso para extraer datos tabulares y lidiar con PDFs compactos u ofuscados. 

El documento histórico del 19 de febrero estipulaba explícitamente como "Deuda Técnica" la necesidad de:
> "Refactorizar pdf_parser.py: Reemplazar pypdf por pdfplumber y portar la lógica del miner.py"

### Reglas de Negocio Ya Definidas a Reutilizar:
Sí, contamos con un arsenal de heurísticas que podemos reciclar sin inventar nada:
1.  **Regex de CUITs Segura:** Detección de validaciones de 11 dígitos priorizando el CUIT del cliente sobre el del emisor.
2.  **Anclaje de Cantidades (Anchor Strategy):** La detección de ítems basada en la métrica "cantidad + unidad de medida" en lugar de posiciones absolutas.
3.  **Lógica UPSERT de Ingesta:** La validación de subir el flag del cliente nuevo a `PENDIENTE_AUDITORIA` para evitar pisar datos de clientes veteranos.

## 4. CONCLUSIÓN Y RUTA DE ACCIÓN

No tenemos que desconectar servicios en la nube porque la ingesta ya opera localmente. Lo que debemos hacer es **evolucionar el "Sabueso Básico" (`pypdf`) actual hacia la versión "Sabueso Avanzado" heredada del `miner.py` (`pdfplumber`)**.

### Misión Propuesta para Sustitución de Motor:
1.  Instalar/asegurar `pdfplumber` en el backend.
2.  Desconectar `pypdf` de `backend/remitos/pdf_parser.py`.
3.  Reescribir el analizador inyectando el código de extracción pulido heredado del incidente del "Miner".
