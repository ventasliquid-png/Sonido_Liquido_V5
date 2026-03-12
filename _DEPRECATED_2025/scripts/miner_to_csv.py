import pdfplumber
import csv
import re
from pathlib import Path

# --- CONFIGURACIÓN ---
BASE_DIR = Path(__file__).resolve().parent.parent
PDF_DIR = BASE_DIR / "INGESTA_FACTURAS"
OUTPUT_CSV = BASE_DIR / "mineria_output.csv"

# TU CUIT (Para asegurarnos de no asignártelo a ti mismo por error)
CUIT_EMISOR = "30709383724"

def extract_data_from_pdf(pdf_path):
    """
    Extrae datos usando Lógica Posicional para Facturas AFIP.
    Estrategia: 
    1. Razón Social: Busca la etiqueta exacta.
    2. Domicilio: Toma el último encontrado (el primero es el tuyo).
    3. CUIT: Toma el segundo encontrado (el primero es el tuyo).
    """
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Leemos solo la primera página (donde están los datos)
            text = pdf.pages[0].extract_text()
    except Exception as e:
        print(f"[ERROR] No se pudo leer {pdf_path.name}: {e}")
        return None

    # 1. RAZÓN SOCIAL
    # Buscamos después de la etiqueta estándar de AFIP
    nombre_match = re.search(r"Apellido y Nombre / Razón Social:\s*(.+)", text)
    razon_social = nombre_match.group(1).strip() if nombre_match else "REVISAR_MANUAL"

    # 2. DOMICILIO 
    # AFIP pone "Domicilio Comercial" dos veces: arriba (emisor) y abajo (receptor).
    # Usamos findall y tomamos el ÚLTIMO de la lista.
    domicilios = re.findall(r"Domicilio Comercial:\s*(.+)", text)
    domicilio = "SIN_DATOS"
    
    if len(domicilios) > 1:
        domicilio = domicilios[-1].strip() # El último es el del cliente
    elif len(domicilios) == 1:
        domicilio = domicilios[0].strip()  # Por si acaso solo hay uno

    # 3. CUIT
    # Buscamos todos los patrones de CUIT (con o sin guiones)
    cuits = re.findall(r"CUIT:\s*(\d{11}|\d{2}-\d{8}-\d{1})", text)
    
    cuit_cliente = "SIN_DATOS"
    
    # Limpieza previa: quitamos guiones a todos para comparar
    cuits_limpios = [c.replace("-", "") for c in cuits]

    if len(cuits_limpios) >= 2:
        # LÓGICA DE ORO: En facturas A, el primer CUIT es el emisor, el segundo es el receptor.
        cuit_cliente = cuits_limpios[1]
    
    elif len(cuits_limpios) == 1:
        # Si solo encontró uno, verificamos que NO sea el tuyo
        if cuits_limpios[0] != CUIT_EMISOR:
             cuit_cliente = cuits_limpios[0]
        else:
             cuit_cliente = "ERROR_SOLO_EMISOR_DETECTADO"

    return {
        "razon_social": razon_social,
        "cuit": cuit_cliente,
        "condicion_iva": "RESPONSABLE INSCRIPTO", # Default seguro
        "domicilio": domicilio,
        "archivo_origen": pdf_path.name
    }

def main():
    print(f"--- MINERÍA A CSV (V3 Posicional) DESDE: {PDF_DIR} ---")
    
    if not PDF_DIR.exists():
        print("ERROR: No existe la carpeta INGESTA_FACTURAS")
        return

    archivos = list(PDF_DIR.glob("*.pdf"))
    print(f"Detectados {len(archivos)} documentos.")

    # Escribimos el CSV
    # Usamos punto y coma (;) que es mejor para Excel en español
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = ['razon_social', 'cuit', 'condicion_iva', 'domicilio', 'archivo_origen']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=';')
        
        writer.writeheader()
        
        count = 0
        for pdf in archivos:
            data = extract_data_from_pdf(pdf)
            if data:
                # Advertencia visual en consola si falta algo crítico
                if data['razon_social'] == "REVISAR_MANUAL" or "ERROR" in data['cuit']:
                    print(f"[WARN] Revisar manualmente: {pdf.name}")
                
                writer.writerow(data)
                count += 1
                print(f"[CSV] Procesado: {pdf.name}")

    print(f"\n--- ÉXITO ---")
    print(f"Se generó el archivo: {OUTPUT_CSV}")
    print(f"Total filas procesadas: {count}")
    print("INSTRUCCIÓN: Abrir en Excel -> Datos -> Texto en columnas -> Delimitador ';'")
    print("IMPORTANTE: Formatear columna CUIT como 'Texto' para evitar notación científica.")

if __name__ == "__main__":
    main()