"""
backend/clientes/direcciones.py
===============================
[S883, Card #158 / paso 1 de "un domicilio, muchos clientes"] ¿Estas dos direcciones son el mismo lugar?

Una persona sabe que «Justo, JB Av 687» (como la escribe ARCA) y «Avenida Juan B Justo N°687» (como la escribimos nosotros) son lo mismo porque compara las PIEZAS, no el texto:
la altura (687) tiene que ser la misma, el nombre de la calle (JUSTO) tiene que estar, las iniciales (JB = Juan B) tienen que cerrar, y el tipo de via («Av», «Avenida»), el «N°» y los «de/la»
no cuentan. Este modulo hace lo mismo y devuelve tres resultados:
  IGUAL     mismas piezas -> se le propone a la persona «usar la existente» (SIEMPRE pregunta; nunca une solo);
  PARECIDA  casi: falta la altura, cambia la localidad dentro de la provincia o las iniciales no cierran -> la mira una persona;
  DISTINTA  otra altura, otra calle u otra provincia.

Sin base de datos ni red: funciones puras, con la tabla de casos probada en test_direcciones_similares_s883.py.
"""
import re
import unicodedata
from typing import Dict, List, Optional, Tuple

TIPOS_DE_VIA = {"AV", "AVDA", "AVENIDA", "CALLE", "C", "PJE", "PASAJE", "PSJE", "DIAG", "DIAGONAL", "BV", "BLVD", "BULEVAR", "BOULEVARD", "RUTA", "RN", "RP", "CAMINO", "AUTOPISTA", "PEATONAL"}
RELLENO = {"DE", "DEL", "LA", "LAS", "EL", "LOS", "Y", "E", "S", "N", "SN", "NRO", "NUM", "NUMERO", "NO", "PISO", "DPTO", "DEPTO", "DTO", "PB"}
ABREVIATURAS = {"GRAL": "GENERAL", "PTE": "PRESIDENTE", "CNEL": "CORONEL", "STA": "SANTA", "STO": "SANTO", "DR": "DOCTOR", "ING": "INGENIERO", "ALTE": "ALMIRANTE", "ALM": "ALMIRANTE",
                "TTE": "TENIENTE", "CAP": "CAPITAN", "BME": "BARTOLOME", "FCO": "FRANCISCO", "PCIA": "PROVINCIA", "PROV": "PROVINCIA"}
ALIAS_CABA = {"CABA", "C A B A", "CAPITAL FEDERAL", "CAPITAL", "CIUDAD DE BUENOS AIRES", "CIUDAD AUTONOMA DE BUENOS AIRES", "CIUDAD AUTONOMA BUENOS AIRES", "BUENOS AIRES CAPITAL",
              "CIUDAD AUTONOMA", "CABA CABA"}


