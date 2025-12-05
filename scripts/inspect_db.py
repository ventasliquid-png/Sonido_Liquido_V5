import psycopg2
import os

# Connection details from backend/core/database.py
DB_HOST = "34.95.172.190"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "e"

def inspect_db():
    try:
        print(f"Connecting to {DB_HOST}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        
        # Check version
        cur.execute("SELECT version();")
        print(f"Version: {cur.fetchone()[0]}")
        
        # Check extensions
        print("\nExtensions:")
        cur.execute("SELECT extname, extversion FROM pg_extension;")
        for row in cur.fetchall():
            print(f"- {row[0]} (v{row[1]})")
            
        # List tables
        print("\nTables:")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cur.fetchall()
        
        for table in tables:
            table_name = table[0]
            # Count rows
            cur.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cur.fetchone()[0]
            print(f"- {table_name}: {count} rows")
            
            # Check columns for atenea_memory to see structure
            if table_name == 'atenea_memory':
                print("  Columns:")
                cur.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table_name}';")
                for col in cur.fetchall():
                    print(f"    - {col[0]}: {col[1]}")

        conn.close()
        print("\nInspection complete.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_db()
