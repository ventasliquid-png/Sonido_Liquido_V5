"""
Motor de Precios V2 (Roca Sólida)
---------------------------------
Este módulo centralizará toda la lógica de cálculo de precios.
"""

from decimal import Decimal

def calcular_precio_roca(costo_reposicion: Decimal, rentabilidad_target_percent: Decimal) -> Decimal:
    """
    Calcula el Precio Roca (Base) a partir del Costo y la Rentabilidad deseada.
    Fórmula: Roca = Costo * (1 + Rentabilidad / 100)
    """
    if costo_reposicion is None or costo_reposicion == 0: return Decimal(0)
    if rentabilidad_target_percent is None: return Decimal(0)
    
    return costo_reposicion * (1 + rentabilidad_target_percent / 100)

def calcular_rentabilidad(costo_reposicion: Decimal, precio_roca: Decimal) -> Decimal:
    """
    Calcula la Rentabilidad (Reverse Engineering) dado un Costo y un Precio Roca.
    Fórmula: Rentabilidad = ((Roca / Costo) - 1) * 100
    """
    if costo_reposicion is None or costo_reposicion == 0: return Decimal(0)
    if precio_roca is None: return Decimal(0)
    
    return ((precio_roca / costo_reposicion) - 1) * 100

# Placeholder para futura lógica de listas y clientes
def calcular_precio_final(precio_roca: Decimal, segmento_cliente: str = None, condicion_fiscal: str = None):
    pass