def _sin_acentos(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def _limpio(texto: Optional[str]) -> str:
    t = _sin_acentos(str(texto or "")).upper()
    t = re.sub(r"N\s*\.?\s*[°º]\s*(?=\d)", " ", t)       # N°687, Nº 687 (con el borde de palabra: «Belgrano 500» no es «Belgra» + «no 500»)
    return re.sub(r"[^A-Z0-9]+", " ", t).strip()


def partes_de_calle(texto: Optional[str]) -> Tuple[List[str], Optional[str], List[str]]:
    """(palabras que distinguen la calle, altura o None, iniciales sueltas). La altura es el ultimo numero; un 0 o «S/N» no es altura."""
    toks = [ABREVIATURAS.get(x, x) for x in _limpio(texto).split()]
    toks = [x for x in toks if x not in TIPOS_DE_VIA and x not in RELLENO]
    nums = [x for x in toks if x.isdigit()]
    altura = nums[-1] if nums and int(nums[-1]) > 0 else None
    nombre = [x for x in toks if not (altura and x.isdigit() and x == altura)] if altura else toks
    largas, iniciales = [], []
    for x in nombre:
        if len(x) == 1:
            iniciales.append(x)
        elif len(x) <= 3 and x.isalpha() and not re.search(r"[AEIOU]", x[1:]):   # «JB»: iniciales juntas (sin vocal despues de la primera)
            iniciales.extend(list(x))
        else:
            largas.append(x)
    return largas, altura, iniciales


def lugar_canonico(localidad: Optional[str], provincia_id: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
    """(provincia, localidad) comparables: «CABA», «Ciudad Autonoma de Buenos Aires» y «Capital Federal» son lo mismo."""
    loc = _limpio(localidad)
    prov = _sin_acentos(provincia_id or "").strip().upper() or None   # el codigo («B», «BA») o, si quien llama lo resolvio, el nombre de la provincia
    loc_sin_repetir = " ".join(dict.fromkeys(loc.split()))      # «CABA CABA» -> «CABA»
    if loc in ALIAS_CABA or loc_sin_repetir in ALIAS_CABA or prov in ("C", "CABA", "CAPITAL FEDERAL"):
        return "C", "CABA"
    return prov, (loc or None)


def comparar(a: Dict[str, Optional[str]], b: Dict[str, Optional[str]]) -> Tuple[str, List[str]]:
    """Compara dos direcciones {calle, numero, localidad, provincia_id}. Devuelve (IGUAL | PARECIDA | DISTINTA, razones)."""
    texto_a, texto_b = f"{a.get('calle') or ''} {a.get('numero') or ''}", f"{b.get('calle') or ''} {b.get('numero') or ''}"
    la, ha, ia = partes_de_calle(texto_a)
    lb, hb, ib = partes_de_calle(texto_b)
    nums_a = {x for x in _limpio(texto_a).split() if x.isdigit() and int(x) > 0}
    nums_b = {x for x in _limpio(texto_b).split() if x.isdigit() and int(x) > 0}
    if not la or not lb:
        return "DISTINTA", ["sin nombre de calle comparable"]
    prov_a, loc_a = lugar_canonico(a.get("localidad"), a.get("provincia_id"))
    prov_b, loc_b = lugar_canonico(b.get("localidad"), b.get("provincia_id"))
    if prov_a and prov_b and prov_a != prov_b:
        return "DISTINTA", [f"otra provincia ({prov_a} / {prov_b})"]
    # rutas y esquinas («Ruta 36 y 630»): el ultimo numero puede no ser la altura; hay conflicto solo si ninguna altura aparece como numero en la otra direccion
    altura_en_la_otra = (ha in nums_b) or (hb in nums_a)
    if ha and hb and ha != hb and not altura_en_la_otra:
        return "DISTINTA", [f"altura distinta ({ha} / {hb})"]
    sa, sb = set(la), set(lb)
    corto, largo = (sa, sb) if len(sa) <= len(sb) else (sb, sa)
    if not corto <= largo:
        # sin altura en alguna de las dos (rutas, manzana y lote): si comparten palabras de la calle la mira una persona
        if ((not ha or not hb) or altura_en_la_otra) and len(sa & sb) >= 2:
            return "PARECIDA", [f"comparten {sorted(sa & sb)}: la mira una persona"]
        return "DISTINTA", [f"palabras de la calle sin correspondencia: {sorted(corto - largo)}"]
    razones = [f"misma calle ({', '.join(sorted(corto))})" + (f" y misma altura {ha}" if ha and hb else "")]
    if not ha or not hb:
        return ("PARECIDA", razones + ["falta la altura en alguna de las dos"]) if (ha or hb) or sa != sb else ("IGUAL", razones + ["sin altura en ninguna: texto de la calle idéntico"])
    # las iniciales de un lado (JB) tienen que aparecer entre las iniciales de las palabras del otro (Juan, B)
    for propias, ajenas_largas, ajenas_iniciales in ((ia, lb, ib), (ib, la, ia)):
        pool = [w[0] for w in ajenas_largas] + list(ajenas_iniciales)
        for letra in propias:
            if letra in pool:
                pool.remove(letra)
            else:
                return "PARECIDA", razones + ["las iniciales no cierran"]
    if loc_a and loc_b and loc_a != loc_b and loc_a.split()[0] != loc_b.split()[0]:
        return "PARECIDA", razones + [f"otra localidad ({loc_a} / {loc_b})"]
    return "IGUAL", razones
