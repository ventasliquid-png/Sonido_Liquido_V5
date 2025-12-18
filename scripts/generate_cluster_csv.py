import sys
import os
import difflib
import csv
from collections import defaultdict

# Add the project root to the python path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal
from backend.productos.models import Producto, ProductoCosto

def generate_cluster_csv():
    db = SessionLocal()
    output_file = "REVISION_DUPLICADOS.csv"
    
    try:
        print("--- INICIANDO CLUSTERING DE DUPLICADOS ---")
        products = db.query(Producto).filter(Producto.activo == True).all()
        costs = db.query(ProductoCosto).all()
        
        # Map costs by product_id
        cost_map = {c.producto_id: c for c in costs}
        
        n = len(products)
        print(f"Productos Activos: {n}")
        
        # Adjacency list for the graph
        adj = defaultdict(list)
        
        # Build graph based on similarity
        # Optimziation: Sort by name length to avoid huge comparisons? 
        # No, 300 items is small enough for O(N^2)
        print("Calculando similitudes...")
        for i in range(n):
            for j in range(i + 1, n):
                p1 = products[i]
                p2 = products[j]
                
                name1 = p1.nombre.lower().strip()
                name2 = p2.nombre.lower().strip()
                
                similarity = difflib.SequenceMatcher(None, name1, name2).ratio()
                
                if similarity > 0.8:
                    adj[p1.id].append(p2.id)
                    adj[p2.id].append(p1.id)
        
        # Find connected components (Clusters)
        visited = set()
        clusters = [] 
        product_map = {p.id: p for p in products}
        
        for p in products:
            if p.id not in visited:
                # BFS to find component
                component = []
                queue = [p.id]
                visited.add(p.id)
                
                while queue:
                    curr_id = queue.pop(0)
                    component.append(curr_id)
                    
                    for neighbor_id in adj[curr_id]:
                        if neighbor_id not in visited:
                            visited.add(neighbor_id)
                            queue.append(neighbor_id)
                
                # Only adding clusters with > 1 element? 
                # User asked to group duplicates. Singletons are not duplicates.
                if len(component) > 1:
                    clusters.append(component)
        
        print(f"Clusters encontrados: {len(clusters)}")
        
        # Generate CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['GRUPO_ID', 'ID_PRODUCTO', 'NOMBRE', 'PRECIO', 'STOCK']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            
            cluster_id = 1
            for cluster in clusters:
                # Sort by ID for consistency
                cluster.sort()
                
                for pid in cluster:
                    prod = product_map[pid]
                    cost = cost_map.get(pid)
                    
                    # Calculate Price
                    if cost:
                        if cost.precio_fijo_override:
                             price = float(cost.precio_fijo_override)
                        else:
                             # Default margin calc (simplified)
                             price = float(cost.costo_reposicion) * (1 + float(cost.margen_mayorista)/100)
                    else:
                        price = 0.0
                    
                    # Stock logic (Mocked as N/A per investigation)
                    stock = "N/A" 
                    
                    writer.writerow({
                        'GRUPO_ID': cluster_id,
                        'ID_PRODUCTO': pid,
                        'NOMBRE': prod.nombre,
                        'PRECIO': f"{price:.2f}",
                        'STOCK': stock
                    })
                
                cluster_id += 1
                
        print(f"✅ Archivo generado: {output_file}")
            
    except Exception as e:
        print(f"❌ Error during clustering: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    generate_cluster_csv()
