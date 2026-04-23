# INFORME ESTRATÉGICO: Calibración de Soberanía Fiscal y Definición de Ingesta Asíncrona

**Fecha:** 2026-04-23  
**Sistema:** Sonido Líquido V5  
**Estado de Avance:** Calibración Arquitectónica (NOMINAL GOLD)

---

## 1. Contexto de la Sesión
Tras la implementación del **Motor Bipolar** y el **Centro de Liquidación** en la sesión anterior, esta jornada se centró en la inducción operativa y la validación de la arquitectura de **Soberanía Fiscal**. El objetivo fue despejar dudas sobre el origen de los datos fiscales (CAE/Nro de Factura) y proyectar la automatización de la "Fase 2".

## 2. Definiciones Tácticas

### A. La Soberanía del Cálculo
Se ratificó que HAWE actúa como el cerebro contable. El sistema realiza el prorrateo de descuentos globales sobre cada ítem para asegurar que el neto gravado y el IVA coincidan exactamente con las exigencias de ARCA (AFIP). El usuario utiliza la **Plantilla Copia-Fácil** para trasladar estos valores a la web oficial sin riesgo de error de redondeo.

### B. El Origen de los Tokens (CAE)
Se clarificó el flujo de datos para la Fase 1:
1.  **HAWE**: Genera el borrador y "sopla" los montos.
2.  **Usuario**: Emite la factura en AFIP manualmente.
3.  **AFIP**: Genera el CAE y el Número correlativo.
4.  **Usuario**: Ingresa esos datos en HAWE para "sellar" la factura.

### C. Fase 2: Ingesta Asíncrona (Estrategia)
Se identificó la oportunidad de eliminar el paso manual de "Copia-Pega" del CAE. La estrategia acordada para la próxima sesión es:
- Implementar un motor de **Ingesta de Comprobantes**.
- El usuario podrá arrastrar el PDF de la factura (o un CSV de AFIP) y el sistema "leerá" los datos para sellar automáticamente los borradores pendientes.

## 3. Estado de Salud del Sistema
- **Bitmask**: 851 (SOBERANO, TRINCHERA, PARIDAD_DB, ORIGEN_CA, SABUESO_READY, SABUESO_TOKEN).
- **Paridad**: D↔P confirmada.

## 4. Próximos Pasos
- [ ] Desarrollo de la lógica de parsing de PDF para facturas de venta.
- [ ] Implementación de la "Drop-Zone" en el Centro de Liquidación.

---
*Reporte finalizado y sellado. Protocolo OMEGA ejecutado bajo PIN 1974.*
