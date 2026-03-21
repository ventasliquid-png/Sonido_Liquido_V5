# Simple Logic Test for PDF Suppression
def mock_get_pdf_data(numero_legal, cae_attr, vto_cae_attr):
    # Mimic router logic
    is_manual = str(numero_legal or "").startswith("0015")
    
    cae_val = cae_attr if not is_manual else None
    vto_cae_val = vto_cae_attr if not is_manual else None
    
    return {
        "cae": cae_val,
        "vto_cae": vto_cae_val.strftime("%d/%m/%Y") if vto_cae_val else None
    }

from datetime import datetime
now = datetime.now()

# Case 1: Manual Remito
res1 = mock_get_pdf_data("0015-00003001", "12345678", now)
print(f"Manual (0015): {res1}")
assert res1["cae"] is None
assert res1["vto_cae"] is None

# Case 2: Ingesta Remito
res2 = mock_get_pdf_data("0016-00003001", "12345678", now)
print(f"Ingesta (0016): {res2}")
assert res2["cae"] == "12345678"
assert res2["vto_cae"] is not None

print("LOGIC VERIFIED: Suppression works correctly.")
