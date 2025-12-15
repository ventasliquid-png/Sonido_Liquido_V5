
import psycopg2
from urllib.parse import quote_plus

def check_iowa():
    # Credentials from database.py hardcode
    host = "104.197.57.226"
    user = "postgres"
    password = "Spawn1482."
    dbname = "postgres"
    
    print(f"Connecting to IOWA ({host})...")
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
            sslmode='require',
            connect_timeout=10 
        )
        cursor = conn.cursor()
        
        # Check Clientes
        try:
            cursor.execute("SELECT count(*) FROM clientes")
            origen_count = cursor.fetchone()[0]
            print(f"IOWA CLIENTES: {origen_count}")
            
            if origen_count > 0:
                print("Retrieving sample names...")
                cursor.execute("SELECT razon_social, created_at FROM clientes ORDER BY created_at DESC LIMIT 5")
                for row in cursor.fetchall():
                    print(f" - {row[0]} ({row[1]})")
        except Exception as e:
            print(f"Error querying clientes: {e}")

        conn.close()
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")

if __name__ == "__main__":
    check_iowa()
