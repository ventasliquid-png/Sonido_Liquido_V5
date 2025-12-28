
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def reconcile():
    local_url = "sqlite:///./pilot.db"
    cloud_url = os.getenv("POSTGRES_URL")
    
    if not cloud_url:
        print("Error: POSTGRES_URL no configurada.")
        return

    engine_l = create_engine(local_url)
    engine_c = create_engine(cloud_url)

    # 1. RUBROS: Definir los rubros permitidos y sus códigos
    # Mapeo: Nombre -> (ID_deseado, Codigo)
    # Buscaremos si existen en la nube para respetar sus IDs si es posible.
    RUBROS_TARGET = {
        "General": "GEN",
        "Guantes": "GUA",
        "Ropa Descartable": "ROP"
    }
    
    print("--- PASO 1: Reconciliación de Rubros ---")
    rubro_map = {} # nombre -> id
    
    with engine_c.connect() as cc:
        for r_name, r_code in RUBROS_TARGET.items():
            res = cc.execute(text("SELECT id FROM rubros WHERE nombre = :n"), {"n": r_name}).fetchone()
            if not res:
                # Buscar por código si el nombre falló
                res = cc.execute(text("SELECT id FROM rubros WHERE codigo = :c"), {"c": r_code}).fetchone()
                
            if res:
                rubro_map[r_name] = res[0]
                # Actualizar nombre y código por las dudas
                cc.execute(text("UPDATE rubros SET nombre = :n, codigo = :c, activo = true WHERE id = :id"), 
                           {"n": r_name, "c": r_code, "id": res[0]})
            else:
                # Crear nuevo con ID serial
                print(f"Inyectando rubro '{r_name}'...")
                cc.execute(text("INSERT INTO rubros (codigo, nombre, activo) VALUES (:c, :n, true)"), 
                           {"c": r_code, "n": r_name})
                new_id = cc.execute(text("SELECT id FROM rubros WHERE codigo = :c"), {"c": r_code}).scalar()
                rubro_map[r_name] = new_id
        cc.commit()

    # Sincronizar a Local
    print("Limpiando y sincronizando rubros locales...")
    with engine_l.connect() as cl:
        cl.execute(text("DELETE FROM rubros"))
        for r_name, r_id in rubro_map.items():
            r_code = RUBROS_TARGET[r_name]
            cl.execute(text("INSERT INTO rubros (id, codigo, nombre, activo) VALUES (:id, :c, :n, true)"), 
                       {"id": r_id, "c": r_code, "n": r_name})
        cl.commit()

    # 2. PRODUCTOS: Base Legal (271 locales)
    print("\n--- PASO 2: Sincronización de Productos (Local -> Cloud) ---")
    with engine_l.connect() as cl, engine_c.connect() as cc:
        local_items = cl.execute(text("SELECT id, nombre, sku FROM productos")).fetchall()
        
        # Mapa de SKUs de la nube
        cloud_items = cc.execute(text("SELECT nombre, sku FROM productos WHERE activo = true")).fetchall()
        name_to_sku_cloud = {p[0].strip().lower(): p[1] for p in cloud_items if p[1]}

        updated_skus = 0
        classified_count = 0
        
        for p_id, p_name, p_sku in local_items:
            p_name_clean = p_name.strip().lower()
            
            # A. Sincronizar SKU
            new_sku = p_sku
            if not p_sku and p_name_clean in name_to_sku_cloud:
                new_sku = name_to_sku_cloud[p_name_clean]
                cl.execute(text("UPDATE productos SET sku = :sku WHERE id = :id"), {"sku": new_sku, "id": p_id})
                updated_skus += 1

            # B. Auto-Clasificación
            target_rubro = "General"
            if "guante" in p_name_clean:
                target_rubro = "Guantes"
            elif any(kw in p_name_clean for kw in ["barbijo", "cofia", "camisolin", "descartable", "cubrezapatos", "cubrecalzado"]):
                target_rubro = "Ropa Descartable"
            
            cl.execute(text("UPDATE productos SET rubro_id = :rid WHERE id = :id"), 
                       {"rid": rubro_map[target_rubro], "id": p_id})
            classified_count += 1
            
        cl.commit()
        print(f"SKUs actualizados en Local: {updated_skus}")
        print(f"Productos re-clasificados: {classified_count}")

    # 3. LIMPIEZA NUBE: Eliminar excedentes
    print("\n--- PASO 3: Limpieza de excedentes en IOWA ---")
    with engine_l.connect() as cl, engine_c.connect() as cc:
        local_names = set(p[1].strip().lower() for p in local_items)
        cloud_prods = cc.execute(text("SELECT id, nombre FROM productos")).fetchall()
        
        deleted_cloud = 0
        for cp_id, cp_name in cloud_prods:
            if cp_name.strip().lower() not in local_names:
                try:
                    # Intentar borrar dependencias si existen (productos_costos)
                    cc.execute(text("DELETE FROM productos_costos WHERE producto_id = :id"), {"id": cp_id})
                    cc.execute(text("DELETE FROM productos WHERE id = :id"), {"id": cp_id})
                    deleted_cloud += 1
                except Exception as e:
                    cc.execute(text("UPDATE productos SET activo = false WHERE id = :id"), {"id": cp_id})
                    print(f"Desactivado (con historial): {cp_name}")
        
        # Limpiar rubros excedentes en la nube (con cuidado de FKs)
        cc.execute(text("UPDATE productos SET rubro_id = NULL WHERE rubro_id NOT IN :ids"), {"ids": tuple(rubro_map.values())})
        cc.execute(text("DELETE FROM rubros WHERE id NOT IN :ids"), {"ids": tuple(rubro_map.values())})
        cc.commit()
        
        print(f"Resumen Cloud: {deleted_cloud} eliminados.")

    print("\n✅ OPERATIVO COMPLETADO.")

if __name__ == "__main__":
    reconcile()
