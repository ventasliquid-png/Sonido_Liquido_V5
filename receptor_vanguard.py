import json
import sqlite3
import uuid
import os
from datetime import datetime, timezone

# --- CONFIGURACIÓN ---
RAR_JSON_PATH = r'c:\dev\RAR_V1\remito_borrador.json'
V5_DB_PATH = r'c:\dev\Sonido_Liquido_V5\pilot.db'

# --- MAPPINGS ---
IVA_MAPPING = {
    'RESPONSABLE INSCRIPTO': '966fdb33d6a64e499c81197790567dcb',
    'MONOTRIBUTISTA': '545951e74c1c4ea5a9e202a56128cc30',
    'EXENTO': '2415f0ea47ae43778d5634f76bca8d1b',
    'CONSUMIDOR FINAL': 'f9cb56f12b2c47169b0f7bed74196d4c',
    'NO RESPONSABLE': '63b406369d99455cbca237aa182baab9'
}

PROVINCIA_MAPPING = {
    'CIUDAD AUTONOMA BUENOS AIRES': 'CABA',
    'CAPITAL FEDERAL': 'CABA',
    'BUENOS AIRES': 'BA',
    'LA RIOJA': 'LR',
    'CORDOBA': 'CD',
    'SANTA FE': 'SF',
    'MENDOZA': 'MZ',
    'TUCUMAN': 'TU',
    'SALTA': 'SA',
    'ENTRE RIOS': 'ER',
    'CHACO': 'CH',
    # ...
}

def parse_rar_address(address_str):
    """
    Intenta desglosar: "DIRECCION, LOCALIDAD, PROVINCIA (CP)"
    """
    try:
        # Ejemplo: "TRELLES MANUEL R. 1566, CIUDAD AUTONOMA BUENOS AIRES, CIUDAD AUTONOMA BUENOS AIRES (1416)"
        # Nota: RAR a veces duplica CABA en localidad/provincia.
        
        # Primero extraemos el CP entre paréntesis
        cp = ""
        if "(" in address_str and ")" in address_str:
            cp = address_str.split("(")[-1].split(")")[0]
            address_str = address_str.split("(")[0].strip()
        
        parts = [p.strip() for p in address_str.split(",")]
        
        calle = parts[0] if len(parts) > 0 else "DESCONOCIDA"
        localidad = parts[1] if len(parts) > 1 else ""
        provincia_raw = parts[2] if len(parts) > 2 else (parts[1] if len(parts) > 1 else "")
        
        # Normalización de provincia
        prov_id = PROVINCIA_MAPPING.get(provincia_raw.upper(), 'CABA') # Default CABA por seguridad fiscal
        
        return calle, localidad, prov_id, cp
    except:
        return address_str, "", "CABA", ""

def ingest_vanguard():
    print("🚀 INICIANDO RECEPTOR VANGUARD...")
    
    if not os.path.exists(RAR_JSON_PATH):
        print(f"❌ Error: No se encuentra el archivo en {RAR_JSON_PATH}")
        return

    try:
        with open(RAR_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            cliente_rar = data.get('cliente')
    except Exception as e:
        print(f"❌ Error al leer JSON: {e}")
        return

    if not cliente_rar:
        print("❌ Error: Estructura de JSON inválida (falta 'cliente')")
        return

    cuit = str(cliente_rar.get('cuit'))
    razon_social = cliente_rar.get('razon_social')
    cond_iva_rar = cliente_rar.get('condicion_iva', '').upper()
    domicilio_str = cliente_rar.get('domicilio_fiscal', '')
    
    iva_id = IVA_MAPPING.get(cond_iva_rar, IVA_MAPPING['CONSUMIDOR FINAL'])
    calle, localidad, prov_id, cp = parse_rar_address(domicilio_str)

    print(f"📡 Procesando: {razon_social} (CUIT: {cuit})")

    conn = sqlite3.connect(V5_DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Buscar si el cliente ya existe
        cursor.execute("SELECT id FROM clientes WHERE cuit = ?", (cuit,))
        res = cursor.fetchone()
        
        if res:
            cliente_id = res[0]
            print(f"♻️ Actualizando cliente existente (ID: {cliente_id})")
            print("   [!] Doctrina de Virginidad: Preservando flags_estado.")
            cursor.execute("""
                UPDATE clientes SET 
                razon_social = ?, 
                condicion_iva_id = ?, 
                estado_arca = 'PENDIENTE_AUDITORIA',
                activo = 1,
                updated_at = ?
                WHERE id = ?
            """, (razon_social, iva_id, datetime.now(timezone.utc).isoformat(), cliente_id))
        else:
            cliente_id = str(uuid.uuid4().hex)
            print(f"✨ Insertando nuevo cliente 'Virgen Dorado' (ID: {cliente_id})")
            print("   [!] Doctrina de Virginidad: Asignando Flag 15.")
            cursor.execute("""
                INSERT INTO clientes (id, razon_social, cuit, condicion_iva_id, flags_estado, estado_arca, activo, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (cliente_id, razon_social, cuit, iva_id, 15, 'PENDIENTE_AUDITORIA', 1, 
                  datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat()))

        # 2. Manejar Domicilio Fiscal
        cursor.execute("SELECT id FROM domicilios WHERE cliente_id = ? AND es_fiscal = 1", (cliente_id,))
        res_dom = cursor.fetchone()
        
        if res_dom:
            print("🏠 Actualizando Domicilio Fiscal...")
            cursor.execute("""
                UPDATE domicilios SET 
                calle = ?, localidad = ?, provincia_id = ?, cp = ?, activo = 1
                WHERE id = ?
            """, (calle, localidad, prov_id, cp, res_dom[0]))
        else:
            print("🏠 Insertando Domicilio Fiscal...")
            dom_id = str(uuid.uuid4().hex)
            cursor.execute("""
                INSERT INTO domicilios (id, cliente_id, calle, localidad, provincia_id, cp, es_fiscal, es_entrega, activo)
                VALUES (?, ?, ?, ?, ?, ?, 1, 1, 1)
            """, (dom_id, cliente_id, calle, localidad, prov_id, cp))

        conn.commit()
        print(f"✅ INGESTIÓN EXITOSA. {razon_social} procesado por Receptor Vanguard.")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error durante la ingestión: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    ingest_vanguard()
