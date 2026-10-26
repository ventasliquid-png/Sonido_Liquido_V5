r"""S893, Carlos 26/10: el nodo Remitos y su ficha (molde DEOU de Cliente y Producto). Prueba estática sobre el código de las pantallas (no hay corredor de componentes):
la ficha tiene ruta propia (/logistica/remitos/:ref) para que ESC y «volver atrás» la cierren; el listado la abre con un clic en la fila y con Enter en el buscador (número, OC, cliente);
los atajos F3/F4/F10/ESC tienen SIEMPRE su botón a la vista; Remitos sale de PEDIDOS y es un grupo propio, naranja (Logística); «Registrar devolución» se fundió con la corrección «Volvió» (se elige de qué remito volvió); «Ver el remito» reemplaza al dibujo HTML;
lo que pasó con la mercadería (no salió todo, se perdió, se rechazó, volvió) se CORRIGE por renglón con su causa y mueve el pedido: no es una nota suelta; la nota libre sigue aparte.
[Carlos 26/10] El Remito Manual se retiró: «Nuevo remito» (F4) elige un pedido y sigue por su armado."""
import sys, os, re, io
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5\scripts"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
ficha = leer("frontend/src/views/Logistica/RemitoFicha.vue")
lista = leer("frontend/src/views/Logistica/RemitoListView.vue")
rutas = leer("frontend/src/router/index.js")
barra = leer("frontend/src/components/layout/AppSidebar.vue")
split = leer("frontend/src/views/Logistica/LogisticaSplitter.vue")

# ---- la ruta: lista + ficha hija, con nombres estables
check("la ruta logistica/remitos es la lista con la ficha como hija (:ref); RemitoList y RemitoFicha tienen nombre",
      re.search(r"path: 'logistica/remitos',\s*component: \(\) => import\('\.\./views/Logistica/RemitoListView\.vue'\),(?:\s*meta:[^\n]*)?\s*children: \[[\s\S]*?name: 'RemitoList'[\s\S]*?path: ':ref', name: 'RemitoFicha', component: \(\) => import\('\.\./views/Logistica/RemitoFicha\.vue'\)", rutas))
check("la lista deja un lugar para la ficha (<router-view />)", "<router-view />" in lista)

# ---- el listado: clic en la fila abre la ficha; los botones de la fila no
check("un clic en la fila abre la ficha (antes era doble clic al editor)", '@click="abrirFicha(remito)"' in lista and '@dblclick="openEditModal(remito)"' not in lista)
check("«Ver pedido» de la fila no abre además la ficha (@click.stop)", re.search(r'@click\.stop="viewPedido\(remito\.pedido_id\)"\s*class="p-2 text-orange-500/50[^"]*"\s*title="Ver Pedido"', lista))
check("el listado es naranja como el resto del nodo (marco, buscador, números); el azul solo queda en el estado EN_CAMINO, que es su significado",
      "rounded-2xl border-2 border-orange-500" in lista and "neon-orange" in lista and ".neon-orange {" in lista and "case 'EN_CAMINO': return 'bg-blue-500/20" in lista
      and "blue" not in lista.replace("case 'EN_CAMINO': return 'bg-blue-500/20 text-blue-400 border-blue-500/50'", ""))
layout = leer("frontend/src/layouts/HaweLayout.vue")
check("la lista NO se vuelve a montar al abrir o cerrar la ficha (conserva filtro y posición): HaweLayout usa meta.claveVista y la ruta de Remitos la define",
      ':key="route.meta.claveVista || route.path"' in layout and "meta: { claveVista: 'remitos' }" in rutas)
check("en la dirección va el número cuando es el de siempre (4+8 dígitos); si no, el id",
      "/^\\d{4}-\\d{8}$/.test(remito.numero_legal)" in lista and "? remito.numero_legal : remito.id" in lista)

