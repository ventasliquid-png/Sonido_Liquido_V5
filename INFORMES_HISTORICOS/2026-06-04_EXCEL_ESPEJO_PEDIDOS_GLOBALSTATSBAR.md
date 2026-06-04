# INFORME SESIÓN 822 — Excel Espejo de Pedidos + GlobalStatsBar UI
**Fecha:** 2026-06-04 | **Entorno:** OF | **Estado cierre:** NOMINAL GOLD
**Hash D:** 135a16f8 (sin push — pendiente PIN 1974)
**Agente:** Claude Code (Sonnet 4.6)

---

## Resumen ejecutivo

Sesión de desarrollo completo del **Espejo Excel de Pedidos**: script Python con
formato bloque (emula el Google Sheets histórico), endpoint FastAPI, botones en
GlobalStatsBar y lógica fiscal correcta via Motor Bipolar.

---

## 1. Script `scripts/exportar_pedidos_excel.py`

**Formato:** Un bloque por pedido, apilados verticalmente.

```
[Pedido Nº | nro RED | Cliente PURPURA]  [OC si existe]
[Fecha     | CUIT    | valor           ]
[PRODUCTO  | CANTIDAD | PRECIO VENTA | SUBTOTAL | | COSTO UNIT | COSTO TOTAL]
 item 1...
 item 2...
[NOTAS | texto mergeado B→H (italic si tiene contenido)]
[      |          | Sub Total | $xxx | | $costo]
[      |          | IVA       | $xxx | | $costo]  ← solo si discrimina IVA
[      |          | TOTAL     | $xxx | | $costo]
(separador)
```

**Características:**
- Colores STATE_MASK: 🟢 Verde (bit33/Firme) | 🟡 Amarillo (bit34/Cumplido) | 🔴 Rojo (bit35/Anulado) | 🟣 Lila (bit32/Presupuesto)
- IVA Motor Bipolar: bit 12 NO_FISCAL_FORCE soberano; fallback condicion_iva_id = RI
- Costos opcionales: productos_costos.costo_reposicion (16/65 ítems cubiertos)
- Nombre fijo: `PEDIDOS_ESPEJO.xlsx` | Fallback con timestamp si está bloqueado
- Destino: `Q:\Mi unidad\V5_Silo_Claude\`

**Iteraciones del día:**
1. V1 tabla plana (descartada)
2. V2 formato bloque
3. Fix IVA Motor Bipolar (LUISA/Rosa: CF informal sin IVA)
4. Colores STATE_MASK
5. CUIT eliminado del footer
6. Fila NOTAS

---

## 2. Backend `GET /pedidos/exportar-espejo`

Archivo: `backend/pedidos/router.py`

- Ejecuta el script via `subprocess.run()` desde project root
- Timeout: 60 seg
- **Bug corregido:** 422 Unprocessable Entity — el endpoint estaba al FINAL del
  router, después de `@router.get("/{pedido_id}", ...)` que lo capturaba como
  ID entero. Movido ANTES de la ruta paramétrica.
- Respuesta: `{"ok": true, "mensaje": "...", "output": "..."}`

---

## 3. Frontend `PedidoList.vue`

**Técnica:** `<Teleport to="#global-header-center">` — usa el portal
ya definido en GlobalStatsBar.vue para inyectar botones contextuales.

- Botón verde **"+ Nuevo"** → `router.push({ name: 'PedidoCanvas' })` | F4 se mantiene
- Botón naranja **"📊 Exportar Excel"** → `GET /pedidos/exportar-espejo` | spinner + toast
- **Eliminado:** "Safety Net Export" (icono Excel verde, tabla plana pandas sin formato)
- Header interno limpiado: solo búsqueda + filtros + refresh

---

## 4. Motor Bipolar — Lógica IVA

Doctrina encontrada en `backend/pedidos/router.py` (`_aplica_iva()`):

```python
# Circuito Negro — soberano, nunca discrimina IVA
if pedido.flags_estado & NO_FISCAL_FORCE:   # bit 12 = 4096
    return False
# Circuito Blanco — solo RI discrimina IVA
return bool(cliente.flags_estado & DISCRIMINA_IVA)  # bit 40
```

**Estado bit 40 en DB:** solo 2 clientes migrados (BULACIO, JOFRE).
**Proxy usado:** `condicion_iva_id = RI_UUID` ('966fdb33...') — confiable y poblado.

Resultado: 27 pedidos discriminan IVA | 6 no (CF/informal) | 2 Circuito Negro intencional.

---

## 5. Board V5 actualizado

| Card | Cambio |
|---|---|
| #26 Excel Espejo | BACKLOG → **EN PROGRESO** + nota sesión 822 |
| #40 Motor prompts | Completada: "Seleccion de motor en prompts" (MEDIA, Sistema) |
| #46 Bugs Tomy | **NUEVA** — ALTA, Ingesta/Pedidos, 4 bugs detectados en P/MT |

---

## 6. Pendientes identificados

### Excel Espejo (Card #26)
1. Identificador de entorno en nombre: `PEDIDOS_ESPEJO_TOM.xlsx` / `_DEV` / `_MC`
2. Parámetro `--entorno` en el script
3. Título interno del Excel en hoja `_info`
4. Integrar con OMEGA de Tomy (generación automática al cierre de sesión P)

### Bugs Tomy P/MT (Card #46 — ALTA)
1. Ingesta no crea pedido nuevo sin vínculo previo (cambio post-818)
2. Pedido manual exige NUMERO_COMPROBANTE — no debería
3. Guard duplicados avisa pero no bloquea
4. Canvas pedido muestra subtotal sin IVA en total final

---

## Canario cierre
```
INTEGRITY: NOMINAL GOLD | FLAGS: 13 | Tiempo: 0.052s
WAL checkpoint: OK
Rama: main
```

*Informe archivado: OF — Sesión 822*
