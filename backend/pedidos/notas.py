"""[S901, H26 de CA; Carlos 06/11] La nota de un pedido CLONADO.

Antes el clon copiaba `pedido.nota` entera con sus líneas [SISTEMA]: el #157 (clon del #151) decía «Flete a cargo NUESTRO (bit 48)» sin tener el bit 48 y contaba tres conversiones de
circuito que eran del #151; con la #215 (S900) cada clon habría heredado además «Cambio de estado: CUMPLIDO ➔ …» sin el bit 50. Las líneas [SISTEMA] cuentan la historia de UN pedido
(quién hizo qué y cuándo): no se heredan. Lo que escribió una persona (una indicación de entrega, un aviso) sí se conserva.
"""
import re

_DESDE_SISTEMA = re.compile(r"\s*\[SISTEMA\].*")        # una línea [SISTEMA] llega hasta el final de la línea
_ENCABEZADO_CLON = re.compile(r"^\s*Clonado de Pedido #\d+\.\s*")   # el «Clonado de Pedido #N.» del original no se acumula en cadena
# Las notas que escribió el sistema (sin la marca [SISTEMA]) cuando el pedido nació de una factura hablan de ESA factura: «Ingesta Automática Factura: 00001-00002514», «Ingesta en Cuarentena…».
_NOTA_DE_INGESTA = re.compile(r"^\s*Ingesta (?:Autom[aá]tica|en Cuarentena)(?: Factura:.*)?\s*$", re.IGNORECASE)


def nota_para_clon(nota_original, id_original) -> str:
    """«Clonado de Pedido #N.» más lo que escribió una persona en el original (sin las líneas [SISTEMA] ni los «Clonado de…» anteriores)."""
    humano = []
    for linea in (nota_original or "").split("\n"):
        linea = _ENCABEZADO_CLON.sub("", _DESDE_SISTEMA.sub("", linea)).strip()
        if linea and not _NOTA_DE_INGESTA.match(linea):
            humano.append(linea)
    return f"Clonado de Pedido #{id_original}." + ((" " + "\n".join(humano)) if humano else "")
