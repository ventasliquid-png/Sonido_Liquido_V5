import sys
import os

# Add the parent directory to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import inspect, text
from backend.core.database import engine

def remove_cuit_constraint():
    inspector = inspect(engine)
    table_name = 'clientes'
    
    print(f"Inspecting table '{table_name}'...")
    
    # Check Constraints
    unique_constraints = inspector.get_unique_constraints(table_name)
    cuit_constraint = None
    for constraint in unique_constraints:
        if 'cuit' in constraint['column_names']:
            cuit_constraint = constraint['name']
            break
    
    if cuit_constraint:
        print(f"Found unique constraint on 'cuit': {cuit_constraint}")
        with engine.connect() as connection:
            try:
                print(f"Dropping constraint '{cuit_constraint}'...")
                connection.execute(text(f"ALTER TABLE {table_name} DROP CONSTRAINT {cuit_constraint}"))
                connection.commit()
                print("Constraint dropped successfully.")
            except Exception as e:
                print(f"Error dropping constraint: {e}")
    else:
        print("No unique constraint found on 'cuit'. Checking indexes...")

    # Check Indexes
    indexes = inspector.get_indexes(table_name)
    cuit_index = None
    for index in indexes:
        if 'cuit' in index['column_names'] and index['unique']:
            cuit_index = index['name']
            break
            
    if cuit_index:
        print(f"Found unique index on 'cuit': {cuit_index}")
        with engine.connect() as connection:
            try:
                print(f"Dropping index '{cuit_index}'...")
                connection.execute(text(f"DROP INDEX {cuit_index}"))
                connection.commit()
                print("Index dropped successfully.")
            except Exception as e:
                print(f"Error dropping index: {e}")
    else:
        print("No unique index found on 'cuit'.")

if __name__ == "__main__":
    remove_cuit_constraint()
