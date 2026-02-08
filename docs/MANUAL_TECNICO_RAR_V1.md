# 📘 MANUAL TÉCNICO: INTEGRACIÓN RAR V1 (SATÉLITE)

**Versión:** 1.0
**Fecha:** 08-02-2026
**Estado:** OPERATIVO (Standalone)

## 1. CONCEPTO ESTRATÉGICO
RAR (Remitos Arca & Recolector) es una "Esclusa de Verdad Fiscal" independiente de Sonido Líquido V5.
*   **Misión:** Validar CUITs contra AFIP (Padrón A13) y generar Remitos PDF legales.
*   **Arquitectura:** Satélite "Air Gapped". No comparte código con V5, solo intercambia datos.

## 2. FLUJO DE DATOS (EL PUENTE)
El intercambio de información se realiza mediante archivos planos, garantizando el desacople total.

1.  **Origen:** BAS (Legacy) o V5 (Futuro) generan `REPORTE 2.TXT`.
2.  **Ingesta:** El operador (Tomy) carga el archivo en la Web UI de RAR (`localhost:5000`).
3.  **Proceso:**
    *   RAR consulta su `cantera_arca.db`.
    *   Si el cliente es nuevo, RAR se conecta a AFIP (WSAA) y lo "cosecha".
4.  **Salida:** PDF Remito "Vitaminizado" (Datos fiscales + Precios ocultos).

## 3. COMPONENTES DEL SATÉLITE
Ubicación física: `C:\dev\RAR_V1`
*   `app.py`: Servidor Web Flask (Interfaz de Operador).
*   `rar_core.py`: Lógica de negocio (3 Cajones de AFIP).
*   `remito_engine.py`: Motor de renderizado PDF (FPDF2).
*   `cantera_arca.db`: Base de datos SQLite (Single Source of Truth Fiscal).

## 4. MANTENIMIENTO TÉCNICO
*   **Comando de Inicio:** `DESPERTAR_RAR.bat` o `python app.py`.
*   **Certificados:** Ubicados en `certs/`. Deben renovarse cada 2 años.
*   **Backup:** La `cantera_arca.db` debe incluirse en la rutina de backup de Google Drive.

## 5. PROTOCOLO DE INCIDENTES
Si RAR falla (ej: AFIP caído), el sistema V5 **NO SE DETIENE**. La operación comercial sigue, y la emisión de remitos se posterga o se hace manual, pero la venta no se bloquea.
