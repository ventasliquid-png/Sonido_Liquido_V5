import sys
import os
from sqlalchemy import create_engine, text

# Hardcoded connection string from backend/core/database.py defaults
DATABASE_URL = "postgresql://postgres:e@34.95.172.190:5432/postgres"

def add_segmento_column():
    print(f"Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Check if column exists
            result = connection.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='clientes' AND column_name='segmento_id'"))
            if result.fetchone():
                print("Column 'segmento_id' already exists in 'clientes'. Skipping.")
            else:
                print("Adding 'segmento_id' column to 'clientes' table...")
                connection.execute(text("ALTER TABLE clientes ADD COLUMN segmento_id UUID REFERENCES segmentos(id)"))
                connection.commit()
                print("Column added successfully.")
        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()

if __name__ == "__main__":
    add_segmento_column()
