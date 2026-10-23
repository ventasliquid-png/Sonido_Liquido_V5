r"""S892, Carlos (23/10): buscando los pedidos de Lácteos de Poblet escribió «lacteos» y el Tablero no encontró nada. La función que
quita acentos existía copiada en diez archivos, pero la mitad de los buscadores no la usaba. Ahora hay una sola,
frontend/src/utils/texto.js (normalizarBusqueda), y la usan los doce buscadores que comparaban sin quitar acentos.
(1) La función (en Node): sin acentos, sin mayúsculas, tolera null. (2) Cada buscador la importa y la usa, y no queda ninguno que
compare con `.toLowerCase().includes(` (salvo las búsquedas internas de «consumidor final», que no son del operador).
Verificado además en el banco con la copia de P: «lacteos» y «LÁCTEOS» filtran los 8 pedidos y los 14 remitos de Lácteos."""
import os, sys, io, re, glob, subprocess
RAIZ = r"C:\dev\Sonido_Liquido_V5"
SRC = os.path.join(RAIZ, "frontend", "src")

checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

util = os.path.join(SRC, "utils", "texto.js").replace("\\", "/")
js = ("import { normalizarBusqueda as n } from 'file:///" + util + "'; "
      "console.log(JSON.stringify([n('Lácteos de Poblet SA').includes(n('lacteos')), n('LÁCTEOS'), n(null), n(undefined), n('  Ñandú '), n(3031)]))")
r = subprocess.run(["node", "--input-type=module", "-e", js], capture_output=True, text=True, encoding="utf-8")
check(f"normalizarBusqueda: «lacteos» está en «Lácteos de Poblet SA», sin mayúsculas, null/undefined vacíos, recorta espacios, números como texto [{r.stdout.strip() or r.stderr.strip()[:80]}]",
      r.returncode == 0 and r.stdout.strip() == '[true,"lacteos","","","nandu","3031"]')

BUSCADORES = ["views/Pedidos/PedidoList.vue", "views/Logistica/RemitoListView.vue", "views/Logistica/EntregasView.vue", "components/ventas/ClientLookup.vue",
              "views/Agenda/ContactosView.vue", "views/Hawe/components/AddressSelector.vue", "views/Hawe/components/TransporteManager.vue",
              "views/Maestros/CanteraExplorer.vue", "views/Maestros/components/RubroMigrationCanvas.vue", "views/Maestros/CondicionIvaForm.vue",
              "views/Maestros/RubrosView.vue", "components/common/CommandPalette.vue"]
faltan = []
for rel in BUSCADORES:
    t = io.open(os.path.join(SRC, rel), encoding="utf-8").read()
    if "import { normalizarBusqueda } from '@/utils/texto'" not in t or t.count("normalizarBusqueda(") < 2:
        faltan.append(rel)
check(f"los 12 buscadores importan y usan normalizarBusqueda {faltan or ''}", not faltan)
pedidos = io.open(os.path.join(SRC, "views", "Pedidos", "PedidoList.vue"), encoding="utf-8").read()
check("Tablero de Pedidos (el caso de Carlos): la consulta y la razón social pasan por la misma función",
      "const query = normalizarBusqueda(searchQuery.value)" in pedidos and "normalizarBusqueda(p.cliente?.razon_social).includes(query)" in pedidos)
quedan = []
for p in glob.glob(os.path.join(SRC, "**", "*.vue"), recursive=True) + glob.glob(os.path.join(SRC, "**", "*.js"), recursive=True):
    for i, linea in enumerate(io.open(p, encoding="utf-8").read().split("\n"), 1):
        if ".toLowerCase().includes(" in linea and "normalize" not in linea and "consumidor final" not in linea:
            quedan.append(f"{os.path.relpath(p, SRC)}:{i}")
check(f"no queda ningún buscador que compare sin quitar acentos {quedan[:5] or ''}", not quedan)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
