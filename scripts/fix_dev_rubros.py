import os
import sys
from sqlalchemy import create_engine, text

# Conectar a la Bóveda de Desarrollo
DB_PATH = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"

def fix_dev_rubros():
    if not os.path.exists(DB_PATH):
        print("No se encuentra la BD de Desarrollo:", DB_PATH)
        return

    print("Conectando a SQLite en:", DB_PATH)
    url = f"sqlite:///{DB_PATH}"
    url = url.replace('\\', '/')
    engine = create_engine(url)
    
    with engine.begin() as conn:
        res_lower = conn.execute(text("SELECT id FROM rubros WHERE nombre = 'General'")).fetchone()
        res_upper = conn.execute(text("SELECT id FROM rubros WHERE nombre = 'GENERAL'")).fetchone()
        
        lower_id = res_lower[0] if res_lower else None
        upper_id = res_upper[0] if res_upper else None
        
        print(f"Lower General ID: {lower_id}")
        print(f"Upper GENERAL ID: {upper_id}")
        
        if lower_id and upper_id:
            print("Fusionando...")
            res = conn.execute(text("UPDATE productos SET rubro_id = :target WHERE rubro_id = :source"), {"target": lower_id, "source": upper_id})
            print(f"Productos migrados: {res.rowcount}")
            res2 = conn.execute(text("UPDATE rubros SET padre_id = :target WHERE padre_id = :source"), {"target": lower_id, "source": upper_id})
            print(f"Sub-rubros migrados: {res2.rowcount}")
            conn.execute(text("DELETE FROM rubros WHERE id = :source"), {"source": upper_id})
            print("Rubro duplicado eliminado.")
        elif upper_id and not lower_id:
            print("Solo existe UPPER. Renombrando...")
            conn.execute(text("UPDATE rubros SET nombre = 'General' WHERE id = :source"), {"source": upper_id})
            
    print("Saneamiento Completado en D.")

if __name__ == "__main__":
    fix_dev_rubros()
