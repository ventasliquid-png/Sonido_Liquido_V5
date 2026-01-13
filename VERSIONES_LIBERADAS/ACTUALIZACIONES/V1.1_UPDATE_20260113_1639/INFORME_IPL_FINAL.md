# INFORME FINAL: PROTOCOLO IPL (Initial Program Load)
**Fecha:** 2025-12-28
**Estado:** SISTEMA CERTIFICADO
**Referencia:** Operativo Rescate Data Master

## 1. El Diagnóstico "Frankenstein"
Al iniciar la sesión, detectamos una desincronización crítica entre la base de datos local (`pilot.db`) y la nube (IOWA):
- **Local:** Tenía los precios y costos actualizados, pero había perdido los SKUs y la clasificación por Rubros (estaba todo en "General").
- **Cloud (IOWA):** Tenía los SKUs y los 23 rubros clasificados, pero no tenía precios.
- **Resultado:** Cualquier cambio en el local no se reflejaba en la inteligencia de la nube y viceversa. Un sistema con dos cerebros desalineados.

## 2. Razones del Desvío (Por qué 271 vs 303)
La disparidad de números se debió a:
1.  **Duplicados por Tipeo:** Diferencias mínimas en nombres (ej: "Acohol" vs "Alcohol") hicieron que se crearan registros dobles en la nube.
2.  **Items de Control:** En IOWA se habían inyectado ítems como `ENTREGADO`, ` Foam` y `Dto 5%` que no son productos reales, sino registros de operación.
3.  **Depuración Local:** El archivo local de 271 productos es la lista "legal" y depurada.

## 3. Acciones Ejecutadas (Rescate Maestro)
Para sanar el sistema, realicé las siguientes maniobras:
- **Reducción de Rubros:** Se eliminaron 20 rubros experimentales, dejando solo **General**, **Guantes** y **Ropa Descartable**.
- **Inyección de SKUs:** Se recuperaron 269 SKUs de la nube y se pegaron en la base local.
- **Auto-Clasificación Humana-Bot:** Clasifiqué los 271 productos locales usando reglas semánticas (ej: si dice 'guante' va a 'Guantes').
- **Purga IOWA:** Se eliminaron los 34 excedentes de la nube para que IOWA vuelva a ser un espejo fiel del local.

## 4. Evolución Técnica: Motor Híbrido V6
Más allá de los datos, hoy el sistema subió de nivel:
- **Prioridad Híbrida:** Ahora puedes fijar un precio artesanal, un CM objetivo, o dejar que el Rubro decida el margen. El sistema es más flexible y protege tu rentabilidad.
- **Búsqueda por SKU:** El buscador ahora es omnicanal (Nombre, Código o SKU).

## 5. Prevención: Cómo evitar futuros Frankesteins
Para que esto no vuelva a pasar, hemos establecido el **Protocolo de Higiene de Datos**:
1.  **Un Solo Capitán:** El `pilot.db` local manda en la operación. Los cambios de precios se hacen ahí.
2.  **Sincronización Semanal (o tras cambios):** Se debe correr habitualmente `python scripts/reconcile_master_data.py`. Este script es el "pegamento" que mantiene alineados ambos cerebros.
3.  **Uso de SKUs:** Nunca cargar un producto nuevo sin SKU. El SKU es el ADN del producto; si el ADN es el mismo, el sistema podrá sincronizarlo siempre.

---
**Conclusión:** El sistema Sonido Líquido V5 ha pasado la prueba del IPL. La "Casa está Limpia" y los datos están sincronizados. 🥂
