# 📄 INFORME TÉCNICO: RESUMEN DE ACTUACIONES (SABUESO, RADAR Y TELEMETRÍA)

**Para:** Arquitecta Nike
**De:** Antigravity (Operaciones Gy)
**Fecha:** 2026-02-22
**Rama de Trabajo Actual:** `feature/sabueso-local-plumber`

---

## 1. RELEVAMIENTO TÁCTICO INICIAL
Se ordenó investigar el motor de ingesta de PDFs de facturas ARCA para eliminar dependencias externas (Vertex AI / Document AI / Gemini).
*   **Hallazgo Forense:** El endpoint actual de ingesta (`backend/remitos/pdf_parser.py`) ya operaba en entorno local 100% utilizando la librería `pypdf` y expresiones regulares básicas. NUNCA estuvo conectado a las APIs de Google para esta tarea específica.
*   **Deuda Técnica Detectada:** `pypdf` presentaba fallos graves al intentar leer PDFs comprimidos (ej. facturas de Lavimar), uniendo cadenas de texto y destruyendo la integridad del CUIT y la Razón Social.
*   **Solución Herencia:** Se identificó que un script antiguo (`backend/scripts/miner.py`) utilizaba `pdfplumber` con un rendimiento vastamente superior, pero no estaba conectado al core de la API web.

## 2. REFACTORIZACIÓN DEL SABUESO PDF (V2)
Se inició la cirugía para actualizar el motor de inyección del sistema:
*   Se creó la rama aislada `feature/sabueso-local-plumber` para salvaguardar `main`.
*   Se inyectó `pdfplumber` en el `pdf_parser.py`.
*   **Extracción CUIT (Dual Regex):** Se implementó una estrategia de embudo de 3 capas para asegurar la extracción del CUIT del cliente ignorando siempre el CUIT Emisor (Sonido Líquido).
*   **Extracción Items (Estrategia Anchor):** Se portó la lógica de anclaje de unidades de medida (litros, bultos, unidades) desarrollada en el Miner V2 para extraer descripciones y cantidades intactas de los renglones de la tabla de la factura.

### 2.1 EL CAMBIO DE PARADIGMA (DIRECTIVA ACTUAL)
Bajo la última directiva del Comando, la heurística de Razón Social y Domicilio vía Regex desde el PDF se descarta por insegura.
**Nuevo Protocolo:** El Sabueso PDF se limita a extraer el **CUIT**, los **ÍTEMS** y el **CAE**. El CUIT extraído se inyecta en el **Consultor AFIP/RAR** puenteado en la V5 para delegarle la responsabilidad de traer la Razón Social, la Condición Frente al IVA y los Domicilios Oficiales de manera 100% limpia y validada.

## 3. SISTEMA DE TELEMETRÍA Y CONTADORES (EL NUEVO RADAR)
Simultáneo al trabajo de PDF, se construyó un ecosistema autónomo para medir el uso estratégico de la IA conversacional (Atenea).

### A. Model Discernitor (Cerebro)
Se amplió el servicio `ModelDiscernitor` para incluir persistencia en el backend (`atenea_telemetry.json`).
*   **Doble Odómetro:** Gestiona un contador volátil para la Sesión (reinicia al apagar el server backend) y un Odómetro Total (Global diario, resistente a caídas).
*   **Auto-Purga:** El odómetro total se formatea a 0:
    1.  Por cambio de día calendario.
    2.  Si el "Escudo de Muerte" recibe un Error 429 de Google, se asume que la cuota PRO de 1 hora se agotó, por lo que los contadores porcentuales carecen de valor táctico en estado degradado.

### B. UI & Frontend (Radar Interno)
El componente `AteneaChat.vue` se modificó para abandonar la medición de estado local (pinchar la respueta y sumar 1 a una variable de Vue) a favor de un **Polling**. El Frontend ahora consulta al endpoint `/atenea/telemetria` cada 1 segundo y representa los porcentajes reales extraídos de la memoria/disco del servidor.

### C. Radar Flotante (Widget Externo)
Se desarrolló un script auxiliar en Python puro (`scripts/radar_flotante.py`) implementando *Tkinter* con diseño Borderless/Alpha.
*   **Comportamiento:** Se superpone a las ventanas del entorno de escritorio del comando. Perfora el endpoint de telemetría por polling y arroja los estadísticos.
*   **Advertencias Visuales:** Pinta su fondo de "Red Alert" si el Backend reporta una penalización 429 en la IA, informando del tiempo (HH:MM:SS) restante para rehabilitar el motor PRO.
*   **Status de Red:** Monitorea la vida del Backend. Al mostrar "Backend Inactivo", certifica que el proceso de Uvicorn/FastAPI colapsó, se reinició o fue detenido intencionalmente por el piloto.

---

**Estado Operativo:** El Sistema se encuentra estable, la rama protegida, y listos para ejecutar la integración final del Sabueso con el protocolo RAR.
