r"""S893, Carlos 26/10: «Origen: Despacha / Retira, no entiendo qué quisimos poner con eso, parece contradictorio». En la ficha del cliente cada domicilio de entrega tenía DOS preguntas que se pisaban:
el método (Retiro local / Transporte / Moto-Flete / Plataforma) y el «Origen» (Despacha / Retira), que el formulario ataba al método y que no leía nadie salvo el punto naranja «necesita entrega».
Se retira «Origen» de las pantallas (la columna `origen_logistico` queda en la base y sus valores viejos se siguen respetando); el que retira es el método «Retiro local»; los dos formularios
(DomicilioForm y DomicilioSplitCanvas) ofrecen las mismas cuatro opciones y piden transportista tanto en Transporte como en Moto/Flete. Estática sobre las pantallas y prueba directa de la propiedad."""
import sys, os, io, re
sys.path.insert(0, r"C:\dev\Sonido_Liquido_V5"); os.chdir(r"C:\dev\Sonido_Liquido_V5")
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def leer(p): return io.open(p, encoding="utf-8").read().replace("\r\n", "\n")
form = leer("frontend/src/views/Hawe/components/DomicilioForm.vue")
split = leer("frontend/src/views/Hawe/components/DomicilioSplitCanvas.vue")
insp = leer("frontend/src/views/Hawe/components/ClienteInspector.vue")
cc = leer("frontend/src/views/Hawe/ClientCanvas.vue")
panel = leer("frontend/src/views/Pedidos/components/LogisticaPanel.vue")

form_sin_comentarios = re.sub(r"<!--[\s\S]*?-->", "", re.sub(r"(?m)^\s*//[^\n]*$", "", form))
check("DomicilioForm ya no pregunta «Origen» (ni Despacha ni Retira) ni lo ata al método",
      all(t not in form_sin_comentarios for t in ("origen_logistico", "DESPACHO_NUESTRO", "RETIRO_EN_PLANTA", ">Origen<", "Despacha", "Retira<")))
check("DomicilioSplitCanvas tampoco", "origen_logistico" not in split and "DESPACHO_NUESTRO" not in split and "RETIRO_EN_PLANTA" not in split)
check("la ficha del cliente (ClientCanvas) ya no copia ni manda origen_logistico", "origen_logistico" not in cc)
check("el pedido (LogisticaPanel) ya no escribe origen_logistico al elegir la oficina", "origen_logistico" not in panel and "updateData.metodo_entrega = 'RETIRO_LOCAL'" in panel)
check("el ícono del domicilio en el inspector sale del método: «Retiro local» = nos retiran, el resto = despachamos",
      "dom.metodo_entrega === 'RETIRO_LOCAL' ? 'Nos retiran' : 'Despachamos'" in insp and "origen_logistico" not in insp)
opciones_form = re.findall(r"id: '([A-Z_]+)', icon: 'fa-[a-z-]+', label", form)
opciones_split = re.search(r"v-for=\"method in \[([^\]]*)\]\"", split).group(1)
opciones_split = re.findall(r"'([A-Z_]+)'", opciones_split)
check(f"los dos formularios ofrecen las mismas cuatro opciones: {sorted(opciones_form)}", sorted(opciones_form) == sorted(opciones_split) == sorted(["RETIRO_LOCAL", "TRANSPORTE", "FLETE_MOTO", "PLATAFORMA"]))
check("los dos piden el transportista tanto con Transporte como con Moto/Flete",
      "['TRANSPORTE', 'FLETE_MOTO'].includes(form.metodo_entrega)" in form and "['TRANSPORTE', 'FLETE_MOTO'].includes(form.metodo_entrega)" in split)

import backend.main   # carga todos los modelos (el mapeador de SQLAlchemy los necesita juntos)
from backend.clientes.models import Cliente, Domicilio
def cli(*doms):
    c = Cliente(); c.domicilios = [Domicilio(es_entrega=True, activo=True, **d) for d in doms]; return c
check("requiere_entrega: un domicilio con «Retiro local» NO necesita entrega, aunque su «origen» viejo diga DESPACHO_NUESTRO (el caso inconsistente que había en P)",
      cli(dict(metodo_entrega="RETIRO_LOCAL", origen_logistico="DESPACHO_NUESTRO")).requiere_entrega is False)
check("requiere_entrega: Transporte, Moto/Flete, Plataforma o sin método SÍ necesitan entrega",
      all(cli(dict(metodo_entrega=m)).requiere_entrega is True for m in ("TRANSPORTE", "FLETE_MOTO", "PLATAFORMA", None)))
check("requiere_entrega: el dato viejo RETIRO_EN_PLANTA se sigue respetando (los domicilios cargados antes)", cli(dict(metodo_entrega="TRANSPORTE", origen_logistico="RETIRO_EN_PLANTA")).requiere_entrega is False)
check("requiere_entrega: con un solo domicilio que necesite entrega alcanza; sin domicilios de entrega activos, no",
      cli(dict(metodo_entrega="RETIRO_LOCAL"), dict(metodo_entrega="TRANSPORTE")).requiere_entrega is True and Cliente().__class__ is Cliente and cli().requiere_entrega is False)

falla = [d for d, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", d) for d in falla]
sys.exit(1 if falla else 0)
