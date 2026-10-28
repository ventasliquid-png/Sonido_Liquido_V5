r"""S894, Carlos 28/10 (primer día del paquete en P): (1) Genesis Bag cargó la entrega en Pilar (calle_entrega del mismo domicilio) y el pedido seguía
mostrando la fiscal (Gutenberg): el pedido guarda solo domicilio_entrega_id y el papel ya imprimía Pilar; la PANTALLA mostraba el lado fiscal.
utils/domicilio.js (textoEntrega) aplica el criterio del papel (RemitosService._texto_domicilio) en la ficha del pedido, el panel de logística y el
armado del remito. (2) «Nuevo remito» en el menú lateral, bajo REMITOS, como «Nuevo Pedido»: abre el listado con el «¿de qué pedido?» abierto."""
import os, subprocess
RAIZ = r"C:\dev\Sonido_Liquido_V5"
SRC = os.path.join(RAIZ, "frontend", "src")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(*p): return open(os.path.join(SRC, *p), encoding="utf-8").read()

util = os.path.join(SRC, "utils", "domicilio.js").replace("\\", "/")
js = ("import { textoEntrega as t } from 'file:///" + util + "'; "
      "console.log(JSON.stringify([t({calle:'GUTENBERG ',numero:'3801',localidad:'CABA',calle_entrega:'Calle 5',numero_entrega:'1750',localidad_entrega:'Pilar'}),"
      "t({calle:'Roseti',numero:'1482',localidad:'CABA',calle_entrega:'ROSETI',numero_entrega:'1482',localidad_entrega:''}),"
      "t({calle:'Av. Siempre Viva',numero:'742',localidad:'Springfield'}), t(null)]))")
r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, encoding="utf-8")
salida = r.stdout.strip()
check(f"textoEntrega: otra calle de entrega -> la de entrega; la misma calle (en P 49 de 55 la repiten) -> la del domicilio; sin entrega -> la del domicilio; nada -> '' {salida}",
      salida == '["Calle 5 1750 (Pilar)","Roseti 1482 (CABA)","Av. Siempre Viva 742 (Springfield)",""]')
ped, panel, arm = leer("views", "Ventas", "PedidoCanvas.vue"), leer("views", "Pedidos", "components", "LogisticaPanel.vue"), leer("views", "Logistica", "LogisticaSplitter.vue")
check("la ficha del pedido usa textoEntrega en el desplegable de entrega y en la cabecera plegada (no más calle/numero/localidad del lado fiscal)",
      "{{ textoEntrega(dom) }}" in ped and "domicilio: dom ? textoEntrega(dom)" in ped and "{{ dom.calle }} {{ dom.numero }} ({{ dom.localidad }})" not in ped)
check("el panel de logística del pedido y el armado del remito también", "{{ textoEntrega(dom) }}" in panel and "return textoEntrega(dom) || dom.resumen" in arm)
menu, lista = leer("components", "layout", "AppSidebar.vue"), leer("views", "Logistica", "RemitoListView.vue")
check("menú lateral: «Nuevo remito» bajo REMITOS lleva al listado con ?nuevo=",
      "<span>Nuevo remito</span>" in menu and "router.push({ name: 'RemitoList', query: { nuevo: Date.now() } })" in menu)
check("el listado abre el «¿de qué pedido?» al llegar con ?nuevo= (al montarse y si ya estaba abierto) y limpia la marca",
      "watch(() => route.query.nuevo, abrirNuevoDesdeMenu)" in lista and "abrirNuevoDesdeMenu()" in lista and "await router.replace({ name: 'RemitoList' })" in lista)
ok = sum(1 for _, c in checks if c)
print(f"\n{ok}/{len(checks)} checks OK")
