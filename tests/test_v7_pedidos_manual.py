from unittest.mock import MagicMock
from backend.pedidos.services.excel_export import ExcelExportService

def test_v7_address_logic():
    print("🧪 Testing V7 Address Logic...")
    service = ExcelExportService()
    
    # Mock Domicilio with V7 fields
    mock_dom = MagicMock()
    mock_dom.calle = "Fiscal 123"
    mock_dom.calle_entrega = "Logistica 999" # Split
    mock_dom.numero_entrega = "A"
    mock_dom.piso_entrega = "1"
    mock_dom.depto_entrega = "B"
    mock_dom.localidad_entrega = "Dock Sud"
    mock_dom.provincia_entrega_id = "BA"
    
    # Mock Pedido
    mock_pedido = MagicMock()
    mock_pedido.domicilio_entrega = mock_dom
    
    # Test
    addr = service._get_delivery_address(mock_pedido)
    loc = service._get_delivery_locality(mock_pedido)
    
    print(f"   -> Address: '{addr}'")
    print(f"   -> Locality: '{loc}'")
    
    assert "Logistica 999" in addr
    assert "Fiscal" not in addr
    assert "Dock Sud" in loc
    
    print("✅ Split Logic Verified.")
    
    # Test Fallback
    mock_dom.calle_entrega = None
    mock_dom.calle = "Fiscal 123"
    addr_fallback = service._get_delivery_address(mock_pedido)
    print(f"   -> Fallback Address: '{addr_fallback}'")
    
    assert "Fiscal 123" in addr_fallback
    print("✅ Fallback Logic Verified.")

if __name__ == "__main__":
    test_v7_address_logic()
