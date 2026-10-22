r"""S887, pedido de Carlos (15/10, pedido 128): (1) la ficha del pedido tiene un botón «Hacer remito» que lleva a las entregas con el cuadro «Armar PR» abierto;
(2) el listado de Remitos tiene una columna «Pedido» (ordenable, se busca por Nº de pedido) y un ícono de impresora por fila.
Prueba estática sobre el código de las pantallas (no hay corredor de componentes): confirma que las piezas existen y están cableadas entre sí."""
import sys, os, re, io
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5\scripts"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
canvas = leer("frontend/src/views/Ventas/PedidoCanvas.vue")
split = leer("frontend/src/views/Logistica/LogisticaSplitter.vue")
lista = leer("frontend/src/views/Logistica/RemitoListView.vue")

# ---- ficha del pedido
m = re.search(r'<button v-if="([^"]+)" @click="\$router\.push\(\{ name: \'PedidoLogistica\', params: \{ id: route\.params\.id \}, query: \{ armar: 1 \} \}\)"[^>]*>\s*<i[^>]*></i> Imprimir remito\s*</button>', canvas)
check("la ficha del pedido tiene el botón «Imprimir remito» que va a PedidoLogistica con ?armar=1", m)
check("«Imprimir remito» solo aparece con el pedido ya guardado y no cerrado (ni CUMPLIDO ni ANULADO)", m and "route.params.id" in m.group(1) and "!isClosedOrder" in m.group(1))
check("el botón de las entregas sigue (ahora «Entregas y remitos») y va sin ?armar", re.search(r"PedidoLogistica', params: \{ id: route\.params\.id \} \}\)\"[^>]*>\s*<i[^>]*></i> Entregas y remitos", canvas))
check("ya no se llama «Entregas (Split)»", "Entregas (Split)" not in canvas)
check("existe la ruta PedidoLogistica (pedidos/:id/logistica)", "name: 'PedidoLogistica'" in leer("frontend/src/router/index.js"))

# ---- pantalla de entregas: el cuadro «Armar PR» sale abierto con ?armar=1, y solo si hay algo pendiente
check("las entregas abren el cuadro «Imprimir remito» solo con ?armar=1 después de cargar los datos y si hay renglones pendientes",
      re.search(r"await loadData\(id\);\s*//[^\n]*\n\s*if \(route\.query\.armar && itemsPendientes\.value\.length > 0\) openArmarModal\(\);", split))

# ---- el cuadro: por defecto el remito es el pedido completo (el parcial es la excepción) y se imprime con un clic
check("el cuadro arma el remito con TODO el pedido tildado y las cantidades completas por defecto",
      # [S890] entre la cantidad y el motivo ahora va el neto por unidad del renglón (base del valor declarado sugerido)
      re.search(r"cantidad: item\.cantidad_pendiente,(?:\s*//[^\n]*)?(?:\s*neto_unitario:[^\n]*)?\s*motivo: '',\s*marcado: true,", split) and "marcado: false," not in split[split.index("const openArmarModal"):split.index("const cancelArmar")])
check("el cuadro dice «Esto voy a imprimir: el pedido completo» y que se puede modificar", "Esto voy a imprimir: el pedido completo." in split and "Podés modificarlo" in split and "Imprimir remito</h3>" in split)
check("el botón principal del cuadro es «Imprimir remito» (arma e imprime) y queda «Solo armar» como secundario",
      "@click=\"confirmArmar(true)\"" in split and "@click=\"confirmArmar(false)\"" in split and "Solo armar" in split and re.search(r"Imprimir remito\s*</button>", split))
check("ningún botón llama a confirmArmar sin argumento (el evento del clic contaría como «imprimir»)", 'confirmArmar"' not in split and "@click=\"confirmArmar\"" not in split)
check("armar e imprimir abre /remitos/<id>/pdf (el servidor numera) y si el navegador bloquea la ventana descarga el PDF",
      "window.open(`/remitos/${remito.id}/pdf`, '_blank')" in split and "if (!ventana) downloadLegalPDF(remito);" in split and "if (imprimir && nuevo?.id) imprimirArmado(nuevo);" in split)
