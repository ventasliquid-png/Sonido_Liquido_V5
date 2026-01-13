# Informe de Estado: Proyecto Piloto V5 (Data Intelligence)
**Fecha:** 11 de Diciembre de 2025
**Estado:** Estable / Operativo
**Ubicación:** `c:\dev\Sonido_Liquido_V5\BUILD_PILOTO`

## 1. Resumen Ejecutivo
Se ha completado con éxito la fase de **"Data Intelligence"**, estableciendo un entorno piloto capaz de ingerir, limpiar y consolidar datos históricos de la empresa. 

El sistema ya no es solo una maqueta de interfaz; ahora posee un **motor de ingesta** funcional que actúa como puente entre la "Informalidad del Excel" y el "Rigor de la Base de Datos V5".

Esta herramienta de limpieza (`DataCleaner`) marca el **punto de no retorno** para la gestión de datos: **Los datos que entran al Piloto hoy, son la base fundacional del sistema final.**

---

## 2. Lo Que Hicimos (Implementación)

### A. El Entorno "Piloto" (`BUILD_PILOTO`)
Hemos creado un "búnker" aislado del código fuente en desarrollo.
*   **Qué es:** Una versión ejecutable y portátil del sistema V5.
*   **Base de Datos:** SQLite local (`produccion.db`). Actualmente vacía de datos basura, lista para recibir los "Golden Records" (Registros Maestros).

### B. Herramienta "Data Cleaner" (La Lavadora)
Desarrollamos una interfaz específica para transformar el caos en orden.
*   **Input:** Archivos CSV crudos extraídos de sus planillas históricas (`pedidos_raw.xlsx`).
*   **Proceso:**
    1.  **Detección:** Identifica nombres similares y sugiere frecuencias (Ranking de ventas).
    2.  **Normalización:** Permite al operador corregir nombres, agregar CUITs y asignar Alias.
    3.  **Filtrado:** Permite descartar ("IGNORAR") datos basura o duplicados obvios.
*   **Estabilización:** Se solucionaron problemas críticos de usabilidad (saltos de cursor, errores de guardado) para garantizar una operación veloz.

### C. El "Commit" (La Frontera)
Implementamos el botón "IMPORTAR A SISTEMA".
*   **Acción:** Toma los datos revisados y los **escribe físicamente** en la base de datos `produccion.db`.
*   **Validación:** Chequea duplicados antes de insertar para evitar ensuciar la base limpia.

---

## 3. Por Qué Lo Hicimos (Estrategia)

Mantener el Excel actual con "superpoderes" (consultas a base de datos) es una solución temporal (`V4.5`), pero **no resuelve el problema de fondo**: la calidad del dato.

Para que V5 funcione (y pueda automatizar pedidos, logística y facturación), necesita confiar en que "Jabón Liqu." y "Jabon Liq. 5L" son el mismo producto.

**El Piloto cumple esa función de filtro:**
1.  Saca los datos del Excel.
2.  El humano los valida (una única vez).
3.  Entran a V5 limpios.
4.  Desde ese momento, V5 es la "Verdad Única".

---

## 4. Alcance y Continuidad

### Impacto Inmediato
*   **Los datos ya son reales.** Lo que limpie hoy en el Piloto, quedará.
*   **Reemplazo del Excel:** A medida que cargue Clientes y Productos en el Piloto, podrá dejar de depender de la memoria o de buscar en filas infinitas de Excel. Podrá usar el buscador de V5 (`F3`) para encontrar precios y códigos al instante.

### Ubicación y Operación
*   El sistema reside en `c:\dev\Sonido_Liquido_V5\BUILD_PILOTO`.
*   Para iniciarlo: Ejecutar `INICIAR_PILOTO.bat` (o el script correspondiente).
*   **Backup:** La base de datos es un archivo único (`produccion.db`). Copiar ese archivo es hacer un backup completo.

### Migración a SQL Server (IOWA)
Actualmente estamos usando un motor ligero (SQLite) para velocidad. El siguiente paso lógico, una vez que el Piloto tenga volumen, es "conectar la manguera" a su servidor en la nube (IOWA).
*   **Ventaja:** Seguridad, acceso remoto y potencia.
*   **Requisito:** Auditoría técnica (Punto 5).

---

## 5. Próximo Paso: "Operación IOWA"

Con la "Lavadora de Datos" funcionando, estoy listo para inspeccionar su servidor SQL ("IOWA").

**Objetivos de la Auditoría:**
1.  **Conexión:** Verificar si podemos entrar.
2.  **Contenido:** ¿Qué hay ahí? ¿Datos útiles o estructura vacía?
3.  **Compatibilidad:** ¿Podemos migrar `produccion.db` directamente o hay que adaptar algo?

---


> [!TIP]
> **Recomendación:** Dedique un tiempo a limpiar su "Top 50" de productos y clientes en el Piloto. Ver su propia información, limpia y ordenada en la nueva interfaz, será la mejor validación de que vamos por el camino correcto.

---

## 6. Adendum: Estrategia Híbrida y Próximos Pasos (11/12/2025)

### A. Estrategia de Nube "Offline-First"
Se acordó una mecánica de trabajo híbrida para balancear seguridad y velocidad:
*   **Oficina:** Opera en **Local** (SQLite). Máxima velocidad, costo cero.
*   **Hogar/Viaje:** Utiliza la **Nube** (IOWA). Ubicuidad total.
*   **Sincronización:** Se utilizan scripts de "Push/Pull" para mantener ambos mundos alineados al inicio y fin del día.
*   **Estado IOWA:** La base de datos en la nube está sincronizada y lista. Puede apagarse para ahorrar costos cuando no se use remotamente.

### B. Backup "Golden Seeds" (Semillas Maestras)
Para evitar dependencia total de formatos binarios (.db), se implementó un **Protocolo de Exportación Plana**:
*   Carpeta: `c:\dev\Sonido_Liquido_V5\SEMILLAS_MAESTRAS`
*   Contenido: Archivos CSV con la totalidad de los datos maestros (Clientes, Productos, Transportes, etc.).
*   Función: Sirven para reconstruir el sistema desde cero en cualquier máquina.

### C. El "Cargador Táctico" (Excel Killer)
En lugar de "vitaminizar" un Excel externo, acordamos construir el **"Modulo de Carga Rápida"** dentro de V5.
*   **Concepto:** Una grilla estilo hoja de cálculo.
*   **Filosofía:** 100% Teclado, sin mouse.
*   **Ventaja:** Validación de precios y stock en tiempo real contra la base de datos real.
*   **Diseño:** Especificaciones aprobadas y listas para desarrollo (Fase 1).
