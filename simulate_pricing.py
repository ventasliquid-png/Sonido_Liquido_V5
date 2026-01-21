import sqlite3
from decimal import Decimal, ROUND_HALF_UP

# Redondeo Inteligente (Copy-paste from pricing_engine.py logic)
def smart_round(value: Decimal) -> Decimal:
    if value is None: return Decimal(0)
    val = Decimal(str(value))
    abs_val = abs(val)
    if abs_val < 100:
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    elif abs_val < 1000:
        return val.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    elif abs_val < 10000:
        return (val / 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 100
    else:
        return (val / 1000).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 1000

def calculate_lists(costo, rent):
    if not costo or costo == 0:
        return {f"lista_{i}": Decimal(0) for i in range(1, 8)}
    
    costo = Decimal(str(costo))
    rent = Decimal(str(rent))
    
    l1 = costo * (1 + rent / 100)
    l2 = l1 * Decimal("1.105")
    l3 = l2 * Decimal("1.105")
    l4 = l3 / Decimal("0.85")
    l5 = l4 * Decimal("1.21")
    l6 = l4 * Decimal("1.47")
    l7 = l6 * Decimal("0.90")
    
    return {
        "lista_1": smart_round(l1),
        "lista_2": smart_round(l2),
        "lista_3": smart_round(l3),
        "lista_4": smart_round(l4),
        "lista_5": smart_round(l5),
        "lista_6": smart_round(l6),
        "lista_7": smart_round(l7)
    }

db_path = 'pilot.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get some clients and their segments
print("--- Clientes & Segmentos ---")
cursor.execute("SELECT id, razon_social, segmento_id, lista_precios_id FROM clientes LIMIT 5")
clients = cursor.fetchall()
for c in clients:
    seg_name = "None"
    if c[2]:
        cursor.execute("SELECT nombre FROM segmentos WHERE id=?", (c[2],))
        res = cursor.fetchone()
        if res: seg_name = res[0]
    
    list_name = "None"
    if c[3]:
        cursor.execute("SELECT nombre FROM listas_precios WHERE id=?", (c[3],))
        res = cursor.fetchone()
        if res: list_name = res[0]
        
    print(f"ID: {c[0]} | {c[1]} | Segmento: {seg_name} | Lista Manual: {list_name}")

# Get some products and test calculation
print("\n--- Test Calcupation (Product ID 153: Cubrezapatos) ---")
cursor.execute("SELECT costo_reposicion, rentabilidad_target FROM productos_costos WHERE producto_id=153")
costo, rent = cursor.fetchone()
print(f"Costo: {costo}, Rent Target: {rent}")
listas = calculate_lists(costo, rent)
for k, v in listas.items():
    print(f"{k}: {v}")

conn.close()
