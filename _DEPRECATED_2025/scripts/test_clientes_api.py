import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token():
    print("--- Autenticando Usuario Admin ---")
    url = f"{BASE_URL}/auth/token"
    payload = {
        "username": "admin",
        "password": "admin123"
    }
    try:
        response = requests.post(url, data=payload) # OAuth2 form data
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Token obtenido exitosamente.")
            return token
        else:
            print(f"❌ Error de autenticación: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción al autenticar: {e}")
        return None

def test_clientes_crud():
    token = get_auth_token()
    if not token:
        return False
        
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n--- Iniciando Test de Integración: API Clientes ---")
    
    # 0. Obtener Maestros (IDs dinámicos)
    print("0. Obteniendo IDs de maestros...")
    try:
        resp_iva = requests.get(f"{BASE_URL}/maestros/condiciones-iva")
        condicion_iva_id = resp_iva.json()[0]["id"]
        print(f"   - CondicionIVA ID: {condicion_iva_id}")

        resp_lp = requests.get(f"{BASE_URL}/maestros/listas-precios")
        lista_precios_id = resp_lp.json()[0]["id"]
        print(f"   - ListaPrecios ID: {lista_precios_id}")
    except Exception as e:
        print(f"❌ Error al obtener maestros: {e}")
        return False

    import random
    random_cuit = f"20-{random.randint(10000000, 99999999)}-{random.randint(0, 9)}"
    
    # 1. Crear Cliente
    payload = {
        "razon_social": f"Test Cliente Automático {random.randint(1000, 9999)}",
        "cuit": random_cuit,
        "legacy_id_bas": "LEGACY-001",
        "whatsapp_empresa": "+5491155556666",
        "web_portal_pagos": "https://portal.ejemplo.com",
        "datos_acceso_pagos": "User: admin / Pass: 1234",
        "condicion_iva_id": condicion_iva_id,
        "lista_precios_id": lista_precios_id,
        "activo": True,
        "domicilios": [
            {
                "calle": "Calle Falsa",
                "numero": "123",
                "localidad": "Springfield",
                "provincia": "C", # ID Provincia CABA
                "es_fiscal": True
            }
        ],
        "contactos": [] 
    }
    
    print(f"\n1. Creando cliente: {payload['razon_social']} (CUIT: {payload['cuit']})...")
    try:
        response = requests.post(f"{BASE_URL}/clientes/", json=payload, headers=headers)
        if response.status_code != 201:
            print(f"❌ Error al crear cliente: {response.status_code} - {response.text}")
            return False
        
        cliente = response.json()
        cliente_id = cliente["id"]
        codigo_interno = cliente.get("codigo_interno")
        print(f"✅ Cliente creado con ID: {cliente_id} | Código Interno: {codigo_interno}")
        
        if codigo_interno is None:
             print("❌ Error: No se generó codigo_interno")
        
        # Verificar datos anidados
        if len(cliente["domicilios"]) > 0:
            print(f"   - Domicilio creado: {cliente['domicilios'][0]['calle']} {cliente['domicilios'][0]['numero']}")
        else:
            print("❌ Error: No se crearon domicilios")
            
    except Exception as e:
        print(f"❌ Excepción crítica al crear: {e}")
        return False

    # 2. Leer Cliente
    print(f"\n2. Leyendo cliente ID: {cliente_id}...")
    response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
    if response.status_code == 200:
        print("✅ Cliente recuperado correctamente.")
    else:
        print(f"❌ Error al leer cliente: {response.status_code}")
        return False

    # 3. Actualizar Cliente
    update_payload = {
        "razon_social": "Test Cliente Modificado"
    }
    print(f"\n3. Actualizando cliente (Razón Social -> {update_payload['razon_social']})...")
    response = requests.put(f"{BASE_URL}/clientes/{cliente_id}", json=update_payload, headers=headers)
    if response.status_code == 200:
        updated_cliente = response.json()
        if updated_cliente["razon_social"] == "Test Cliente Modificado":
            print("✅ Cliente actualizado correctamente.")
        else:
            print(f"❌ Error: El nombre no cambió. Recibido: {updated_cliente['razon_social']}")
    else:
        print(f"❌ Error al actualizar: {response.status_code}")
        return False

    # 4. Borrar Cliente
    print(f"\n4. Borrando cliente ID: {cliente_id}...")
    response = requests.delete(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
    if response.status_code == 200:
        print("✅ Cliente borrado (soft-delete o físico según implementación).")
    else:
        print(f"❌ Error al borrar: {response.status_code}")
        return False

    # 5. Verificar Borrado
    print(f"\n5. Verificando estado post-borrado...")
    response = requests.get(f"{BASE_URL}/clientes/{cliente_id}", headers=headers)
    if response.status_code == 200:
        final_cliente = response.json()
        if final_cliente.get("activo") is False:
             print("✅ Verificación Exitosa: Cliente marcado como inactivo (Soft Delete).")
        else:
             print("⚠️ Advertencia: El cliente sigue activo o no tiene campo 'activo'.")
    elif response.status_code == 404:
        print("✅ Verificación Exitosa: Cliente eliminado físicamente.")
    else:
        print(f"⚠️ Estado inesperado: {response.status_code}")

    print("\n--- ✅ TEST FINALIZADO CON ÉXITO ---")
    return True

if __name__ == "__main__":
    success = test_clientes_crud()
    sys.exit(0 if success else 1)