check("después de imprimir recarga el pedido otra vez para mostrar el número asignado", "if (imprimir && nuevo?.id) setTimeout(() => loadData(localPedido.value.id), 1500);" in split)
check("el parcial sigue exigiendo la confirmación escrita (no domina la carga normal pero no se pierde la salvaguarda)", "Escribí ${sel.cantidad_pendiente} para confirmar" in split)
check("sin método de entrega no se puede imprimir y el cuadro lo avisa", '<p v-if="!armarMetodo"' in split and "|| !armarMetodo" in split)
check("el botón de la pantalla de entregas pasó de «Armar PR» a «Imprimir remito»", "<i class=\"fas fa-print\"></i> Imprimir remito" in split and "</i> Armar PR" not in split)

# ---- «PR» es de la arquitectura (el distribuidor interno de posiciones del pedido): el operador no lo ve en la pantalla de entregas ni en la ficha
plantilla = re.sub(r"<!--[\s\S]*?-->", "", split[split.index("<template>"):split.index("</template>")])
avisos = re.findall(r"(?:alert|prompt|confirm)\((?:[^()]|\([^()]*\))*\)", split)
check("la pantalla de entregas no muestra «PR» al operador (ni en pantalla ni en los avisos y confirmaciones)", not re.search(r"PR", plantilla) and not [a for a in avisos if re.search(r"PR", a)])
check("el aviso del parcial habla de «remito parcial»", "hacés un remito parcial." in split)
check("la ficha del pedido y el listado de remitos tampoco dicen «PR» en pantalla", not re.search(r"PR", re.sub(r"<!--[\s\S]*?-->", "", canvas[canvas.index("<template>"):canvas.index("</template>")])) and not re.search(r"PR", re.sub(r"<!--[\s\S]*?-->", "", lista[lista.index("<template>"):lista.index("</template>")])))

# ---- listado de remitos
cab = lista[lista.index("<!-- Header Row -->"):lista.index("v-for=\"remito in sortedRemitos\"")]
orden = [cab.index(f"toggleSort('{k}')") for k in ("numero", "pedido", "fecha", "cliente")]
check("la cabecera tiene la columna «Pedido» ordenable, entre Número y Fecha", orden == sorted(orden) and ">\n                    Pedido\n" in cab)
fila = lista[lista.index("v-for=\"remito in sortedRemitos\""):lista.index("<!-- Empty State -->")]
# [S890] la columna Fecha muestra la fecha del remito (fechaRemito: la de cuando tomó número), ya no fecha_creacion
pos = [fila.index(s) for s in ("remito.numero_legal || 'BORRADOR'", "#{{ remito.pedido_id }}", "formatDate(fechaRemito(remito))", "remito.razon_social || 'Desconocido'")]
check("cada fila muestra el Nº de pedido en su columna, en el mismo orden que la cabecera (Número, Pedido, Fecha, Cliente)", pos == sorted(pos))
check("el Nº de pedido ya no va como subtítulo bajo el cliente", "Pedido #{{ remito.pedido_id }}" not in fila)
check("cada fila tiene un ícono de impresora que no abre el editor (@click.stop) y se apaga en los ANULADOS",
      re.search(r'@click\.stop="imprimirRemito\(remito\)"\s*:disabled="remito\.estado === \'ANULADO\'"[\s\S]{0,900}fa-print', fila))
anch = lambda s: re.findall(r'^ {16}<div class="(w-\d+)[ "]', s, re.M)
check(f"las anchuras de las columnas de la cabecera y de las filas coinciden {anch(cab)}", anch(cab) == anch(fila) and len(anch(cab)) == 7)
check("imprimir un remito sin número pide confirmación (el PDF lo numera con el próximo 0015) y refresca el listado después (S891: también un numerado sin IMPRESO)",
      "if (sinNumero && !confirm(" in lista and "if (!impreso(remito)) setTimeout(refresh, 1500);" in lista and "próximo número del talonario 0015" in lista)
check("el PDF que se abre es el mismo que usa el editor: /remitos/<id>/pdf", "const pdfUrl = `/remitos/${remito.id}/pdf`;" in lista and "printRemito(remito);" in lista)
check("el buscador también encuentra por Nº de pedido (exacto, con o sin #) y el orden por Pedido es numérico",
      "String(r.pedido_id ?? '') === query.replace(/^#/, '').trim()" in lista and "Number(a.pedido_id) || 0" in lista and "Buscar por número, pedido o cliente..." in lista)
check("el botón «Ver pedido» se mantiene", 'title="Ver Pedido"' in lista)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
