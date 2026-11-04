r"""S899, Carlos 04/11: «no tenemos un sistema que nos muestre las facturas ingeridas; debemos abrir el PDF de la factura en otra pestaña e ir conciliando contra el pedido».
La pantalla «Conciliar contra PR» mostraba de la factura solo la cabecera hasta apretar «Comparar», y las alternativas del PR no traían el precio del pedido; el PDF original ya se guarda en la ingesta
(GET /ingesta/raw/{id}/pdf) pero ninguna pantalla lo ofrecía. Ahora la factura queda a la vista desde el principio: sus renglones (lo que lee el sistema del PDF de ARCA), el PDF en la misma pantalla y, en
cada alternativa, los renglones del pedido con su precio. Prueba estática de la pantalla y del endpoint, y compilación con @vue/compiler-sfc (Node)."""
import sys, os, re, json, subprocess
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
SRC = os.path.join(RAIZ, "frontend", "src")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
con = open(os.path.join(SRC, "views", "Pedidos", "ConciliarFacturaView.vue"), encoding="utf-8").read()
rou = open(os.path.join(RAIZ, "backend", "ingesta", "router.py"), encoding="utf-8").read()
cnc = open(os.path.join(RAIZ, "backend", "ingesta", "conciliador.py"), encoding="utf-8").read()

check("la factura queda a la vista desde el principio: bloque «Renglones de la factura (ARCA)» con descripción, cantidad, precio unitario y subtotal, antes de apretar «Comparar» y solo mientras no hay resultado ni es una nota",
      'data-test="renglones-factura"' in con and 'v-if="!resultado && !esAjuste && (cand.factura.items || []).length"' in con and "Renglones de la factura (ARCA)" in con
      and all(s in con for s in ("{{ it.descripcion }}", "{{ it.cantidad }}", "{{ moneda(it.precio_unitario) }}", "{{ moneda(it.subtotal) }}")) and 'v-for="(it, i) in cand.factura.items"' in con)
check("el PDF original se ve en la misma pantalla: botón «Ver PDF» que alterna un visor con el PDF de la factura (iframe) y un enlace para abrirlo en otra pestaña",
      'data-test="ver-pdf"' in con and 'data-test="visor-pdf"' in con and ':src="pdfSrc"' in con and "const pdfSrc = `/ingesta/raw/${rawId}/pdf`" in con and "abrir el PDF en otra pestaña" in con and "const pdfAbierto = ref(false)" in con)
check("cada alternativa muestra el precio del pedido de cada renglón («a $ 5.200,00») junto al producto y lo pendiente",
      "v-if=\"r.precio_pedido != null\"" in con and "a {{ moneda(r.precio_pedido) }}" in con)
check("el servidor ya ofrece los datos: el PDF guardado se sirve en GET /ingesta/raw/{id}/pdf (inline) y /conciliacion/candidatos devuelve la factura con sus renglones y cada renglón del PR con su precio_pedido",
      '@router.get("/raw/{raw_id}/pdf")' in rou and 'media_type="application/pdf"' in rou and '"items": parsed.get("items", [])' in cnc and '"precio_pedido": _precio_efectivo_pedido(pi)' in cnc)
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire(process.argv[1] + '/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const f = 'ConciliarFacturaView';"
      "const src = fs.readFileSync(process.argv[2], 'utf8'); const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length;"
      "if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } console.log(JSON.stringify({ n }))")
try:
    front = os.path.join(RAIZ, "frontend").replace("\\", "/")
    r = subprocess.run(["node", "-e", js, front, os.path.join(SRC, "views", "Pedidos", "ConciliarFacturaView.vue").replace("\\", "/")], capture_output=True, text=True, encoding="utf-8", timeout=120)
    res = json.loads(r.stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res = {}
check("la pantalla compila (parseo, plantilla y script) sin errores", res == {"n": 0})

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
