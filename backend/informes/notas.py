# backend/informes/notas.py
"""
[S875, DISENO_MODULO_INFORMES_S875_2026-09-26.md S2.3.D] Clasificación de fragmentos de
`Pedido.nota` por prefijo `[SISTEMA] ` -- compartida entre el Informe D (pedidos con notas
relevantes) y el Informe E (buscar en notas), que la reusa tal cual para su fuente Pedido.nota.

Convención obligatoria desde S875 (Carlos, 27/09): toda nota que escriba el sistema arranca
exacto con "[SISTEMA] " (corchete, mayúsculas, corchete, espacio). Con eso, humano/sistema se
resuelve con un solo chequeo, sin lista que mantener. La tabla de abajo es solo para
ponerle nombre propio a los tipos ya catalogados -- no hace falta tocarla para que una nota
de sistema nueva siga contando como sistema.
"""
from typing import List, Optional, Dict

MARCADOR_SISTEMA = "[SISTEMA] "

# Prefijo (línea completa varía por fecha/número, esto es la parte fija) -> (clave, etiqueta).
# Archivo:línea de origen de cada uno, verificado contra el código real (DISENO_MODULO_
# INFORMES_S875_2026-09-26.md §2.3.D):
#   pedidos/router.py:283, :288, :893, :1075, :1391 -- remitos/service.py:943
CATEGORIAS_SISTEMA = [
    ("migrado_a_pedido", "[SISTEMA] Migrado a pedido #", "Migrado a otro pedido"),
    ("nace_por_migracion", "[SISTEMA] Nace por migración desde pedido #", "Nace por migración"),
    ("cierre_con_discrepancia", "[SISTEMA] Cierre confirmado con discrepancia", "Cierre con discrepancia"),
    ("ajuste_post_entrega", "[SISTEMA] Ajuste de cantidad post-entrega", "Ajuste post-entrega"),
    ("mutacion_a_comercial", "[SISTEMA] Mutación ES_NO_COMERCIAL → Comercial", "Mutación a Comercial"),
    ("remito_parcial", "[SISTEMA] Remito Parcial", "Remito Parcial"),
    # [Etapa 7c] ingesta/contra_natura.py -- factura emitida en ARCA sin PR previo, "marcada y
    # contable" (DISENO_CIRCUITO_PR_S869.md §5.1).
    ("contra_natura", "[SISTEMA] Pedido reconstruido desde factura", "Contra natura"),
]
CATEGORIA_SISTEMA_OTRO = ("sistema_otro", "Sistema (otro)")
CATEGORIA_HUMANA = ("nota_humana", "Nota humana")

CATEGORIAS_DISPONIBLES = [(c[0], c[2]) for c in CATEGORIAS_SISTEMA] + [CATEGORIA_SISTEMA_OTRO, CATEGORIA_HUMANA]


def clasificar_fragmento(fragmento: str) -> str:
    """Devuelve la clave de categoría (ver CATEGORIAS_DISPONIBLES) para una línea de nota ya
    recortada. No matchea ninguno de los catalogados pero empieza con el marcador -> sistema
    sin catalogar (nunca cae en humana: doctrina S875, el marcador manda, no la tabla)."""
    if not fragmento.startswith(MARCADOR_SISTEMA):
        return CATEGORIA_HUMANA[0]
    for clave, prefijo, _ in CATEGORIAS_SISTEMA:
        if fragmento.startswith(prefijo):
            return clave
    return CATEGORIA_SISTEMA_OTRO[0]


def fragmentos_clasificados(nota: Optional[str]) -> List[Dict]:
    """Separa `Pedido.nota` por línea y clasifica cada fragmento no vacío.
    Devuelve [{"texto": ..., "categoria": ...}, ...] en el orden original."""
    if not nota:
        return []
    resultado = []
    for linea in nota.split("\n"):
        texto = linea.strip()
        if not texto:
            continue
        resultado.append({"texto": texto, "categoria": clasificar_fragmento(texto)})
    return resultado
