
import sqlite3
import os

db_path = r'c:\dev\Sonido_Liquido_V5\pilot.db'

if not os.path.exists(db_path):
    print(f"ERROR: Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Database: {db_path}")
    print(f"Size: {os.path.getsize(db_path)} bytes")
    print("-" * 30)
    print(f"{'Table':<30} | {'Rows':<10}")
    print("-" * 30)
    
    for table_name in tables:
        table = table_name[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{table:<30} | {count:<10}")
        except Exception as e:
            print(f"{table:<30} | ERROR: {e}")
            
    conn.close()
    
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
