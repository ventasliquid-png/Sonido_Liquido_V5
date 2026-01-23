# ANTI-PATRÓN: MANIPULACIÓN DE SYS.PATH E IMPORTS

**Fecha del Incidente:** Jueves 22/01/2026 (aprox)
**Gravedad:** CRÍTICA (Structural Instability)

## ⛔ LA REGLA DE ORO
**NUNCA** modificar `sys.path` o `PYTHONPATH` dinámicamente dentro del código (`main.py`, `__init__.py`) para "arreglar" un `ModuleNotFoundError` o simplificar imports.

## 💀 El Anti-Patrón (Lo que NO debes hacer)
```python
# NO HAGAS ESTO EN MAIN.PY
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__))) # ☠️
```

## 💥 Por qué es Peligroso
1.  **Duplicidad de Módulos:** Python puede cargar el mismo módulo dos veces (ej: `core.config` y `backend.core.config`) como si fueran distintos.
    *   *Consecuencia:* Variables globales duplicadas, Singletons rotos, conexiones a DB inconsistentes.
2.  **Race Conditions:** El orden de carga se vuelve impredecible.
3.  **IDE Confusion:** Los linters y el auto-completado del IDE dejan de entender la estructura del proyecto.
4.  **"Frankenstein":** Obliga a mezclar imports relativos (`from . import x`) y absolutos (`from backend.x import y`) de forma caótica.

## ✅ La Forma Correcta (Protocolo V11)
El proyecto `Sonido_Liquido_V5` es un paquete Python estándar.
1.  **Ejecución:** Siempre ejecutar desde la raíz del proyecto.
    *   `uvicorn backend.main:app` (Correcto)
    *   `cd backend && python main.py` (Incorrecto sin configuración previa)
2.  **Imports:** Usar siempre imports absolutos desde la raíz.
    *   `from backend.core.database import get_db`
3.  **Configuración:** Si faltan módulos, configurar `PYTHONPATH` en el entorno, NO en el código.

**Lección:** Un bug lógico ("Alta de Cliente") se arregla con lógica. Si tocamos la estructura de imports para arreglar lógica, estamos rompiendo el sistema.
