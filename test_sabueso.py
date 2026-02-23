import fitz  # Esta es la librería PyMuPDF que ya tenés en tu disco

def probar_sabueso_local(ruta_al_pdf):
    try:
        # 1. Abrir el documento
        doc = fitz.open(ruta_al_pdf)
        
        # 2. Leer la primera página (donde suele estar toda la info de ARCA)
        pagina = doc[0]
        
        # 3. Extraer el texto crudo
        texto = pagina.get_text()
        
        print("\n" + "="*40)
        print("📊 REPORTE DE EXTRACCIÓN SOBERANA")
        print("="*40)
        print(texto) # Aquí vas a ver toda la "sopa de letras"
        print("="*40 + "\n")
        
        doc.close()
    except Exception as e:
        print(f"❌ Error al leer el PDF: {e}")

# --- CAMBIÁ ESTO ---
# Poné la ruta de un PDF real que tengas en tu computadora
ruta_real = r"C:\Users\USUARIO\Downloads/30715603973_001_00001_00002489 (1).pdf" 
probar_sabueso_local(ruta_real)