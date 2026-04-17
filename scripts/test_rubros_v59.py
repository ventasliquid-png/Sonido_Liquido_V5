import requests
import json

BASE_URL = "http://localhost:8080/productos"

def test_rubro_upgrade():
    # 1. Crear Rubro
    payload = {
        "codigo": "G99",
        "nombre": "PRUEBA_V59_UPGRADE",
        "activo": True
    }
    
    print("--- 1. CREANDO RUBRO ---")
    res = requests.post(f"{BASE_URL}/rubros", json=payload)
    if res.status_code != 200:
        print("Fallo creación:", res.text)
        return
        
    rubro = res.json()
    rubro_id = rubro['id']
    print(f"Creado ID: {rubro_id}")

    # 2. Verificar existencia en lista
    print("--- 2. VERIFICANDO EN LISTA ---")
    res = requests.get(f"{BASE_URL}/rubros")
    found = any(r['id'] == rubro_id for r in res.json())
    print(f"Encontrado en lista: {found}")

    # 3. Eliminar (Upgrade Borrado Lógico)
    print("--- 3. ELIMINANDO (BORRADO LÓGICO V5.9) ---")
    res = requests.delete(f"{BASE_URL}/rubros/{rubro_id}")
    print(f"Delete status: {res.status_code}")

    # 4. Verificar ausencia en lista
    print("--- 4. VERIFICANDO AUSENCIA EN LISTA ---")
    res = requests.get(f"{BASE_URL}/rubros")
    found = any(r['id'] == rubro_id for r in res.json())
    print(f"Encontrado post-delete: {found}")
    
    # 5. Verificación física (flags_estado en DB)
    print("--- 5. VERIFICACIÓN FÍSICA DB ---")
    import os
    from sqlalchemy import create_engine, text
    DB_PATH = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"
    url = f"sqlite:///{DB_PATH}".replace('\\', '/')
    engine = create_engine(url)
    with engine.connect() as conn:
        db_res = conn.execute(text("SELECT flags_estado FROM rubros WHERE id = :id"), {"id": rubro_id}).fetchone()
        if db_res:
            print(f"Flags en DB: {db_res[0]} (Esperado: 4)")
        else:
            print("Registro NO encontrado en DB (Error: debería existir pero estar oculto)")

if __name__ == "__main__":
    test_rubro_upgrade()
