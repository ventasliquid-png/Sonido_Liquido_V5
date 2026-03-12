import psycopg2

def diagnostic():
    hosts = ['104.197.57.226']
    passwords = ['Spawn1482.', 'Spawn1482']
    
    for host in hosts:
        for pw in passwords:
            print(f"\n--- Testing Connection: {host} (Pass: {pw[:3]}***) ---")
            try:
                conn = psycopg2.connect(
                    host=host,
                    user='postgres',
                    password=pw,
                    dbname='postgres',
                    sslmode='require',
                    connect_timeout=10
                )
                print("✅ CONNECTED to 'postgres'!")
                
                cur = conn.cursor()
                
                # 1. List Databases
                print("\nDatabases:")
                cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
                dbs = cur.fetchall()
                for db in dbs:
                    print(f" - {db[0]}")
                
                # 2. List Tables in current (postgres)
                print("\nTables in 'postgres':")
                cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
                tables = cur.fetchall()
                for t in tables:
                    print(f" - {t[0]}")
                
                cur.close()
                conn.close()
                return # Stop if success
                
            except Exception as e:
                print(f"❌ Failed: {e}")

if __name__ == "__main__":
    diagnostic()
