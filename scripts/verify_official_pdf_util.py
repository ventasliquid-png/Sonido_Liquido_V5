import sys
import os

# Añadir el path del backend para poder importar el utility
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.utils.pdf import add_oc_label
from io import BytesIO

def verify():
    input_file = r"c:\dev\Sonido_Liquido_V5\data\30715603973_001_00001_00002429 Amazing.pdf"
    output_file = r"c:\dev\Sonido_Liquido_V5\data\FINAL_VERIFIED_OC.pdf"
    
    print(f"Procesando factura con el utilitario oficial...")
    
    with open(input_file, "rb") as f:
        processed_stream = add_oc_label(f.read(), "2563-CONFIRMADO")
    
    with open(output_file, "wb") as f:
        f.write(processed_stream.getbuffer())
        
    print(f"Archivo verificado generado en: {output_file}")

if __name__ == "__main__":
    verify()
