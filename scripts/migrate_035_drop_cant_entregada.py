import os
import sys

# Asegurar que 'backend' está en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.core.database import engine
from sqlalchemy import text

def migrate():
    print(f"Migrando base de datos: {engine.url}")
    with engine.begin() as conn:
        try:
            conn.execute(text("ALTER TABLE pedidos_items DROP COLUMN cantidad_entregada"))
            print("Columna 'cantidad_entregada' eliminada exitosamente de pedidos_items.")
        except Exception as e:
            if "no such column" in str(e).lower() or "no such table" in str(e).lower():
                print(f"Aviso: {e} - Probablemente la columna ya fue eliminada.")
            else:
                print(f"Error al eliminar la columna: {e}")
                print("Si usas SQLite < 3.35, ALTER TABLE DROP COLUMN no está soportado. En ese caso, usa recreación de tabla.")

if __name__ == "__main__":
    migrate()
