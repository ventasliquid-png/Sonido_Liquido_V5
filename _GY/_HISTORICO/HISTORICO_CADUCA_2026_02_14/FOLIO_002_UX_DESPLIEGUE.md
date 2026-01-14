# FOLIO 2: Experiencia de Usuario y Despliegue en Entornos Reales

**Contexto:** Prueba de Campo (UAT) - Release V1.1
**Operador:** Tomás (Usuario Final)
**Observador:** Carlos

## 1. Análisis de Fricción Técnica (El infierno de las dependencias)

La sesión de instalación reveló una fragilidad estructural en el método de despliegue actual basado en scripts y entornos volátiles.

*   **Ausencia de Librerías Críticas:** El arranque falló reiteradamente debido a dependencias faltantes (`python-multipart`, `email-validator`) que no estaban declaradas o instaladas por defecto en el entorno base del usuario. Esto obligó a intervenciones manuales (`pip install`) que rompen la experiencia de "producto terminado".
*   **Fragilidad de Rutas:** La ejecución devolvió errores de importación (`Could not import module "main"` vs `backend.main`) al intentar correr Uvicorn desde directorios distintos a la raíz. Esto demuestra que la arquitectura actual no es resiliente a donde el usuario decida ubicar la carpeta del sistema.
*   **Ansiedad por Consola:** El despliegue de logs en "letras rojas" (advertencias de librerías, delays de conexión a DB) generó una respuesta de ansiedad inmediata en el operador, quien interpretó mensajes inofensivos de diagnóstico como fallos catastróficos, deteniendo su flujo de trabajo para pedir asistencia innecesaria.

## 2. La Brecha Cognitiva (Frontend vs. Backend)

Se evidenció una barrera conceptual insalvable para el operador promedio:

*   **El "Misterio" de la Ventana Negra:** El usuario no comprende por qué debe mantener abierta una terminal ("ventana negra") para que la "pantalla visual" (el navegador) funcione.
*   **Modelo Mental Monolítico:** El usuario espera una aplicación autocontenida. El concepto de arquitectura cliente-servidor desacoplada es transparente para él; si cierra la ventana "que no hace nada" (el backend), se rompe la aplicación, generando frustración y desconfianza en la estabilidad del sistema.

## 3. Conclusión Estratégica y Solución

**Veredicto:** El método de despliegue actual (scripts `.bat`, gestión manual de pip, terminales visibles) es **INVIABLE** para una distribución masiva o profesional del producto.

**Requerimiento Prioritario: Empaquetado "One-Click" (.exe)**
Es imperativo desarrollar un instalador robusto y autocontenido que cumpla con:

1.  **Entorno Python Embebido:** El instalador debe contener su propio intérprete y todas las dependencias pre-instaladas. El usuario no debe necesitar instalar Python ni ejecutar `pip` nunca.
2.  **Ejecución Headless (Segundo Plano):** Los servicios de backend deben iniciarse como procesos de fondo o servicios de sistema, sin desplegar ventanas de terminal que inviten a ser cerradas por error.
3.  **Agnosticismo de Rutas:** El sistema debe ser capaz de autodetectar su directorio de ejecución y configurar sus rutas internas dinámicamente, sin importar dónde lo instale el usuario (Archivos de Programa, Escritorio, etc.).

**Meta:** Blindar el proceso de instalación para eliminar la dependencia de soporte técnico durante la puesta en marcha.