# ---- DEOU: F3 buscar, F4 alta, y siempre con su botón
check("el buscador anuncia F3 y dice por qué se busca: número, OC, cliente o pedido", "Buscar por número, OC, cliente o pedido (F3)..." in lista)
check("Enter en el buscador abre la ficha si hay una sola coincidencia o el número es exacto (consulta al servidor /remitos/buscar)",
      '@keydown.enter.prevent="buscarYAbrir"' in lista and "api.get('/remitos/buscar'" in lista and "if (data.exacto)" in lista and "enLista.length === 1" in lista)
check("el filtro del listado también mira la OC", "normalizarBusqueda(r.oc).includes(query)" in lista and "ocMatch" in lista)
check("F3 y F4 tienen su botón visible: «Buscar (F3)» y «Nuevo remito (F4)»",
      re.search(r'@click="enfocarBusqueda"[^>]*data-accion="buscar"', lista) and re.search(r'@click="nuevoRemito"[^>]*data-accion="nuevo-remito"', lista) and "Nuevo remito (F4)" in lista)
check("F3 enfoca el buscador (cerrando la ficha si estaba abierta) y F4 va al alta; los atajos se sueltan al salir",
      re.search(r"e\.key === 'F3'\) \{ e\.preventDefault\(\); enfocarBusqueda\(\) \}", lista) and re.search(r"e\.key === 'F4'\) \{ e\.preventDefault\(\); nuevoRemito\(\) \}", lista)
      and "window.addEventListener('keydown', onKeyLista)" in lista and "window.removeEventListener('keydown', onKeyLista)" in lista and "if (fichaAbierta()) await router.push({ name: 'RemitoList' })" in lista)
check("ESC cierra la ventana de arriba del listado (fecha, anulación, retiro, edición) y no llega a la ficha de abajo",
      re.search(r"e\.key === 'Escape' && hayModalAbierto\(\)[\s\S]*?e\.stopImmediatePropagation\(\)[\s\S]*?cerrarCambioFecha\(\)[\s\S]*?cerrarAnulacion\(\)[\s\S]*?cerrarAccionFecha\(\)[\s\S]*?closeEditModal\(\)", lista))

# ---- las acciones del listado se comparten con la ficha (no se duplican)
check("el listado ofrece sus acciones a la ficha (provide remitosAcciones) y una versión que sube con cada recarga",
      "provide('remitosAcciones'" in lista and "const version = ref(0)" in lista and "version.value++" in lista
      and all(k in lista for k in ("abrirAnulacion:", "abrirCambioFecha:", "abrirAccionFecha:", "marcarEnDeposito:", "imprimirRemito:", "vistaPrevia:", "openEditModal:", "hayModalAbierto,")))
check("la ficha usa esas acciones (inject) y se relee cuando la versión cambia", "inject('remitosAcciones', null)" in ficha and re.search(r"watch\(\(\) => \(acc && acc\.version \? acc\.version\.value : 0\), \(\) => cargar\(\)\)", ficha))

# ---- la ficha
check("la ficha lee GET /remitos/ficha/<ref> (el número o el id)", "api.get(`/remitos/ficha/${encodeURIComponent(route.params.ref)}`)" in ficha)
check("si llegó con el id y el remito tiene número de siempre, la dirección pasa a ser el número (replace, sin releer dos veces)",
      "router.replace({ name: 'RemitoFicha', params: { ref: canon }, query: {} })" in ficha and "if (route.params.ref !== canon) saltearCambio = true" in ficha and "/^\\d{4}-\\d{8}$/.test(num)" in ficha)
check("la tabla del PR muestra impreso, salió, llegó, facturado, acreditado y los dos pendientes; un renglón que no se factura dice «no aplica»",
      all(k in ficha for k in ("Impreso", "Salió", "Llegó", "Facturado", "Acreditado", "Pend. remitir", "Pend. facturar")) and ficha.count("no aplica") >= 3 and "it.facturado !== null" in ficha)
check("ESC cierra la ficha (si no hay una ventana del listado abierta) y vuelve atrás si hay historia",
      re.search(r"e\.key === 'Escape'\) \{\s*(?:if \(correccion\.visible\)[^\n]*\n\s*)?if \(acc && acc\.hayModalAbierto && acc\.hayModalAbierto\(\)\) return", ficha) and "window.history.state && window.history.state.back" in ficha and "router.back()" in ficha)
