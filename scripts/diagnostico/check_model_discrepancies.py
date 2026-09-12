import sqlite3
import os
import sys

from dotenv import load_dotenv

# Uso: python scripts/diagnostico/check_model_discrepancies.py [ruta_a_la_base.db]
# Sin argumento mide la misma base que el backend: carga <raiz>/.env con override=True,
# igual que backend/main.py (en B la ruta viene del .env; sin cargarlo se media otra).
# Con argumento mide esa base. Los PRAGMA se hacen sobre la misma ruta que el engine:
# antes estaban hardcodeados a ./pilot_v5x.db y median la base viva aunque se pidiera
# otra, con un log de arranque que mostraba la ruta pedida (hallazgo S864-CA).
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(ROOT_DIR, ".env"), override=True)
if len(sys.argv) > 1:
    os.environ["DATABASE_URL"] = "sqlite:///" + os.path.abspath(sys.argv[1]).replace("\\", "/")

from sqlalchemy import create_engine, inspect
from backend.core.database import Base, engine
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto, Rubro, ProductoCosto
from sqlalchemy.schema import CreateTable

db_path = engine.url.database
print(f"Base medida: {os.path.abspath(db_path)}")
if not os.path.exists(db_path):
    # sqlite3.connect crearia una base vacia y reportaria todas las tablas faltantes.
    print("ERROR: la base no existe.")
    sys.exit(1)
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all tables from SQLAlchemy
tables = Base.metadata.tables

discrepancies = []

for table_name, table in tables.items():
    cursor.execute(f"PRAGMA table_info({table_name});")
    db_cols = {col[1] for col in cursor.fetchall()}
    
    if not db_cols:
        discrepancies.append(f"Table {table_name} NOT FOUND in DB.")
        continue
        
    model_cols = {c.name for c in table.columns}
    missing_in_db = model_cols - db_cols
    if missing_in_db:
        discrepancies.append(f"Table {table_name} missing columns in DB: {missing_in_db}")

if not discrepancies:
    print("NO DISCREPANCIES FOUND.")
else:
    print("DISCREPANCIES FOUND:")
    for d in discrepancies:
        print(f" - {d}")

conn.close()
