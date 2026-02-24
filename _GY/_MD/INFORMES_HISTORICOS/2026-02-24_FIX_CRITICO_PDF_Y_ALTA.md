# INFORME DE SESIÓN - 2026-02-24: "FIX CRÍTICO DE ALTA Y DESCARGA RUTINARIA PDF"

## RESUMEN EJECUTIVO
La sesión se enfocó en asegurar que el flujo de alta del Usuario no destruyera datos ingresados y en la estabilización absoluta del motor PDF del Backend, el cual estaba arrojando errores silenciosos que abortaban la emisión física del remito.

## 1. INCIDENTE DE DATOS EN ALTA DE CLIENTES (FRONTEND)
**Problema Detectado:**
Durante el alta de clientes (Estado 14 o 15), la plataforma Vue purgaba accidentalmente campos rellenados por el usuario (como Segmento y Lista de Precio) tras confirmar un Domicilio Fiscal. Esto se debía a un recargo integral (`fetchClienteById`) tras guardar el submódulo de Domicilios que pisaba la memoria en `ClientCanvas.vue`.

**Intervención Aplicada:**
- Cambiado comportamiento de `handleDomicilioSaved`. Ahora rescata el cliente de la BD, pero solo anexa/reemplaza la rama `.domicilios` en vez del objeto primario `form.value`.
- Implementado auto-fill de variables paramétricas en el router al navegar a un `Cliente Incompleto` luego del escaneo PDF (prellenando calle e IVA si coinciden).

## 2. TIMEOUT RENDERING PDF (BACKEND)
**Problema Detectado:**
La ruta `/remitos/ingesta-process` completaba la lógica DB, empalmaba modelos de negocio, pero al final la propiedad `pdf_url` volvía en `null`.
El sistema de generación arrojaba Timeout de RAM al procesar la capa inferior del remitente: `base_remito_v1.png` era excesivamente grande para Uvicorn y FPDF 1.7.2.

**Intervención Aplicada:**
- Migración de la placa base a un formato comprimido `base_remito_v1.jpg` (112 kb).
- Ajuste del backend API Uvicorn (`service.py`), reemplazando referencias estáticas absolutas de Python por rutas relativas dentro de la arquitectura de la app V5.
- Confirmación Exitosa: `REMITO_R-00XXXXXX.pdf` se crea en disco e impacta su UUID/URL en el router de cara a la descarga frontend en un tiempo menor a 800ms.

## MÉTRICAS DE IMPACTO
- **Flujo de Alta Continuo**: Reactivado.
- **Motor Generador Remito**: 100% (JPG Base + FPDF).

## ESTADO DE REPOSITORIO
- Listo para Push. El entorno Piloto (`pilot.db`) mantiene consistencia total.

## PRÓXIMOS PASOS (VANGUARD)
- Finalizar esquema Contable y trasladar despliegue de RAR Punto de Venta hacia Entorno IOWA de forma oficial.
