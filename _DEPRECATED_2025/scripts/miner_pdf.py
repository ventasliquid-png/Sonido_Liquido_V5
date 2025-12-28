def extract_data_from_pdf(pdf_path):
    """Extrae datos usando Lógica Posicional (El Cliente es el 2do CUIT)."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = pdf.pages[0].extract_text()
    except Exception as e:
        return None

    # 1. RAZÓN SOCIAL
    nombre_match = re.search(r"Apellido y Nombre / Razón Social:\s*(.+)", text)
    razon_social = nombre_match.group(1).strip() if nombre_match else "REVISAR_MANUAL"

    # 2. DOMICILIO (Tomamos el último encontrado, suele ser el del receptor)
    domicilios = re.findall(r"Domicilio Comercial:\s*(.+)", text)
    domicilio = "SIN_DATOS"
    if len(domicilios) > 0:
        domicilio = domicilios[-1].strip()

    # 3. CUIT (CORRECCIÓN: TOMAR SIEMPRE EL SEGUNDO)
    # Buscamos todos los CUITs en la página
    cuits = re.findall(r"CUIT:\s*(\d{11}|\d{2}-\d{8}-\d{1})", text)
    
    cuit_cliente = "SIN_DATOS"
    
    if len(cuits) >= 2:
        # Si hay al menos 2, el segundo (índice 1) es el Cliente 
        cuit_cliente = cuits[1].replace("-", "")
    elif len(cuits) == 1:
        # Si hay solo uno, verificamos que NO sea el tuyo
        c_encontrado = cuits[0].replace("-", "")
        if "30709383724" not in c_encontrado:
             cuit_cliente = c_encontrado
        else:
             cuit_cliente = "REVISAR_MANUAL_SOLO_EMISOR"

    return {
        "razon_social": razon_social,
        "cuit": cuit_cliente,
        "condicion_iva": "RESPONSABLE INSCRIPTO",
        "domicilio": domicilio,
        "archivo_origen": pdf_path.name
    }