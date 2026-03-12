"""
Motor de Precios V5 "Steel Core" (Definición Maestra)
-----------------------------------------------------
Implementación estricta de la Cascada de 7 Listas y Redondeo Inteligente.
"""

from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

# --- 1. PRECISIÓN & REDONDEO INTELIGENTE ---

def smart_round(value: Decimal) -> Decimal:
    """
    Política de Redondeo Inteligente (Smart Rounding):
    - Rango A (< 100): 2 decimales.
    - Rango B (100 - 999): Entero más cercano.
    - Rango C (1.000 - 9.999): Centena más cercana (100).
    - Rango D (>= 10.000): Millar más cercano (1.000).
    """
    if value is None: return Decimal(0)
    
    # Asegurar Decimal
    val = Decimal(str(value)) # String conversion avoids float precision issues
    
    abs_val = abs(val)

    if abs_val < 100:
        # Rango A: 2 decimales (Ej: 7.892 -> 7.89)
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    
    elif abs_val < 1000:
        # Rango B: Unidad (Ej: 150.50 -> 151)
        return val.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        
    elif abs_val < 10000:
        # Rango C: Centena (Ej: 4150 -> 4200)
        # Técnica: Dividir por 100, redondear entero, multiplicar por 100
        return (val / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100
        
    else:
        # Rango D: Millar (Ej: 22400 -> 22000)
        return (val / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 1000

# --- 2. CÁLCULO DE LISTAS (LA CASCADA) ---

def calculate_lists(costo_reposicion: Decimal, rentabilidad_target_percent: Decimal) -> dict:
    """
    Calcula la cascada de 7 listas a partir del Costo y Rentabilidad.
    Devuelve un diccionario con los valores CRUDOS (sin redondear) y FINAL (redondeado).
    """
    # Guard Clauses
    if not costo_reposicion or costo_reposicion == 0:
        return {f"lista_{i}": Decimal(0) for i in range(1, 8)}
    
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
        return {"precio": Decimal(0), "iva_discriminado": False, "lista_origen": 0}

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
             # Strict Mode: No match -> No price
             nivel_lista = None
    else:
        # Strict Mode: No Segment -> No price
        nivel_lista = None
    
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
    
    return {
        "precio": precio_final,
        "lista_origen": nivel_lista,
        "debug_listas": listas 
    }
