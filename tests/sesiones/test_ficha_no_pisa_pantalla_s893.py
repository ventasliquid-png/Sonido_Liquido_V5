r"""S893, Carlos 26/10 (producción, Ceretti SRL): en la ficha del cliente, el buscador de CUIT (el mapamundi) trae razón social, CUIT, condición de IVA y domicilio fiscal, pero SOLO a la pantalla: no
graba nada hasta «Guardar» del cliente. Si antes de eso se editaba el domicilio y se apretaba su «Guardar», el domicilio sí se grababa («Domicilio guardado») y la ficha se recargaba ENTERA desde el servidor:
volvían «Ceretti SRL» y el CUIT 11111111119, como si no se hubiera guardado nada. Era un error viejo: solo la guarda de domicilio fiscal + entrega vinculados y la de contactos recargaban conservando lo que
estaba en pantalla ('merge'); las demás (domicilio simple, bifurcación, «usar el domicilio que ya existía», sincronía, baja y reactivación, vínculos) recargaban entero. Ahora todas conservan lo no guardado
(incluido lo que deja la validación de ARCA) y, si hay datos del cliente sin guardar, el aviso lo dice con nombre propio. Estática sobre ClientCanvas.vue; el comportamiento se verificó además en el banco
(copia de P con el código de D): razón social y CUIT tocados sin guardar + guardar el domicilio → siguen en pantalla y sale el aviso; sin nada pendiente, no avisa."""
import re, io
RAIZ = r"C:\dev\Sonido_Liquido_V5"
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)

cc = io.open(RAIZ + r"\frontend\src\views\Hawe\ClientCanvas.vue", encoding="utf-8").read()

# ---- la causa: ninguna recarga del cliente después de grabar un domicilio o un vínculo es «entera»
enteras = re.findall(r"loadCliente\(form\.value\.id\)", cc)
check(f"ninguna recarga que sigue a grabar un domicilio o un vínculo pisa la pantalla con lo grabado (recargas enteras de «form.value.id»: {len(enteras)})", len(enteras) == 0)
merges = re.findall(r"loadCliente\(form\.value\.id, 'merge'\)", cc)
check(f"las 9 recargas 'merge': domicilio simple, «usar el que ya existía», error al guardar, sincronía, reactivar, baja, vínculo, contacto y fiscal+entrega ({len(merges)})", len(merges) == 9)
check("las cargas iniciales y la del cliente recién creado siguen siendo enteras (es lo correcto: no hay nada en pantalla que conservar)",
      "await loadCliente(props.id)" in cc and "await loadCliente(route.params.id)" in cc and "isNew.value = false; await loadCliente(newId)" in cc)

# ---- lo que se conserva
m = re.search(r"const preserve = \[(.*?)\];", cc, re.S)
lista = m.group(1) if m else ""
for campo in ("razon_social", "cuit", "condicion_iva_id", "segmento_id", "lista_precios_id", "vendedor_id", "flags_estado"):
    check(f"se conserva «{campo}» al recargar con 'merge'", f"'{campo}'" in lista)
for campo in ("estado_arca", "datos_arca_last_update", "nombre_fantasia"):
    check(f"se conserva también «{campo}» (lo que deja la validación de ARCA y el nombre de fantasía)", f"'{campo}'" in lista)

# ---- el aviso
check("la recarga devuelve los datos del cliente que siguen sin guardar (los compara con lo que tiene el servidor, con '' y null como lo mismo)",
      "let sinGuardar = []" in cc and "return sinGuardar" in cc and "vacioANull" in cc and "Object.keys(ETIQUETA_SIN_GUARDAR).filter" in cc)
check("los datos se nombran como los ve el operador: razón social, CUIT, condición de IVA, segmento, lista de precios, vendedor, nombre de fantasía",
      all(t in cc for t in ("razon_social: 'razón social'", "cuit: 'CUIT'", "condicion_iva_id: 'condición de IVA'", "segmento_id: 'segmento'", "lista_precios_id: 'lista de precios'", "vendedor_id: 'vendedor'", "nombre_fantasia: 'nombre de fantasía'")))
check("el aviso dice que el domicilio quedó guardado pero que esos datos del cliente TODAVÍA NO están guardados, y qué hacer",
      "El domicilio quedó guardado, pero estos datos del cliente TODAVÍA NO están guardados:" in cc and "Guardá el cliente para que queden." in cc and "'warning'" in cc.split("const avisarSiFaltaGuardar")[1][:700])
check("al grabar un domicilio simple, el «Domicilio guardado» de éxito solo sale si no hay nada pendiente (si lo hay, avisa en vez de aparentar que quedó todo)",
      "if (!avisarSiFaltaGuardar(sinGuardar) && !isMirrored) notificationStore.add('Domicilio guardado', 'success');" in cc)
check("la guarda de fiscal + entrega vinculados también avisa",
      "notificationStore.add('Domicilio Fiscal y de Entrega actualizados', 'success');\n            avisarSiFaltaGuardar(await loadCliente(form.value.id, 'merge'));".replace("\n", "\r\n") in cc
      or "notificationStore.add('Domicilio Fiscal y de Entrega actualizados', 'success');\n            avisarSiFaltaGuardar(await loadCliente(form.value.id, 'merge'));" in cc)
check("el contacto guardado recarga con 'merge' sin avisar (no toca el domicilio; solo conserva lo no guardado)", "const handleContactoSaved = () => loadCliente(form.value.id, 'merge')" in cc)

ok = sum(1 for _, c in checks if c)
print(f"\nRESULTADO: {ok}/{len(checks)} checks OK")
if ok != len(checks):
    print("FALLO:", *[d for d, c in checks if not c], sep="\n  ")
    raise SystemExit(1)
