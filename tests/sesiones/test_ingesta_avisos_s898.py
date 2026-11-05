r"""S898, Carlos 03/11 (caso de la 2625, pedido #144). Dos arreglos de pantalla en la Ingesta de facturas, sin tocar el servidor:
(1) El camino viejo («Vincular Pedido Existente») solo lista pedidos PENDIENTES; si el cliente ya tiene un remito armado sin facturar (pedido ya CUMPLIDO) decía «se creará uno nuevo».
Ahora la pantalla le pide a la conciliación los remitos del cliente (el mismo /conciliacion/candidatos de «Conciliar contra PR») y, si hay, avisa y manda a «Conciliar contra PR»; es solo un aviso:
no bloquea nada ni cambia el flujo. (2) Después de conciliar, la pantalla relee los candidatos y dibujaba el bloqueo FACTURA_DUPLICADA y el aviso SIN_PR_PENDIENTE de la factura recién registrada
encima del cartel verde: ahora, con el resultado a la vista, solo queda el verde. Prueba estática de los dos archivos y compilación de las dos pantallas con @vue/compiler-sfc (Node)."""
import sys, os, re, json, subprocess
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
SRC = os.path.join(RAIZ, "frontend", "src")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
leer = lambda *p: open(os.path.join(SRC, *p), encoding="utf-8").read()
ing, con = leer("views", "Pedidos", "IngestaFacturaView.vue"), leer("views", "Pedidos", "ConciliarFacturaView.vue")

# ---------- (1) aviso en el camino viejo ----------
check("la Ingesta pide los remitos del cliente al mismo endpoint de «Conciliar contra PR» y solo avisa si no hay bloqueos",
      "const cargarPrArmados = async (rawId)" in ing and "/conciliacion/candidatos" in ing and "if (!(data.bloqueos || []).length) prArmados.value = data.prs || [];" in ing)
check("se carga al subir el PDF (después del análisis), al volver del contexto 409 y se limpia en reset()",
      "auditLog.value = previewData.audit_log;\n    await cargarPrArmados(rawId);" in ing and "await analizarRaw(rawId);" in ing[ing.index("const processFile"):ing.index("const processFile") + 1500]   # [S900, Card #213] el análisis pasó a analizarRaw(rawId): mismo código, un nivel menos de sangría, llamado desde processFile
      and "if (ctx.rawId) await cargarPrArmados(ctx.rawId);" in ing and "duplicadoData.value = null;\n    prArmados.value = [];" in ing)
check("si falla la consulta la pantalla queda como siempre (el error se traga, solo es un aviso)",
      re.search(r"cargarPrArmados = async \(rawId\) => \{.*?catch \(e\) \{\s*// sin el aviso la pantalla queda como siempre", ing, re.S) is not None)
check("la franja de «Conciliar contra PR» se pone ámbar y dice cuántos remitos tiene el cliente (con número y pedido); sin remitos conserva el texto de siempre",
      ":class=\"prArmados.length ? 'bg-amber-900/30 border-amber-500/50'" in ing and "{{ prArmadosTexto }}" in ing and "¿El PR ya está armado? Conciliá esta factura contra él en vez de crear un remito nuevo." in ing
      and "`${p.numero_legal} del pedido #${p.pedido_id}`" in ing)
check("con pedidos pendientes hay una nota «Ojo:» bajo «Vincular Pedido Existente»; sin ninguno, el «se creará uno nuevo» pasa a mandar a «Conciliar contra PR»",
      "Ojo: este cliente ya tiene" in ing and "usá «Conciliar contra PR» (arriba), no este camino" in ing and "Sin pedidos pendientes para este cliente — se creará uno nuevo" in ing)
check("es solo un aviso: «Vincular y Proceder» sigue deshabilitado únicamente por falta de pedido elegido y el camino viejo no cambia",
      ":disabled=\"loading || !selectedPedidoId\"" in ing and "prArmados" not in ing[ing.index("const handleProceder"):ing.index("const handleProceder") + 600])

# ---------- (2) la conciliación ya hecha deja solo el cartel verde ----------
check("con el resultado a la vista se ocultan el bloqueo y el aviso (los genera la propia factura recién registrada al releer los candidatos)",
      "<ul v-if=\"!resultado && bloqueosVisibles.length\"" in con and "<ul v-if=\"!resultado && cand.avisos.length\"" in con)
check("el cartel verde sigue mostrándose y el botón de confirmar no cambió",
      "<section v-if=\"resultado\"" in con and "Registrada {{ resultado.tipo_comprobante }} {{ resultado.numero }} y vinculada a" in con and ":disabled=\"!!ev.bloqueos.length || confirmando\"" in con)

# ---------- (3) el total del pedido en cada alternativa ----------
check("cada alternativa de la conciliación muestra el total del pedido y, si es el mismo importe que la factura, lo marca «igual a la factura» (a los centavos)",
      "Total del pedido <b" in con and "{{ moneda(p.pedido_total) }}" in con and "mismoImporte(p.pedido_total, cand.factura.total_final)" in con
      and "Math.abs(Number(a) - Number(b)) < 0.005" in con)

# ---------- compilación de las dos pantallas (Node) ----------
js = ("const fs = require('fs'); const { createRequire } = require('module'); const req = createRequire('C:/dev/Sonido_Liquido_V5/frontend/package.json');"
      "const { parse, compileTemplate, compileScript } = req('@vue/compiler-sfc'); const out = {};"
      "for (const f of ['IngestaFacturaView', 'ConciliarFacturaView']) { const src = fs.readFileSync('C:/dev/Sonido_Liquido_V5/frontend/src/views/Pedidos/' + f + '.vue', 'utf8');"
      "const { descriptor, errors } = parse(src, { filename: f }); let n = errors.length; if (!n) { n += compileTemplate({ source: descriptor.template.content, filename: f, id: 'x' }).errors.length; compileScript(descriptor, { id: 'x' }); } out[f] = n }"
      "console.log(JSON.stringify(out))")
try:
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True, encoding="utf-8", timeout=120)
    res = json.loads(r.stdout.strip())
except (OSError, ValueError, subprocess.SubprocessError):
    res = {}
check("las dos pantallas compilan (parseo, plantilla y script) sin errores", res == {"IngestaFacturaView": 0, "ConciliarFacturaView": 0})

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
