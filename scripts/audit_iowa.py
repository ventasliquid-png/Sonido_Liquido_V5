
import psycopg2
from urllib.parse import quote_plus

# Credentials found in backend/core/database.py
import os
HOST = "104.197.57.226"
USER = "postgres"
PASS = os.getenv('DB_PASSWORD')
DB_NAME = "postgres"

def audit_db():
    print(f"--- IOWA AUDIT: Connecting to {HOST} ---")
    try:
        conn = psycopg2.connect(
            host=HOST,
            user=USER,
            password=PASS,
            dbname=DB_NAME,
            sslmode='require' 
        )
        print("✅ Connection Successful!")
        
        cur = conn.cursor()
        
        # 1. List Tables
        print("\n--- TABLES ---")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cur.fetchall()
        
        if not tables:
            print("No tables found in 'public' schema.")
        
        for table in tables:
            t_name = table[0]
            # 2. Count Rows
            cur.execute(f"SELECT COUNT(*) FROM {t_name}")
            count = cur.fetchone()[0]
            print(f"- {t_name}: {count} rows")
            
            # 3. Sample Data (First 3 rows)
            # cur.execute(f"SELECT * FROM {t_name} LIMIT 3")
            # rows = cur.fetchall()
            # for r in rows:
            #     print(f"  Sample: {r}")
                
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    audit_db()
