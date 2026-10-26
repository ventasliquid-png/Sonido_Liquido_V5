r"""S887, pedido de Carlos (15/10): el pedido es el punto de partida; ahí tiene que verse si ya tiene remito y cuál es (ficha, Tablero de Pedidos, pantalla de entregas; el Remito Manual se retiró en la S893), poder reimprimirlo sin hacer otro,
y el botón «Imprimir remito» solo aparece si queda algo por remitar. Prueba estática del código de las pantallas (el comportamiento se verificó en el navegador sobre una copia de P)."""
import sys, os, re, io
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5\scripts"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
comp = leer("frontend/src/composables/useRemitosDelPedido.js")
canvas = leer("frontend/src/views/Ventas/PedidoCanvas.vue")
lista = leer("frontend/src/views/Pedidos/PedidoList.vue")
split = leer("frontend/src/views/Logistica/LogisticaSplitter.vue")
def plantilla(s): return re.sub(r"<!--[\s\S]*?-->", "", s[s.index("<template>"):s.index("</template>")]) if "</template>" in s else ""

# ---- composable compartido
check("el composable trae los remitos del pedido por GET /remitos/por_pedido/<id> y descarta los anulados", "api.get(`/remitos/por_pedido/${pedidoId}`)" in comp and "r.estado !== 'ANULADO'" in comp)
check("reimprimir abre el PDF del mismo remito (no crea nada) y, si no tiene número, pide confirmación antes de gastar uno",
      "window.open(`/remitos/${remito.id}/pdf`, '_blank')" in comp and "if (sinNumero && !confirm(" in comp and "próximo número del talonario 0015" in comp)

# ---- ficha del pedido
check("la ficha carga los remitos del pedido al abrirlo y al cambiar de pedido", "traerRemitosDelPedido(id)" in canvas and re.search(r"watch\(\(\) => route\.params\.id, \(id\) => \{ remitosCargados\.value = false;[^}]*cargarRemitosDelPedido\(id\);[^}]*\}, \{ immediate: true \}\)", canvas))
check("con remito, la franja de la ficha dice «Remito de este pedido», el número, el estado y trae «Reimprimir»",
      'data-estado-remito="con-remito"' in canvas and "Remito de este pedido" in canvas and "claseEstadoRemito(r.estado)" in canvas and "Reimprimir" in canvas and "@click=\"reimprimirRemito(r)\"" in canvas)
check("dice si el pedido quedó «remitido completo» o cuántos renglones quedan por remitar", "Pedido remitido completo" in canvas and "Queda pendiente de remitar:" in canvas and "renglonesPendientes.length === 0" in canvas)
check("sin remito, la franja dice «Este pedido todavía no tiene remito» (solo si el pedido no está cerrado)", 'data-estado-remito="sin-remito"' in canvas and "Este pedido todavía no tiene remito." in canvas and "remitosCargados && !isClosedOrder" in canvas)
m = re.search(r'<button v-if="([^"]+)" @click="\$router\.push\(\{ name: \'PedidoLogistica\', params: \{ id: route\.params\.id \}, query: \{ armar: 1 \} \}\)"', canvas)
check("«Imprimir remito» solo aparece si queda algo por remitar (y el pedido está guardado y no cerrado)", m and "renglonesPendientes.length > 0" in m.group(1) and "!isClosedOrder" in m.group(1) and "route.params.id" in m.group(1))
check("«Entregas y remitos» sigue siempre (para ver y reimprimir)", re.search(r"<button v-if=\"route\.params\.id\" @click=\"\$router\.push\(\{ name: 'PedidoLogistica', params: \{ id: route\.params\.id \} \}\)\"[^>]*>\s*<i[^>]*></i> Entregas y remitos", canvas))
check("el reimprimir de la ficha refresca los remitos si el PDF numeró uno", "imprimirRemitoExistente(r, () => cargarRemitosDelPedido(route.params.id))" in canvas)

# ---- Tablero de Pedidos
check("el Tablero pide UNA vez el resumen de remitos por pedido (GET /remitos/resumen_por_pedido) cada vez que se refresca", "api.get('/remitos/resumen_por_pedido')" in lista and re.search(r"await store\.fetchPedidos\(params\)\s*await cargarRemitos\(\)", lista))
check("cada fila muestra el número del remito (con «+N» si hay más) debajo del estado, y «sin remito» solo en pedidos PENDIENTES", "remitosDe(pedido)[0].numero_legal || 'sin numerar'" in lista and "pedido.estado === 'PENDIENTE'" in lista and "sin remito</span>" in lista)
check("el número del remito del tablero lleva a las entregas del pedido sin seleccionar la fila (@click.stop)", '@click.stop="verRemitos(pedido)"' in lista and "name: 'PedidoLogistica', params: { id: pedido.id }" in lista)
check("el Tablero no suma una columna (a 1440 px con el inspector abierto le sacaba todo el lugar al nombre del cliente): el encabezado dice «Estado · Remito»", "Estado · Remito" in lista and 'w-36">Remito' not in lista)

# ---- pantalla de entregas y Remito Manual
check("la pantalla de entregas dice «Este pedido ya está remitido completo» cuando no queda nada por remitar y hay remitos vigentes",
      'data-estado-remito="completo"' in split and "itemsPendientes.length === 0 && remitos.some(r => r.estado !== 'ANULADO')" in split and "Este pedido ya está remitido completo" in split)
check("el botón «Imprimir remito» apagado explica por qué", ":title=\"itemsPendientes.length === 0 ? 'No queda nada por remitar: el pedido ya está remitido completo'" in split)
# [S893] El Remito Manual se retiró: el aviso de «este pedido ya tiene remito» vive en la ficha del pedido, el Tablero y la pantalla de entregas (el armado desde el pedido).

# ---- sin «PR» a la vista en lo nuevo
nuevo = " ".join(re.findall(r"(?:Remito de este pedido|Este pedido[^<{]*|Reimprimir|Queda pendiente[^<]*)", plantilla(canvas) + plantilla(split)))
check("los textos nuevos hablan de «remito» (ninguno dice «PR»)", not re.search(r"\bPR\b", nuevo) and not re.search(r"\bPR\b", comp))

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
