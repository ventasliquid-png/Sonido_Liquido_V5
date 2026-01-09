import psycopg2
import sys

def test_password(pw):
    host = '104.197.57.226'
    user = 'postgres'
    db = 'postgres'
    print(f"Testing password: {pw}")
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=pw,
            dbname=db,
            sslmode='require',
            connect_timeout=10
        )
        print(f"✅ SUCCESS: {pw}")
        
        cur = conn.cursor()
        cur.execute("SELECT count(*) FROM productos")
        p_count = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM clientes")
        c_count = cur.fetchone()[0]
        print(f"   IOWA Data: {p_count} products, {c_count} clients")
        
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False

if __name__ == "__main__":
    passwords = ['SonidoV5_2025', 'Spawn1482.', 'Spawn1482']
    success = False
    for p in passwords:
        if test_password(p):
            success = True
            break
    
    if not success:
        sys.exit(1)
