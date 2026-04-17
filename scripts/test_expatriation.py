import requests
import os
import sqlite3
import glob

BASE_URL = "http://localhost:8080/productos"

def test_expatriation():
    print("--- INICIANDO TEST DE EXPATRIACIÓN V5.9 ---")
    
    import time
    ts = int(time.time())
    res = requests.post(f"{BASE_URL}/rubros", json={
        "codigo": f"T{str(ts)[-2:]}",
        "nombre": f"EXILE_TEST_{ts}",
        "activo": True
    })
    if res.status_code != 200:
        print(f"[FAIL] Error creando rubro: {res.status_code} - {res.text}")
        return
    rubro = res.json()
    rubro_id = rubro['id']
    print(f"[OK] Rubro creado: {rubro_id}")

    # 2. Crear Producto en ese Rubro
    res = requests.post(f"{BASE_URL}", json={
        "sku": int(time.time()) % 1000000,
        "nombre": "PRODUCTO_EXILIADO_TEST",
        "rubro_id": rubro_id,
        "activo": True,
        "flags_estado": 1,
        "costos": {
            "costo_reposicion": 100.0,
            "precio_roca": 150.0
        }
    })
    if res.status_code != 200:
        print(f"[FAIL] Error creando producto: {res.status_code} - {res.text}")
        return
    producto = res.json()
    prod_id = producto['id']
    print(f"[OK] Producto creado: {prod_id}")

    # 3. Borrar Rubro (Disparar Exilio)
    print(f"[ACTION] Borrando rubro {rubro_id}...")
    res = requests.delete(f"{BASE_URL}/rubros/{rubro_id}")
    print(f"[OK] Status delete: {res.status_code}")

    # 4. Verificación en DB
    conn = sqlite3.connect('pilot_v5x.db')
    cursor = conn.cursor()
    
    # Check Producto
    cursor.execute("SELECT rubro_id, flags_estado FROM productos WHERE id = ?", (prod_id,))
    p_data = cursor.fetchone()
    print(f"[CHECK] Producto flag post-exilio: {p_data[1]} (Bit 3/8 debería estar ON)")
    print(f"[CHECK] Producto rubro post-exilio: {p_data[0]} (Debería ser ID de 'General')")
    
    # Check Rubro (Baneado Bit 2 / 4)
    cursor.execute("SELECT activo, flags_estado FROM rubros WHERE id = ?", (rubro_id,))
    r_data = cursor.fetchone()
    print(f"[CHECK] Rubro activo: {r_data[0]}, Flag: {r_data[1]} (4 esperado)")
    
    conn.close()

    # 5. Verificar CSV
    csv_files = glob.glob(f"exports/exilio_rubro_{rubro_id}_*.csv")
    if csv_files:
        print(f"[OK] Manifiesto encontrado: {csv_files[0]}")
        with open(csv_files[0], 'r') as f:
            print("--- CONTENIDO MANIFIESTO ---")
            print(f.read())
    else:
        print("[ERROR] No se encontró el manifiesto CSV.")

if __name__ == "__main__":
    test_expatriation()
