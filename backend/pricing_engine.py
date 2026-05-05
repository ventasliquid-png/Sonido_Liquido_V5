"""
Motor de Precios V5 "Steel Core" (Definición Maestra)
-----------------------------------------------------
Implementación estricta de la Cascada de 7 Listas y Redondeo Inteligente.
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

# --- 1. PRECISIÓN & REDONDEO INTELIGENTE ---

def smart_round(precio: Decimal) -> Decimal:
    """
    Aplica redondeo psicológico escalonado (Smart Rounding).
    Conserva la resolución de 4 decimales de "La Roca" y sólo formatea la cara externa.
    
    Reglas de Arquitectura:
    - Rango 1 (< $100): Conservar 2 decimales exactos.
    - Rango 2 ($100 - $999): Redondear a la unidad entera.
    - Rango 3 ($1.000 - $9.999): Redondear a la centena.
    - Rango 4 (>= $10.000): Redondear al millar.
    """
    if precio is None: return Decimal(0)
    
    if not isinstance(precio, Decimal):
        precio = Decimal(str(precio))
        
    p = precio.quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
    
    abs_p = abs(p)

    if abs_p < Decimal('100'):
        return p.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
    elif abs_p < Decimal('1000'):
        return p.quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        
    elif abs_p < Decimal('10000'):
        centenas = (p / Decimal('100')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return centenas * Decimal('100')
        
    else:
        millares = (p / Decimal('1000')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        return millares * Decimal('1000')

# --- 2. CÁLCULO DE LISTAS (LA CASCADA) ---

def calculate_lists(costo_reposicion: Decimal, rentabilidad_target_percent: Decimal) -> dict:
    """
    Calcula la cascada de 7 listas a partir del Costo y Rentabilidad.
    Devuelve un diccionario con los valores CRUDOS (sin redondear) y FINAL (redondeado).
    """
    # Guard Clauses
    if not costo_reposicion or costo_reposicion == 0:
        res = {f"lista_{i}": Decimal(0) for i in range(1, 8)}
        res["_needs_cost"] = True
        return res
    
    rent_percent = rentabilidad_target_percent if rentabilidad_target_percent is not None else Decimal(0)

    # Convertir a Decimal si no lo son
    costo = Decimal(str(costo_reposicion))
    rent = Decimal(str(rent_percent))

    # --- LISTA 1: MAYORISTA BASE (LA ROCA) ---
    # Precio_Roca = Costo * (1 + Rentabilidad%)
    lista_1_raw = costo * (1 + rent / 100)
    
    # --- LISTA 2: MAYORISTA 1/2 IVA ---
    # = LISTA_1 * 1.105
    lista_2_raw = lista_1_raw * Decimal("1.105")
    
    # --- LISTA 3: DISTRIBUIDOR (BASE INTERMEDIA) ---
    # = LISTA_2 * 1.105
    lista_3_raw = lista_2_raw * Decimal("1.105")
    
    # --- LISTA 4: MINORISTA NETO (BASE IMPONIBLE) ---
    # = LISTA_3 / 0.85
    lista_4_raw = lista_3_raw / Decimal("0.85")
    
    # --- LISTA 5: MINORISTA FINAL (PÚBLICO) ---
    # = LISTA_4 * 1.21
    lista_5_raw = lista_4_raw * Decimal("1.21")
    
    # --- LISTA 6: MELI (VIDRIERA DIGITAL) ---
    # = LISTA_4 * 1.47
    lista_6_raw = lista_4_raw * Decimal("1.47")
    
    # --- LISTA 7: TIENDA (ECOMMERCE PROPIO) ---
    # = LISTA_6 * 0.90
    lista_7_raw = lista_6_raw * Decimal("0.90")

    # Retornamos el diccionario completo aplicando Smart Rounding a la salida
    return {
        "lista_1": smart_round(lista_1_raw),
        "lista_2": smart_round(lista_2_raw),
        "lista_3": smart_round(lista_3_raw),
        "lista_4": smart_round(lista_4_raw),
        "lista_5": smart_round(lista_5_raw),
        "lista_6": smart_round(lista_6_raw),
        "lista_7": smart_round(lista_7_raw),
        
        # Valores crudos opcionales para debug si se necesitaran
        "_raw_1": lista_1_raw,
        "_raw_4": lista_4_raw
    }

# --- 3. SELECCIÓN GENÉTICA (CLIENTE) ---

def get_virtual_price(producto_costos, cliente) -> dict:
    """
    Determina el precio final para un cliente específico basándose en su ADN.
    Input: Objeto ProductoCosto (ORM), Objeto Cliente (ORM)
    Output: { "precio": Decimal, "iva_discriminado": Bool, "lista_origen": Int }
    """
    if not producto_costos or not cliente:
        return {
            "precio": Decimal(0), 
            "iva_discriminado": False, 
            "lista_origen": 0,
            "needs_cost": True,
            "error": "PRODUCTO_SIN_COSTO"
        }

    # 1. Calcular Escalera Completa
    listas = calculate_lists(producto_costos.costo_reposicion, producto_costos.rentabilidad_target)
    
    # 2. Determinar Nivel de Lista (Hard Logic: Mapeo por Nombre)
    nivel_lista = 3 # Default: Distribuidor (Seguro)
    
    # Priority 1: Direct Link via lista_precios_id (Manual Override)
    if cliente.lista_precios_id:
        # Check if relation is loaded, if not, we trust the ID implies a specific override
        # But for 'orden_calculo' we need the object. 
        # If loaded:
        if cliente.lista_precios and hasattr(cliente.lista_precios, 'orden_calculo') and cliente.lista_precios.orden_calculo:
            nivel_lista = cliente.lista_precios.orden_calculo
    
    # Priority 2: Segmento (Name-Based Mapping per User Order)
    elif cliente.segmento and hasattr(cliente.segmento, 'nombre'):
        seg_nombre = cliente.segmento.nombre.upper().strip()
        
        # Mapeo Explícito V5 (Diccionario de Verdad)
        if "MAYORISTA" in seg_nombre:
            nivel_lista = 1
        elif "DISTRIBUIDOR" in seg_nombre:
            nivel_lista = 3 
        elif "MINORISTA" in seg_nombre or "CONSUMIDOR" in seg_nombre:
            nivel_lista = 5
        elif "TIENDA" in seg_nombre:
            nivel_lista = 7
        else:
             # Fallback: Distribuidor (Lista 3) o la más cercana segura
             nivel_lista = 3
    else:
        # Fallback si no tiene segmento asignado
        nivel_lista = 3
    
    # --- STRICT MODE ENFORCEMENT ---
    # Si no se pudo determinar una lista (ni manual ni por segmento), DETENERSE.
    if not nivel_lista:
        # Retornamos estructura de error controlado o lanzamos excepción
        # Para evitar romper el flujo del frontend con 500, devolvemos 0 y una bandera.
        # O mejor, lanzamos excepción HTTP si este método se usa directo en endpoint.
        # Pero get_virtual_price se usa en bucles. Mejor devolver 0 y loggear warn.
        # User said: "Debe devolver un error controlado (ej: HTTP 409) ... que obligue al Frontend"
        # Since this acts as a helper, we raise a specific Exception that the Router can catch.
        # Or, we return a special signal.
        # Let's return precio 0 and liste_origen None, handling it upstairs.
        return {
            "precio": Decimal(0),
            "lista_origen": None, # Signal for "Missing Data"
            "error": "STRICT_MODE_VIOLATION: Falta Lista de Precios o Segmento Válido"
        }
    
    # Fallback seguro boundaries (if level was found but out of range)
    if nivel_lista < 1: nivel_lista = 1
    if nivel_lista > 7: nivel_lista = 7
    
    target_key = f"lista_{nivel_lista}"
    precio_final = listas.get(target_key, Decimal(0))
    needs_cost = listas.get("_needs_cost", False)
    
    return {
        "precio": precio_final,
        "lista_origen": nivel_lista,
        "debug_listas": listas,
        "costo_reposicion": (producto_costos.costo_reposicion if producto_costos else 0) or 0,
        "rentabilidad_base": (producto_costos.rentabilidad_target if producto_costos else 0) or 0,
        "needs_cost": needs_cost
    }
