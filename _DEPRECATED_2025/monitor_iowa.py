
import psycopg2
import time
from datetime import datetime

def monitor_iowa():
    import os
    host = "104.197.57.226"
    user = "postgres"
    password = os.getenv('DB_PASSWORD')
    dbname = "postgres"
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring IOWA connection...")
    
    while True:
        try:
            conn = psycopg2.connect(
                host=host, 
                user=user, 
                password=password, 
                dbname=dbname, 
                sslmode='require', 
                connect_timeout=3
            )
            print(f"\n✅ [{datetime.now().strftime('%H:%M:%S')}] CONNECTION SUCCESSFUL!")
            
            cursor = conn.cursor()
            cursor.execute("SELECT count(*) FROM clientes")
            count = cursor.fetchone()[0]
            print(f"   Remote Clientes Count: {count}")
            conn.close()
            break
        except Exception as e:
            # Short error msg
            err = str(e).split('\n')[0]
            print(f".", end="", flush=True)
            time.sleep(5)

if __name__ == "__main__":
    monitor_iowa()
