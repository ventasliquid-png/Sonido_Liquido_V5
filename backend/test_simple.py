import psycopg2
import time

# TUS DATOS (Confirmados por lo que vimos hoy)
HOST = "34.95.172.190"  # La IP del "Micro"
DB = "postgres"         # Base default
USER = "postgres"
PASS = "SonidoV5_2025"  # <--- OJO: Poné la clave real

print(f"--- INICIANDO PRUEBA DE CONEXIÓN A {HOST} ---")
print("Intentando golpear la puerta 5432...")

start = time.time()
try:
    # Intentamos conectar con un timeout corto para que no te duermas esperando
    conn = psycopg2.connect(
        host=HOST,
        database=DB,
        user=USER,
        password=PASS,
        connect_timeout=10, 
        sslmode='require' # Google suele pedir SSL
    )
    
    print("\n✅ ¡MILAGRO! ¡CONECTÓ!")
    print("Si ves esto, el problema era alguna config de Gy, no la red.")
    
    # Preguntamos algo simple
    cur = conn.cursor()
    cur.execute("SELECT current_timestamp;")
    hora = cur.fetchone()[0]
    print(f"Hora del servidor: {hora}")
    
    conn.close()

except psycopg2.OperationalError as e:
    print("\n❌ REBOTAMOS (Error Operativo)")
    print("Esto confirma bloqueo de RED (ISP o Firewall).")
    print(f"Detalle: {e}")

except Exception as e:
    print(f"\n❌ OTRO ERROR: {e}")

print(f"\nTiempo transcurrido: {round(time.time() - start, 2)} segundos.")