import os
import sys
from sqlalchemy import create_engine, text

# Conectar directamente a la Bóveda de Producción para saneamiento
DB_PATH = r"C:\dev\V5-LS\data\V5_LS_MASTER.db"

def fix_prod_rubros():
    if not os.path.exists(DB_PATH):
        print("No se encuentra la BD de Producción:", DB_PATH)
        return

    print("Conectando a SQLite en:", DB_PATH)
    # Windows absolute paths need ///C:/path
    url = f"sqlite:///{DB_PATH}"
    url = url.replace('\\', '/')
    print("URL:", url)
    engine = create_engine(url)
    
    with engine.begin() as conn: # Auto-commits at the end of block
        # Buscar los rubros
        res_lower = conn.execute(text("SELECT id FROM rubros WHERE nombre = 'General'")).fetchone()
        res_upper = conn.execute(text("SELECT id FROM rubros WHERE nombre = 'GENERAL'")).fetchone()
        
        lower_id = res_lower[0] if res_lower else None
        upper_id = res_upper[0] if res_upper else None
        
        print(f"Lower General ID: {lower_id}")
        print(f"Upper GENERAL ID: {upper_id}")
        
        if lower_id and upper_id:
            print("Fusionando...")
            # Migrar P
            res = conn.execute(text("UPDATE productos SET rubro_id = :target WHERE rubro_id = :source"), {"target": lower_id, "source": upper_id})
            print(f"Productos migrados: {res.rowcount}")
            # Migrar subrubros
            res2 = conn.execute(text("UPDATE rubros SET padre_id = :target WHERE padre_id = :source"), {"target": lower_id, "source": upper_id})
            print(f"Sub-rubros migrados: {res2.rowcount}")
            # Eliminar duplicado
            conn.execute(text("DELETE FROM rubros WHERE id = :source"), {"source": upper_id})
            print("Rubro duplicado eliminado.")
        elif upper_id and not lower_id:
            print("Solo existe UPPER. Renombrando...")
            conn.execute(text("UPDATE rubros SET nombre = 'General' WHERE id = :source"), {"source": upper_id})
            
    print("Saneamiento Completado en P.")

if __name__ == "__main__":
    fix_prod_rubros()
