
import psycopg2
import pandas as pd

def list_iowa_clients():
    import os
    host = "104.197.57.226"
    user = "postgres"
    password = os.getenv('DB_PASSWORD')
    dbname = "postgres"
    
    try:
        conn = psycopg2.connect(host=host, user=user, password=password, dbname=dbname, sslmode='require')
        df = pd.read_sql("SELECT razon_social, cuit, created_at FROM clientes ORDER BY created_at DESC", conn)
        print(f"IOWA Clients ({len(df)}):")
        print(df.to_string())
        conn.close()
    except Exception as e:
        print(e)

if __name__ == "__main__":
    list_iowa_clients()