check("«Cerrar (ESC)» y «Guardar nota (F10)» son botones a la vista; F10 guarda la nota",
      'data-accion="cerrar"' in ficha and "Cerrar (ESC)" in ficha and 'data-accion="guardar-nota"' in ficha and "Guardar nota (F10)" in ficha and re.search(r"e\.key === 'F10'\) \{\s*e\.preventDefault\(\);?\s*if \(correccion\.visible\) guardarCorreccion\(\)\s*else guardarNota\(\)", ficha))
check("la historia tiene la nota libre (no cambia cantidades) y, aparte, «Corregir lo que pasó» con cuatro causas que abren la corrección",
      "const CAUSAS = [" in ficha and all(f"k: '{c}'" in ficha for c in ("NO_SALIO", "SE_PERDIO", "SE_RECHAZO", "VOLVIO")) and 'data-corregir' in ficha
      and "Anotar una novedad (no cambia cantidades)" in ficha and "api.post(`/remitos/${f.value.remito.id}/notas`" in ficha and '@click="abrirCorreccion(c.k)"' in ficha)
check("la corrección: renglón, causa, cuánto quedó realmente y nota; se guarda en POST /remitos/{id}/correccion con «Guardar corrección (F10)» y se cancela con «Cancelar (ESC)»",
      'data-modal="correccion"' in ficha and 'data-campo="correccion-cantidad"' in ficha and 'data-accion="guardar-correccion"' in ficha and "Guardar corrección (F10)" in ficha and "Cancelar (ESC)" in ficha
      and "api.post(`/remitos/${f.value.remito.id}/correccion`" in ficha and "cantidad_real: Number(correccion.real)" in ficha)
check("solo se corrige un remito con número, no anulado y que no es él mismo una corrección; se corrige lo que QUEDA (> 0) y la cantidad nueva tiene que ser menor",
      "const puedeCorregir = computed(() => !!(f.value && f.value.remito.numero_legal && !anulado.value && !esCorreccion.value))" in ficha and "it.quedo > 0" in ficha
      and "v < it.quedo - 0.0005" in ficha)
check("ESC y F10 se aplican a la ventana de arriba: con la corrección abierta, ESC la cierra (no la ficha) y F10 la guarda",
      re.search(r"if \(correccion\.visible\) \{ e\.preventDefault\(\); cerrarCorreccion\(\); return \}", ficha) and "if (correccion.visible) guardarCorreccion()" in ficha)
check("un remito de corrección se ve como tal en la ficha (insignia, aviso con vínculo al remito que corrige) y no se imprime ni se anula: «Deshacer la corrección»",
      "k: 'correccion'" in ficha and 'data-banner="correccion"' in ficha and 'data-vinculo="remito-corregido"' in ficha and 'data-accion="deshacer-correccion"' in ficha
      and "!anulado && !esCorreccion" in ficha and "acc.abrirAnulacion(remitoLista, 'deshacer-correccion')" in ficha)
check("la tabla del PR muestra «Quedó» y bajo el producto cada corrección (cantidad, causa y fecha)", '<th class="text-right px-2">Quedó</th>' in ficha and 'data-celda="quedo"' in ficha and 'data-correccion' in ficha)
check("no hay 'relojería' en la tabla del PR: es de solo lectura (sin inputs de cantidad); la cantidad se carga en la ventana de corrección", "<input" not in ficha[ficha.index('data-seccion="tabla-pr"'):ficha.index('data-seccion="historia"')])
check("en el listado, una corrección dice «CORRECCIÓN», no se imprime, no tiene vista previa ni «sin papel» y se deshace con motivo (tercer modo del cuadro de anulación)",
      "const esCorreccion = (remito)" in lista and "(esCorreccion(remito) ? 'CORRECCIÓN' : 'BORRADOR')" in lista and "remito.estado === 'ANULADO' || esCorreccion(remito)" in lista
      and "ruta = anulacion.modo === 'anular' ? 'anular' : (anulacion.modo === 'deshacer-correccion' ? 'deshacer-correccion' : 'deshacer-anulacion')" in lista and 'data-accion="deshacer-correccion"' in lista)

