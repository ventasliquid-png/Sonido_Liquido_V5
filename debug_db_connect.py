
import psycopg2
import sys

# Define credentials WITH THE DOT (matching .env)
HOST = "104.197.57.226"
PORT = "5432"
USER = "postgres"
DB = "postgres"
PASSWORD = "Spawn1482." 

print(f"--- TESTING CONNECTION (FINAL CHECK) ---")
print(f"Target: {USER}@{HOST}:{PORT}/{DB}")
print(f"Password: '{PASSWORD}' (Len: {len(PASSWORD)})")

try:
    conn = psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DB,
        sslmode="require"
    )
    print("✅ SUCCESS! Connected successfully.")
    conn.close()
    sys.exit(0)
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)
