r"""S888, Card #182: los interruptores COMERCIAL/NO COMERCIAL y circuito de la ficha del pedido (frontend/src/views/Ventas/PedidoCanvas.vue) entraban en un BUCLE INFINITO de pedidos al servidor
cuando este respondia error (ej. 401 con la sesion vencida): el watch revertia el valor (isNoComercial.value = !val), esa asignacion volvia a disparar el mismo watch, que volvia a llamar al servidor con
el valor contrario, fallaba, revertia... y en cada vuelta se guardaba el pedido ENTERO. Reproducido en D el 19/10: un clic con un token invalido = 25 pedidos a /no-comercial y 12 guardados en 6 segundos, sin parar.
Arreglo: toda reversion pasa por revertirInterruptor(), que prende una bandera (revirtiendoInterruptor) mientras el watch corre, y ambos watch la respetan (misma tecnica que isHydratingPedido).
Prueba estatica sobre el codigo de la pantalla (no hay corredor de componentes); el comportamiento se verifico ademas en el navegador de D (1 llamada por clic, ambas direcciones, token valido e invalido)."""
import sys, os, re, io
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5\scripts"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
src = leer("frontend/src/views/Ventas/PedidoCanvas.vue")

def bloque(inicio):
    """cuerpo de un watch: desde su apertura hasta el primer cierre `\n});` a la altura de la columna 0"""
    i = src.find(inicio)
    if i < 0: return ""                       # el watch no existe: las comprobaciones de abajo fallan una por una en vez de explotar
    j = src.find("\n});", i)
    return src[i:j if j >= 0 else len(src)]
circuito, nocomercial = bloque("watch(isCircuitoNegro, async (val) => {"), bloque("watch(isNoComercial, async (val) => {")

# la bandera y el ayudante
m = re.search(r"const revirtiendoInterruptor = ref\(false\);\nconst revertirInterruptor = async \(interruptor, valor\) => \{\n(.*?)\n\};", src, re.S)
cuerpo = m.group(1) if m else ""
orden = [cuerpo.find(s) for s in ("revirtiendoInterruptor.value = true;", "interruptor.value = valor;", "await nextTick();", "revirtiendoInterruptor.value = false;")]
check("existe la bandera revirtiendoInterruptor y el ayudante revertirInterruptor", m)
check("el ayudante prende la bandera, asigna el valor, espera al microtask del watch (nextTick) y recien despues apaga la bandera (en ese orden)", all(o >= 0 for o in orden) and orden == sorted(orden))
check("nextTick esta importado de vue", re.search(r"^import \{[^}]*\bnextTick\b[^}]*\} from 'vue';", src, re.M))
pos = [src.find(s) for s in ("const revirtiendoInterruptor = ref(false);", "watch(isCircuitoNegro, async (val) => {", "watch(isNoComercial, async (val) => {")]
check("la bandera se declara ANTES de los dos watch (si no, el watch la lee sin inicializar)", all(x >= 0 for x in pos) and pos == sorted(pos))

# los dos watch la respetan, justo despues de la guarda de hidratacion
for nombre, b in (("circuito", circuito), ("no comercial", nocomercial)):
    check(f"el watch de {nombre} sale enseguida si es una reversion, despues de la guarda de hidratacion",
          re.search(r"if \(isHydratingPedido\.value\) return;[^\n]*\n\s*if \(revirtiendoInterruptor\.value\) return;", b))
    check(f"el watch de {nombre} NO asigna el interruptor directamente: toda reversion pasa por revertirInterruptor",
          not re.search(r"\b(isCircuitoNegro|isNoComercial)\.value\s*=[^=]", b) and "revertirInterruptor(" in b)
check("circuito: se revierte en el error del servidor (a !val) y cuando el servidor corrige el valor (a estadoReal)",
      "await revertirInterruptor(isCircuitoNegro, !val);" in circuito and "await revertirInterruptor(isCircuitoNegro, estadoReal);" in circuito)
check("no comercial: se revierte en las dos salidas con error (el guardado previo de precios y el cambio del servidor)",
      nocomercial.count("await revertirInterruptor(isNoComercial, !val);") == 2)
check("cada reversion termina el watch con return (no sigue a actualizar los flags como si hubiera funcionado)",
      len(re.findall(r"await revertirInterruptor\(isNoComercial, !val\);\n\s*return;", nocomercial)) == 2 and re.search(r"await revertirInterruptor\(isCircuitoNegro, !val\);\n\s*return;", circuito))
check("sigue la guarda de hidratacion original (FIX S870) en los dos watch", circuito.count("isHydratingPedido.value") >= 1 and nocomercial.count("isHydratingPedido.value") >= 1)
check("el interruptor sigue llamando UNA vez al servidor por clic: los endpoints /circuito-bipolar y /no-comercial siguen en sus watch", "/circuito-bipolar" in circuito and "/no-comercial" in nocomercial)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
