
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

IOWA_HOST = "104.197.57.226"
IOWA_DB = "postgres"
USERS = ["postgres"]
PASSWORDS = ["SonidoV5_2025"]

def test_connections():
    print(f"--- [TEST CONEXION IOWA]: Probando {IOWA_HOST}... ---")
    
    for user in USERS:
        for pwd in PASSWORDS:
            try:
                conn = psycopg2.connect(
                    host=IOWA_HOST,
                    user=user,
                    password=pwd,
                    dbname=IOWA_DB,
                    sslmode='require',
                    connect_timeout=3
                )
                print(f"✅ CONEXION EXITOSA: user={user}, password={pwd}")
                conn.close()
                return
            except Exception as e:
                pass # Silent fail for bulk test
    print("❌ Todas las combinaciones fallaron.")

if __name__ == "__main__":
    test_connections()
