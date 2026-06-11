# Informe de Incidencia: Z-Index y Dropdown Cortado en Cantera

## 1. ¿Qué pasó exactamente? (El Problema Core)
Teníamos un error visual crítico en la vista de Ventas (`PedidoCanvas.vue`) donde la lista desplegable de resultados del buscador "Cantera" se cortaba abruptamente al llegar a la línea del *footer*, ocultando productos.

Aunque parecía un problema de "capas" o profundidad (`z-index`), en realidad era un problema de **recorte estructural (`overflow`)**:
- La tabla de productos estaba envuelta en un contenedor con la clase de Tailwind `overflow-hidden`.
- Esta propiedad actúa como una "tijera invisible": sin importar si el desplegable tenía `z-[9999]`, al estar dentro de esa caja, cualquier píxel que superara el límite de la caja era eliminado visualmente por el navegador.

La ilusión de que "ayer andaba bien en D" ocurrió porque ayer, al hacer la prueba, la búsqueda devolvió un solo producto. Ese único producto ocupaba poco espacio vertical y entraba perfectamente dentro de la caja sin llegar al límite de la tijera. Hoy, al buscar "barbijo", devolvió 3 productos, tocó el piso de la caja y se cortó.

## 2. ¿Cómo lo resolvimos?
El arreglo requirió una "cirugía" en dos frentes:

1. **Estructura HTML (El Fix Real):** 
   - Fuimos a `PedidoCanvas.vue` y reemplazamos los contenedores padre (`<main>` y el fondo oscuro de la tabla) cambiando `overflow-hidden` por `overflow-visible`.
   - Además, separamos la fila del buscador rápido para que no comparta el mismo contenedor de scroll (`overflow-y-auto`) que los productos ya agregados al pedido.

2. **Sincronización de Entornos (El Problema Fantasma):**
   - **Entorno D (`localhost:5173`):** Usa Vite, que recompila e inyecta los cambios en el navegador en milisegundos (Hot Module Replacement). Por eso el fix se vio inmediatamente.
   - **Entorno P (`localhost:8090`):** Usa el backend de Python (FastAPI) para servir los archivos pre-compilados. El problema fue que hicimos el proceso de `npm run build` (que crea la carpeta `dist`), pero faltó ejecutar `deploy.bat`, el cual es el encargado de copiar esa carpeta `dist` al directorio `static/` que lee Python. Al ejecutar el `.bat`, el código final finalmente se inyectó en P.

---

## 3. Sugerencias para evitar el `deploy.bat` manual constantemente

Tener que acordarse de ejecutar un script manual para ver cambios en P genera fricción y este tipo de confusiones ("el código está bien pero veo la versión vieja"). 

Aquí te presento tres estrategias arquitectónicas para resolver esto, de la más sencilla a la más profesional:

### Opción A: Separación Estricta de Roles (La más sencilla)
Adoptar la doctrina de que **todo el desarrollo visual y pruebas se hacen exclusivamente en D (`localhost:5173`)**. 
El entorno P (`localhost:8090`) solo debe abrirse al final de la jornada o del sprint para hacer un "QA general" simulando lo que vería el cliente final. Si asumimos esto, ejecutar `deploy.bat` solo una vez al día deja de ser una molestia.

### Opción B: Proxy Inverso Integrado (Recomendada para Desarrollo Fluido)
Podemos modificar la arquitectura local para no depender de la compilación estática durante el desarrollo. 
Actualmente, el Backend sirve el Frontend. Podemos invertir esto en desarrollo:
Configuramos FastAPI para que **no sirva archivos estáticos en modo desarrollo**, y hacemos que un proxy o el mismo Vite redirija automáticamente las peticiones de API hacia Python, mientras Vite maneja la interfaz. 
*Nota: Ya tenés algo similar configurado en `vite.config.js`, por lo que usar `localhost:5173` como entorno principal de uso diario es el camino más natural.*

### Opción C: Auto-Deploy en Background (Vite Watch)
Podemos crear un script de NPM que observe los cambios (`--watch`) y automáticamente copie los archivos al backend cada vez que guardás un archivo.
* **Pro:** Vas a ver los cambios en el puerto `8090` casi al instante.
* **Contra:** El proceso de `build` de Vue puede tardar entre 5 y 10 segundos. Si hace esto cada vez que guardás un archivo, la computadora (especialmente la de Tomy) va a estar con los ventiladores al máximo y el disco trabajando constantemente, degradando la performance general.

### 💡 Mi recomendación táctica:
Apegarnos a la **Opción A**, apoyada por la configuración que ya tenemos en Vite. 
El flujo ideal de tu equipo debería ser:
1. **Carlos / Gy:** Programan y prueban en `localhost:5173` (Vite, instantáneo).
2. **Fin del día / Feature:** Al terminar, ejecutan `deploy.bat` y hacen push.
3. **Producción / Tomy:** Arranca directamente con el `ARRANCAR_TOMY.bat` (`8090`) y consume el código estático ultrarrápido y ya compilado. 

No tiene sentido intentar que el puerto 8090 sea reactivo a cambios de código fuente, porque ese puerto está diseñado precisamente para simular un servidor en producción, donde los archivos son inmutables.
