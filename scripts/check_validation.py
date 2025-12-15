
import sys
import os
import sqlite3
import datetime
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, ValidationError

# Try to use the REAL schemas from the backend to test the actual code state
# Append root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.clientes.schemas import ClienteListResponse
    print("IMPORTED REAL SCHEMA successfully.")
except Exception as e:
    print(f"COULD NOT IMPORT SCHEMA: {e}")
    sys.exit(1)

# Connect to DB
db_path = os.path.join(os.path.dirname(__file__), '..', 'pilot.db')
print(f"Connecting to {db_path}")
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT * FROM clientes")
rows = cursor.fetchall()

print(f"Found {len(rows)} clients in DB.")

errors = []
for row in rows:
    data = dict(row)
    # Convert 'id' and UUID fields to UUID objects if string by checking keys ending in _id or being 'id'
    # Actually Pydantic (V2 or V1) often handles string to UUID coercion automatically, but let's be safe if it doesn't
    # In SQLite they are stored as strings.
    
    # We will pass the dict directly. If Pydantic fails on string-uuid, we'll know.
    
    try:
        # Pydantic model validation
        ClienteListResponse.model_validate(data) # V2 syntax? or valid for V1 if configured
    except AttributeError:
        # Fallback to V1
        ClienteListResponse(**data)
    except ValidationError as e:
        errors.append(f"Client {data.get('razon_social', 'Unknown')} (ID: {data.get('id')}): {e}")

if not errors:
    print("SUCCESS: All clients validated correctly.")
else:
    print(f"FAILURE: {len(errors)} validation errors found.")
    for err in errors[:10]:
        print(err)

conn.close()
