import sys
import os
import csv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Add project root to path
sys.path.append(os.getcwd())

from backend.productos.models import Producto, ProductoCosto

def simulate_price_impact():
    print("--- INICIANDO SIMULACIÓN DE PRECIOS: CELTRAP FEBRERO 2026 ---")
    
    # 1. Connect to DB
    engine = create_engine("sqlite:///pilot.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # 2. Read CSV
    csv_path = r"LISTAS_PRECIO/Proveedores/Celtrap/comparativa_precios_celtrap.csv"
    if not os.path.exists(csv_path):
        print(f"Error: No se encuentra {csv_path}")
        return

    print(f"Leyendo: {csv_path}\n")
    
    updates = []
    
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            print(f"{'SKU':<10} {'PRODUCTO':<40} {'COSTO ACTUAL':<15} {'COSTO NUEVO':<15} {'VARIACIÓN':<10} {'PRECIO CALC':<15}")
            print("-" * 110)

            for row in reader:
                try:
                    sku_code = int(row['Codigo'])
                    new_cost_csv = float(row['Costo Nuevo (Feb 2026)']) if row['Costo Nuevo (Feb 2026)'] else 0.0
                except (ValueError, KeyError) as e:
                    # print(f"Skipping row: {e}")
                    continue

                # --- REGLA DE NEGOCIO (Camilleros 301) ---
                if sku_code == 301:
                    # Logic: Apply 10% to OLD cost (we need to fetch old cost first)
                    override_rule = True
                else:
                    override_rule = False
                
                # Find in DB
                product = session.execute(select(Producto).where(Producto.sku == sku_code)).scalar_one_or_none()
                
                if product:
                    # Get current cost
                    cost_entry = session.execute(select(ProductoCosto).where(ProductoCosto.producto_id == product.id)).scalar_one_or_none()
                    
                    current_cost = float(cost_entry.costo_reposicion) if cost_entry else 0.0
                    
                    # Calculate New Cost based on Rule
                    if override_rule:
                        final_new_cost = current_cost * 1.10
                        note = "(* 10% RULE)"
                    else:
                        final_new_cost = new_cost_csv
                        note = ""
                    
                    # Calculate Variation
                    if current_cost > 0:
                        variation = ((final_new_cost - current_cost) / current_cost) * 100
                    else:
                        variation = 100.0 # New Item logic
                    
                    # Calculate Simulated Price (Using Rentabilidad Target)
                    rentabilidad = float(cost_entry.rentabilidad_target) if cost_entry else 30.0
                    simulated_price = final_new_cost * (1 + (rentabilidad / 100))
                    
                    # Print Row
                    print(f"{sku_code:<10} {product.nombre[:38]:<40} ${current_cost:<14.2f} ${final_new_cost:<14.2f} {variation:>6.1f}% {note:<10} ${simulated_price:<14.2f}")
                    
                    updates.append({
                        "sku": sku_code,
                        "old": current_cost,
                        "new": final_new_cost
                    })
                else:
                    # Product not in DB
                    print(f"{sku_code:<10} [NO EN DB] {row['Descripcion'][:30]}...")
                    pass

    except Exception as e:
        print(f"Error crítico en script: {e}")
    finally:
        session.close()

    print("\n--- RESUMEN ---")
    print(f"Productos procesados/encontrados: {len(updates)}")
    print("Simulación finalizada. No se modificó la base de datos.")

if __name__ == "__main__":
    simulate_price_impact()