# ---- el Remito Manual se retiró (tag remito-manual-original): un remito se arma siempre desde un pedido
check("la pantalla del Remito Manual ya no existe y su dirección vieja redirige al libro de Remitos", not os.path.exists("frontend/src/views/Logistica/ManualRemitoView.vue")
      and re.search(r"path: 'logistica/remito-manual',\s*redirect: \{ name: 'RemitoList' \}", rutas) and "name: 'ManualRemito'" not in rutas)
splitter = leer("frontend/src/views/Logistica/LogisticaSplitter.vue"); inspector = leer("frontend/src/views/Pedidos/PedidoInspector.vue")
check("ninguna pantalla manda al Remito Manual: «Entregas y remitos» ya no tiene «Nuevo Remito (manual)» y el «Remito» del Inspector va al armado del pedido (?armar=1)",
      "ManualRemito" not in splitter and "Nuevo Remito (manual)" not in splitter and "ManualRemito" not in inspector
      and re.search(r"const emitirRemito = \(\) => \{\s*router\.push\(\{\s*name: 'PedidoLogistica',\s*params: \{ id: props\.modelValue\.id \},\s*query: \{ armar: 1 \}", inspector))
srv = leer("backend/remitos/service.py"); rou = leer("backend/remitos/router.py"); sch = leer("backend/remitos/schemas.py")
check("en el servidor ya no hay create_manual, su endpoint POST /remitos/manual ni sus schemas", "def create_manual(" not in srv and '@router.post("/manual"' not in rou and "class ManualRemitoPayload" not in sch and "class ManualRemitoItem" not in sch)
check("«Nuevo remito» (F4) elige el PEDIDO: ventana con buscador (número, OC o cliente), la lista de pedidos por remitar y «Armar remito» que va a su armado (?armar=1)",
      "const nuevoRemito = async () =>" in lista and 'data-modal="elegir-pedido"' in lista and "api.get('/remitos/pedidos-por-remitar'" in lista and 'data-accion="armar-desde-pedido"' in lista
      and re.search(r"router\.push\(\{ name: 'PedidoLogistica', params: \{ id: p\.pedido_id \}, query: \{ armar: 1 \} \}\)", lista) and "ManualRemito" not in lista)
pedidos = barra[barra.index("<!-- PEDIDOS Group -->"):barra.index("<!-- REMITOS Group")]
remitos = barra[barra.index("<!-- REMITOS Group"):barra.index("<!-- PRODUCTOS Group -->")]
check("PEDIDOS ya no lista Remitos ni Reporte de Entregas", not any(f"navigate('{n}')" in pedidos for n in ("RemitoList", "EntregasReport", "ManualRemito")))
check("el grupo REMITOS (naranja) lista Remitos y Reporte de Entregas (el Remito Manual se retiró)",
      all(f"navigate('{n}')" in remitos for n in ("RemitoList", "EntregasReport")) and "ManualRemito" not in barra and "bg-orange-900/20 border-orange-500/30" in remitos and "toggleGroup('REMITOS')" in remitos)
check("el grupo se marca activo (y se despliega) con la lista, la ficha y el reporte de entregas; PEDIDOS ya no",
      "if (group === 'REMITOS') return ['RemitoList', 'RemitoFicha', 'EntregasReport'].includes(route.name)" in barra
      and re.search(r"if \(group === 'PEDIDOS'\) return \[[^\]]*\]", barra) and "'RemitoList'" not in re.search(r"if \(group === 'PEDIDOS'\) return \[[^\]]*\]", barra).group(0)
      and "'PEDIDOS', 'REMITOS', 'INFORMES'" in barra and ".active-link-orange" in barra)

# ---- (se restauran los controles que un parche anterior se llevó puestos) la ficha: acciones, insignias, resumen y color
check("las acciones de siempre están en la ficha, cada una con su condición: imprimir/reimprimir, ver el remito, sin papel, fecha, depósito, retiro, anular, deshacer, editar",
      all(f'data-accion="{a}"' in ficha for a in ("imprimir", "ver-remito", "sin-papel", "cambiar-fecha", "en-deposito", "retiro", "anular", "deshacer-anulacion", "editar")))
