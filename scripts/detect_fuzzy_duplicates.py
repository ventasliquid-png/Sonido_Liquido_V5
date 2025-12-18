import sys
import os
import difflib

# Add the project root to the python path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.productos.models import Producto, ProductoCosto

def detect_fuzzy_duplicates():
    db = SessionLocal()
    output_file = "SOSPECHOSOS.txt"
    
    try:
        print("--- INICIANDO ESCANEO HEURISTICO ---")
        products = db.query(Producto).filter(Producto.activo == True).all()
        costs = db.query(ProductoCosto).all()
        
        # Map costs by product_id
        cost_map = {c.producto_id: c for c in costs}
        
        n = len(products)
        print(f"Analizando {n} productos activos...")
        
        suspicious_pairs = []
        
        for i in range(n):
            for j in range(i + 1, n):
                p1 = products[i]
                p2 = products[j]
                
                # Basic normalization for comparison
                name1 = p1.nombre.lower().strip()
                name2 = p2.nombre.lower().strip()
                
                similarity = difflib.SequenceMatcher(None, name1, name2).ratio()
                
                if similarity > 0.8:
                    suspicious_pairs.append((similarity, p1, p2))
        
        # Sort by similarity (descending)
        suspicious_pairs.sort(key=lambda x: x[0], reverse=True)
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"REPORTE DE DUPLICADOS HEURISTICOS (>80%)\n")
            f.write(f"Generado: 2025-12-18\n")
            f.write(f"Total Pares Detectados: {len(suspicious_pairs)}\n")
            f.write("="*80 + "\n\n")
            
            for score, p1, p2 in suspicious_pairs:
                c1 = cost_map.get(p1.id)
                c2 = cost_map.get(p2.id)
                
                price1 = f"${c1.precio_fijo_override or c1.costo_reposicion:.2f}" if c1 else "N/A"
                price2 = f"${c2.precio_fijo_override or c2.costo_reposicion:.2f}" if c2 else "N/A"
                
                f.write(f"[{score:.2f}] COINCIDENCIA DETECTADA\n")
                f.write(f"   A: ID {p1.id} | {p1.nombre} | {price1}\n")
                f.write(f"   B: ID {p2.id} | {p2.nombre} | {price2}\n")
                f.write("-" * 40 + "\n")
        
        print(f"✅ Reporte generado: {output_file}")
        print(f"Total sospechosos: {len(suspicious_pairs)}")

    except Exception as e:
        print(f"❌ Error during scan: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    detect_fuzzy_duplicates()
