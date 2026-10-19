r"""S883, paso 1 de «un domicilio, muchos clientes»: el comparador de direcciones (backend/clientes/direcciones.py) reconoce el mismo lugar escrito distinto y no confunde lugares distintos."""
import sys, os
RAIZ = r"C:\dev\Sonido_Liquido_V5"
sys.path.insert(0, RAIZ); os.chdir(RAIZ)
from backend.clientes.direcciones import comparar, partes_de_calle, lugar_canonico
checks = []
def check(d, c): checks.append((d, bool(c))); print(("[OK]  " if c else "[FAIL]"), d)
def d(calle, numero="", localidad="", prov=None): return {"calle": calle, "numero": numero, "localidad": localidad, "provincia_id": prov}

# (a, b, esperado, descripcion)
casos = [
    (d("Justo, JB Av", "687", "CABA"), d("Avenida Juan B Justo", "N°687", "Ciudad de Buenos Aires"), "IGUAL", "el caso de Carlos: ARCA contra nosotros"),
    (d("Justo, JB Av 687", "", "CABA"), d("Avenida Juan B Justo N°687", "", "Capital Federal"), "IGUAL", "lo mismo con todo escrito en el campo calle"),
    (d("Avenida Juan B Justo", "687", "CABA"), d("Avenida Juan B Justo", "678", "CABA"), "DISTINTA", "digitos cambiados de lugar: otra altura"),
    (d("Av. Corrientes", "687", "CABA"), d("Avenida Juan B Justo", "687", "CABA"), "DISTINTA", "mismo numero en otra calle"),
    (d("Gral. Paz", "1500", "CABA"), d("General Paz Av", "1500", "CABA"), "IGUAL", "abreviatura General"),
    (d("Vieytes ", "1549", "CABA"), d("VIEYTES", "1549", "CABA"), "IGUAL", "mayusculas y espacios (Centro Pet)"),
    (d("DIAGONAL 74", "80", "La Plata"), d("Diagonal 74", "N° 80", "LA PLATA"), "IGUAL", "calle numerada (INAPYR)"),
    (d("AVENIDA 72", "796", "LA PLATA"), d("Av 72", "796", "La Plata"), "IGUAL", "calle numerada (M&M)"),
    (d("Zuviria", "5747", "CABA"), d("Zuviría", "5747", "CABA"), "IGUAL", "acento"),
    (d("Av. Rivadavia", "5000", "CABA"), d("Rivadavia", "5000", "CABA"), "IGUAL", "sin el tipo de via"),
    (d("Corrientes", "1234", "CABA", "C"), d("Corrientes", "1234", "La Plata", "B"), "DISTINTA", "misma calle y altura en otra provincia"),
    (d("Corrientes", "1234", "CABA"), d("Corrientes", "1234", "La Plata"), "PARECIDA", "misma calle y altura, localidades distintas y sin provincia: que mire una persona"),
    (d("Corrientes", "1234", "Rosario", "S"), d("Corrientes", "1234", "Santa Fe", "S"), "PARECIDA", "misma provincia, otra localidad"),
    (d("Ruta Provincial 36 y 630 0, La Plata Sudeste Calle 50 Ambas Veredas", "", "BUENOS AIRES"), d("Ruta Provincial 36 y 630", "S/N", "Poblet"), "PARECIDA", "Gelato contra Poblet: ruta sin altura, que lo decida una persona"),
    (d("Mza 79 Lote 12", "0", "Santiago Del Estero"), d("MZA 79 LOTE 12", "0,", "Santiago Del Estero"), "IGUAL", "manzana y lote, texto identico"),
    (d("Alberdi", "412", "Salta"), d("Alberdi", "421", "Salta"), "DISTINTA", "412 contra 421"),
    (d("San Martin", "100", "Rosario"), d("San Martin", "100", "Rosario"), "IGUAL", "identica"),
    (d("Belgrano", "", ""), d("Belgrano", "", ""), "IGUAL", "sin altura en ninguna, mismo texto"),
    (d("Belgrano", "500", ""), d("Belgrano", "", ""), "PARECIDA", "una con altura y la otra sin"),
    (d("", "", ""), d("Belgrano", "500", ""), "DISTINTA", "sin calle"),
]
for a, b, esp, nota in casos:
    r, why = comparar(a, b)
    check(f"{esp:8s} <- {nota}: {r} {why[-1][:70]}", r == esp)
    r2, _ = comparar(b, a)
    check(f"   simétrica (al revés da lo mismo) [{r2}]", r2 == r)
la, ha, ia = partes_de_calle("Justo, JB Av 687")
check(f"partes de «Justo, JB Av 687»: palabras {la}, altura {ha}, iniciales {ia}", la == ["JUSTO"] and ha == "687" and ia == ["J", "B"])
check("CABA, Ciudad Autónoma de Buenos Aires y «CABA – CABA» son el mismo lugar", all(lugar_canonico(x) == ("C", "CABA") for x in ("CABA", "Ciudad Autónoma de Buenos Aires", "CABA – CABA", "Capital Federal")))
falla = [x for x, ok in checks if not ok]
print(f"\nRESULTADO: {len(checks) - len(falla)}/{len(checks)} checks OK"); [print("FALLO:", x) for x in falla]
sys.exit(1 if falla else 0)
