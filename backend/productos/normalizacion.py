"""
Normalizacion PROPIA de nombres de producto (Card #152, S879).

`backend.core.utils.text.normalize_name` (bolsa de palabras) la comparten los clientes y descarta los
tokens de un solo caracter: para un producto eso borra justamente lo que lo distingue («Bidon 5 L» y
«Bidon 1 L» daban la misma clave; «Talle M» y «Talle L» tambien). Aca se conserva todo lo que
identifica una presentacion y se descarta solo el ruido.

Solo libreria estandar: la usan el servicio, el modelo y la migracion 048 (que la carga por ruta).

- `normalizar_producto(nombre)`: clave canonica, EXACTA en numeros, unidades y talles. Dos nombres con la
  misma clave son el mismo producto (bloquea el alta). Insensible a acentos, mayusculas, orden de las
  palabras, «de/del/x/por/con...» y a como se escribe la unidad («5 lts», «5 litros», «5L» -> `5L`).
- `similitud(a, b)`: 0.0 si difieren las medidas (numeros, unidades, talles) y, si coinciden, un puntaje
  tolerante a errores de tipeo y plurales sobre las palabras. Sirve para SUGERIR («¿es este producto?»),
  nunca para bloquear.
"""
import re
import unicodedata
from difflib import SequenceMatcher

# Ruido que no identifica nada. Corto a proposito: cada palabra que se agrega aca hace que mas nombres
# distintos den la misma clave.
_RUIDO = {"DE", "DEL", "LA", "EL", "LOS", "LAS", "Y", "EN", "X", "POR", "CON"}

# Unidad escrita de cualquier manera -> unidad canonica (se pega al numero: «5 lts» -> «5L»).
_UNIDADES = {
    "LITROS": "L", "LITRO": "L", "LTS": "L", "LT": "L", "L": "L",
    "ML": "ML", "MLS": "ML", "CC": "ML",
    "KILOGRAMOS": "KG", "KILOGRAMO": "KG", "KILOS": "KG", "KILO": "KG", "KGS": "KG", "KG": "KG",
    "GRAMOS": "G", "GRAMO": "G", "GRS": "G", "GR": "G", "G": "G",
    "CM": "CM", "MM": "MM", "MTS": "M", "MT": "M", "METROS": "M", "METRO": "M",
    "UNIDADES": "U", "UNIDAD": "U", "UNID": "U", "UN": "U", "U": "U",
}
# alternativas ordenadas de la mas larga a la mas corta para que «LITROS» no se corte en «L»
_ALT = "|".join(sorted(_UNIDADES, key=len, reverse=True))
_NUM_UNIDAD = re.compile(r"(\d+(?:\.\d+)?)\s*(" + _ALT + r")(?![A-Z0-9])")
_PORCENTAJE = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_TOKEN = re.compile(r"[A-Z0-9]+(?:\.[0-9]+)?")
# «litro» / «kilo» sueltos (sin numero adelante) significan uno: «botella de litro» = «botella 1 litro»
_SUELTAS = {"LITRO": "1L", "KILO": "1KG"}
_TALLES = {"XS", "XXS", "XL", "XXL", "XXXL"}


def _tokens(nombre):
    if not nombre:
        return []
    t = unicodedata.normalize("NFKD", str(nombre)).encode("ASCII", "ignore").decode("ASCII").upper()
    t = re.sub(r"(?<=\d),(?=\d)", ".", t)  # 1,5 -> 1.5
    t = _PORCENTAJE.sub(lambda m: m.group(1) + "PCT", t)
    t = _NUM_UNIDAD.sub(lambda m: m.group(1) + _UNIDADES[m.group(2)], t)
    salida = []
    for tok in _TOKEN.findall(t):
        if tok in _RUIDO:
            continue
        salida.append(_SUELTAS.get(tok, tok))
    return salida


def normalizar_producto(nombre) -> str:
    """Clave canonica de un nombre de producto: tokens ordenados, unidades unificadas, numeros conservados."""
    return " ".join(sorted(_tokens(nombre)))[:300]


def _es_medida(tok: str) -> bool:
    """Numeros (con o sin unidad), codigos como L5 y talles (una letra suelta, XL...): todo lo que
    distingue una presentacion de otra y no admite «parecido»."""
    return any(c.isdigit() for c in tok) or len(tok) == 1 or tok in _TALLES


def _partir(nombre):
    toks = _tokens(nombre)
    medidas = frozenset(t for t in toks if _es_medida(t))
    palabras = " ".join(sorted(t for t in toks if not _es_medida(t)))
    return medidas, palabras


def similitud(a, b) -> float:
    """0.0 si las medidas no coinciden exactamente; si coinciden, parecido (0..1) de las palabras."""
    ma, pa = _partir(a)
    mb, pb = _partir(b)
    if ma != mb or not pa or not pb:
        return 0.0
    return SequenceMatcher(None, pa, pb).ratio()


UMBRAL_SUGERENCIA = 0.85