check("las insignias del genoma: estado, en depósito, impreso/sin imprimir, salida asumida/confirmada, Rosa · no se factura",
      all(f"k: '{k}'" in ficha for k in ("estado", "en-deposito", "impreso", "sin-imprimir", "salida-confirmada", "salida-asumida", "rosa")) and "Rosa · no se factura" in ficha)
check("la OC, el domicilio del papel, el transporte con «Pedir retiro» y la factura de referencia se ven en el resumen",
      all(k in ficha for k in ('data-campo="oc"', "f.domicilio_entrega", 'data-vinculo="web-retiro"', 'data-campo="factura"')))
check("la ficha es naranja (Logística): marco, cabecera, botón principal y títulos (las insignias de estado conservan su color de significado)",
      "border-2 border-orange-500/40" in ficha and "border-orange-900/30" in ficha and "bg-orange-600" in ficha and "text-orange-300" in ficha)

# ---- [S893, Carlos 26/10] «Ver el remito» reemplaza al dibujo HTML; la devolución se fundió con la corrección «Volvió»; F4 es alta del campo donde se está parado
check("«Ver el remito» (ficha y Entregas y remitos) abre /remitos/{id}/pdf?ver=1; el dibujo HTML y su botón «Imprimir» ya no existen",
      "const verRemito = () =>" in ficha and "/pdf?ver=1" in ficha and 'data-accion="ver-remito"' in ficha and "const verRemito = (remito)" in splitter and "/pdf?ver=1" in splitter and 'data-accion="ver-remito"' in splitter
      and "RemitoTemplate" not in splitter and "openPrint" not in splitter and not os.path.exists("frontend/src/views/Logistica/components/RemitoTemplate.vue"))
check("«Registrar devolución» ya no es un botón aparte de la ficha: la ficha corrige con «Volvió»",
      'data-accion="registrar-devolucion"' not in ficha and "query: { devolucion: 1 }" not in ficha and "CAUSAS" in ficha and "k: 'VOLVIO'" in ficha)
check("en «Entregas y remitos» «Registrar Devolución» pregunta de qué remito volvió (uno solo va directo) y abre su ficha con ?corregir=VOLVIO; el modal viejo de la Etapa 6 ya no está",
      'data-accion="registrar-devolucion"' in splitter and 'data-modal="elegir-remito-devolucion"' in splitter and "query: { corregir: 'VOLVIO' }" in splitter and "if (c.length === 1) return irADevolver(c[0])" in splitter
      and "showDevolucionModal" not in splitter and "devolucionSeleccion" not in splitter and "confirmDevolucion" not in splitter and "openDevolucionModal" not in splitter)
check("la ficha abre la corrección con la causa que llega en ?corregir= y la saca de la dirección (para que no se reabra al recargar)",
      "route.query.corregir" in ficha and "abrirCorreccion(causa)" in ficha and "router.replace({ name: 'RemitoFicha', params: { ref: canon }, query: {} })" in ficha)
check("quién carga con la pérdida: con el transporte del comprador una PÉRDIDA no mueve el pedido (la ventana lo dice y el resumen cambia); lo demás mueve siempre",
      "f.value.remito.riesgo_entrega === 'COMPRADOR' && correccion.causa === 'SE_PERDIO'" in ficha and 'data-campo="correccion-riesgo"' in ficha and "a cargo del comprador" in ficha
      and "el pedido no cambia" in ficha)
check("F4 es el alta del campo donde se está parado: la lista no actúa si el campo ya la atendió (defaultPrevented, p. ej. un selector de cliente) ni con una ventana abierta",
      "(e.key === 'F3' || e.key === 'F4') && (e.defaultPrevented || hayModalAbierto())" in lista)

ok = sum(1 for _, c in checks if c)
print(f"\nRESULTADO: {ok}/{len(checks)} checks OK")
if ok != len(checks):
    print("FALLO:", *[d for d, c in checks if not c], sep="\n  ")
    sys.exit(1)
