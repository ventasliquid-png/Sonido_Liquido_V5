# 💰 PLAN DE ACCIÓN: GESTIÓN DE LISTAS DE PRECIOS

**Fecha:** 03 de Febrero 2026
**Estado:** PROPUESTA
**Contexto:** Transición de gestión Excel a Sistema Integrado V5.

---

## 1. ESTRUCTURA ORGANIZATIVA (YA IMPLEMENTADA)

Se ha reorganizado la carpeta raíz `LISTAS_PRECIO` siguiendo la lógica de "Fuente" vs "Salida":

```text
LISTAS_PRECIO/
├── Proveedores/          <-- INPUT (Lo que recibimos)
│   └── Celtrap/
│       ├── Celtrap (2).xlsx               (Histórico Fuente)
│       ├── CELTRAP - Febrero 2026.pdf     (Novedad / Update)
│       └── comparativa_precios_celtrap.csv (Procesado IA - LISTO PARA IMPACTAR)
│
└── Listas_LS/            <-- OUTPUT (Lo que genera Sonido Líquido)
    └── (Aquí guardaremos los Excel/PDF que V5 genere para nuestros clientes)
```

---

## 2. FLUJO DE TRABAJO PROPUESTO (PIPELINE)

El objetivo es dejar de "copiar y pegar" en Excels y pasar a una **Ingesta Inteligente**.

### PASO 1: Recepción y Digitalización
1.  Llega el archivo del proveedor (PDF/Excel) -> Se guarda en `Proveedores/{Nombre}/`.
2.  **Análisis IA (Como hiciste con Gemini):** Se genera un archivo intermedio estandarizado (CSV) que contiene:
    *   `Codigo` (SKU Proveedor)
    *   `Costo Nuevo`
    *   `Moneda`
    *   `Variación` (Audit Log)

### PASO 2: Laboratorio de Precios (Fase Estanca V2)
**Objetivo:** Generar Excel con **Agrupación Visual** (Headers) y **Versionado Seguro**.

*   **Herramienta:** `scripts/create_celtrap_v3.py`
*   **Estrategia:** "Template Injection"
    1.  **Leer Estructura 2025-05:** Iterar fila por fila.
    2.  **Detectar:** ¿Es Título (JABONES)? -> Copiar formato. ¿Es Producto? -> Buscar Precio en CSV.
    3.  **Regla 301:** Aplicar +10% al Camillero.
    4.  **Residuo:** Los productos del CSV que no estaban en 2025-05 se agregan al final bajo "NUEVOS".
*   **Salida:** Nuevo archivo `Celtrap (3).xlsx` (Evita bloqueos).

### PASO 3: Generación de Listas LS (Salida)
Una vez impactados los costos:
1.  V5 genera un PDF/Excel limpio con NUESTROS precios calculados.
2.  Se guarda en `Listas_LS/2026-02_Lista_General.pdf`.
3.  **Aislamiento:** Esta carpeta actúa como un "Sistema Estanco". Los archivos aquí son la verdad de precios para imprimir/enviar, desacoplados momentaryamente de la base de datos transaccional.

---

## 3. DEFINICIÓN DE SISTEMA ESTANCO

> **PRINCIPIO DE SEGURIDAD:**
> El módulo `LISTAS_PRECIO` funciona como una "Esclusa de Aire".
> 1.  **Entrada:** Listas Proveedor (Sucias/Crudas).
> 2.  **Proceso:** Scripts de Análisis y Simulación (Reglas de Negocio).
> 3.  **Salida:** Listas de Precios LS (Limpias/Oficiales).
>
> **La Base de Datos Operativa (`pilot.db`) NO se toca automáticamente.** Se usa solo para consultar costos históricos. La actualización de precios en el sistema de ventas requerirá una confirmación manual explícita (Botón "Impactar").
