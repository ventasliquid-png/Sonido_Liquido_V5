
import sqlite3
import sys

db_files = ["pilot.db", "sql_app.db"]
found_valid = False

for db_file in db_files:
    print(f"Checking {db_file}...")
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos_costos'")
        if not cursor.fetchone():
            print(f"  X Table productos_costos NOT found in {db_file}")
            conn.close()
            continue
            
        # Get columns
        cursor.execute("PRAGMA table_info(productos_costos)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "precio_fijo_override" in columns:
            print(f"  V VALID: 'precio_fijo_override' found in {db_file}")
            found_valid = True
        else:
            print(f"  X INVALID: 'precio_fijo_override' NOT found in {db_file}")
            print(f"    Existing columns: {columns}")
            
        conn.close()
    except Exception as e:
        print(f"  X Error checking {db_file}: {e}")

if found_valid:
    print("\nSUCCESS: Database integrity verified.")
    sys.exit(0)
else:
    print("\nFAILURE: No valid V5 database found.")
    sys.exit(1)
