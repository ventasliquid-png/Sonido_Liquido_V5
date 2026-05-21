"""
Text normalization utilities — Shared across Productos and Clientes.
[GY-V16.2 → UTI-64bit] Protocolo de Tokenización Alfabética (Bag of Words).
"""

import unicodedata
import re


def normalize_name(name: str) -> str:
    """
    [GY-V16.2 → UTI-64bit] Protocolo de Tokenización Alfabética (Bag of Words).
    Remueve acentos, unifica siglas, tokeniza, elimina ruido y ordena alfabéticamente.

    Procedimiento:
    1. Normalización Unicode (elimina acentos)
    2. Unificación de Siglas: "S.R.L." -> "SRL" (quita puntos)
    3. Tokenización por espacios y caracteres no-alfanuméricos
    4. Limpieza de ruido (palabras < 2 caracteres)
    5. Ordenamiento alfabético
    6. Sellado (unir sin espacios)

    Ejemplo: "EL TALLER S.R.L." -> "ELRLTALLER"

    Args:
        name: Nombre a normalizar

    Returns:
        Nombre canonicalizado (mayúsculas, sin acentos, alfabéticamente ordenado)
    """
    if not name:
        return ""

    # 1. Normalización Unicode (mata acentos)
    text = unicodedata.normalize('NFKD', str(name))
    text = text.encode('ASCII', 'ignore').decode('ASCII').upper()

    # 2. Unificación de Siglas
    text = text.replace('.', '')

    # 3. Tokenización
    text = re.sub(r'[^A-Z0-9]', ' ', text)
    tokens = text.split()

    # 4. Limpieza de ruido
    tokens = [t for t in tokens if len(t) >= 2]

    # 5. Ordenamiento alfabético
    tokens.sort()

    # 6. Sellado
    return "".join(tokens)
