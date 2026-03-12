import sqlite3
import psycopg2

def audit_schemas_detailed():
    print("--- 🔬 AUDITORÍA DETALLADA DE TIPOS (Local vs IOWA) ---")
    
    # Cloud
    try:
        conn_c = psycopg2.connect(host='104.197.57.226', user='postgres', password='SonidoV5_2025', dbname='postgres', sslmode='require')
        cur_c = conn_c.cursor()
        for t in ['rubros', 'productos', 'clientes']:
            cur_c.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{t}'")
            cols = cur_c.fetchall()
            print(f"Cloud {t.upper()} Types: {cols}")
        conn_c.close()
    except Exception as e:
        print(f"Error Cloud: {e}")

    # Local
    try:
        conn_l = sqlite3.connect('pilot.db')
        cur_l = conn_l.cursor()
        for t in ['rubros', 'productos', 'clientes']:
            cur_l.execute(f"PRAGMA table_info({t})")
            cols = [(c[1], c[2]) for c in cur_l.fetchall()]
            print(f"Local {t.upper()} Types: {cols}")
        conn_l.close()
    except Exception as e:
        print(f"Error Local: {e}")

if __name__ == "__main__":
    audit_schemas_detailed()
