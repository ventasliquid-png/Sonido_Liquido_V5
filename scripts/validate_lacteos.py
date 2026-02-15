
import sys
import os
import json

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.clientes.services.afip_bridge import AfipBridgeService

CUIT_TARGET = "33660726859" # Lacteos de Poblet

print(f"--- VALIDANDO LÁCTEOS DE POBLET ({CUIT_TARGET}) ---")

try:
    # 1. Call Bridge (which uses updated rar_core.py)
    res = AfipBridgeService.get_datos_afip(CUIT_TARGET)
    
    if "error" in res:
        print(f"❌ ERROR: {res['error']}")
        sys.exit(1)
        
    print("\n✅ RESPUESTA ARCA RECIBIDA:")
    print(f"   Razón Social: {res.get('razon_social')}")
    print(f"   Condición IVA: {res.get('condicion_iva')}")
    print(f"   Domicilio Fiscal (Raw): {res.get('domicilio_fiscal')}")
    
    print(f"   Domicilio Fiscal (Raw): {res.get('domicilio_fiscal')}")
    
    # 2. Extract Parsed Address
    parsed = res.get('parsed_address', {})
    if parsed:
        print("\n   🔍 DOMICILIO INTELIGENTE (Detectado):")
        print(f"      Calle: {parsed.get('calle')}")
        print(f"      Piso:  {parsed.get('piso') or '---'}")
        print(f"      Depto: {parsed.get('depto') or '---'}")
        print(f"      Loc:   {parsed.get('localidad')}")
    else:
        print("\n   ⚠️ No se pudo parsear estructura fina del domicilio.")

except Exception as e:
    print(f"❌ EXCEPCION: {e}")
