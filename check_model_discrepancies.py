import sqlite3
import os

from sqlalchemy import create_engine, inspect
from backend.core.database import Base, engine
from backend.clientes.models import Cliente, Domicilio
from backend.productos.models import Producto, Rubro, ProductoCosto
from sqlalchemy.schema import CreateTable

db_path = "pilot_v5x.db"
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
