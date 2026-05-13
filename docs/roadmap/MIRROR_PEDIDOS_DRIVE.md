# Mirror Pedidos MT → Google Drive

## Objetivo
Tener los pedidos de MT accesibles desde cualquier dispositivo vía Google Drive,
sin depender de conexión a MT.

## Contexto
- MT corre V5_LS_MASTER.db localmente (soberana, sin acceso remoto aún)
- Drive de empresa: ventasliquid@gmail.com, montado como Q: en MC
- El sheet viejo (Pedidos Liquid en Drive) queda como histórico intocable
- Archivo nuevo: Q:\Produccion_MT\Pedidos_V5_MT.xlsx

## Casos de uso
- "¿Qué precio le vendí la última vez a Signum Sepif?"
- "¿Qué compró Instituto de Terapia Radiante?"
- "Hay un pago de $X ¿de qué pedido es?"

## Arquitectura decidida
- Script: sync_pedidos_sheet.py en MT
- Lee: pedidos + pedidos_items + clientes de V5_LS_MASTER.db
- Genera: Pedidos_V5_MT.xlsx (formato similar al sheet histórico)
- Destino: Q:\Produccion_MT\ (Google Drive Desktop montado en MT)
- Sin Sheets API — escritura directa al disco Q: que Drive sincroniza

## Columnas del xlsx
Pedido N° | Fecha | Cliente | CUIT | Producto | Cantidad | 
Precio Unit | Subtotal | IVA | Total | OC | Estado

## Triggers
1. Botón en UI de MT: POST /sync/drive
2. Automático al ejecutar OMEGA de MT

## Pasos pendientes para implementar
1. Instalar Google Drive Desktop en MT y loguear con ventasliquid@gmail.com
2. Verificar que Q: queda montado en MT
3. Crear carpeta Q:\Produccion_MT\
4. Desarrollar sync_pedidos_sheet.py (usar openpyxl)
5. Crear endpoint POST /sync/drive en backend
6. Agregar botón en UI (sugerido: panel de herramientas o navbar)
7. Integrar llamada en OMEGA de MT
8. Testear flujo completo

## Dependencias
- openpyxl (pip install openpyxl en venv de MT)
- Google Drive Desktop instalado en MT
- Q: montado y accesible

## Referencias de sesión
- Analizado en sesión 806 con Carlos
- Sheet histórico: docs.google.com/spreadsheets/d/105Clswh91ad7eTVMGmB_KRTvuuGlEoaxDtZzwMhMl6o
- Carpeta Drive V5_Silo_Claude: Q:\Mi unidad\V5_Silo_Claude
