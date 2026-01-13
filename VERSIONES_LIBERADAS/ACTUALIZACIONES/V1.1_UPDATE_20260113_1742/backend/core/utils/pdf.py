import pikepdf
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
import os

def add_oc_label(input_pdf: BytesIO or bytes or str, oc_text: str, prefix: str = "OC") -> BytesIO:
    """
    Añade una etiqueta de OC/OV/PO en el cuadrante superior derecho (Opción A).
    
    Args:
        input_pdf: Stream de bytes, bytes crudos o path del PDF original.
        oc_text: El número de Orden de Compra/PO.
        prefix: El encabezado a usar (default: "OC").
        
    Returns:
        BytesIO: El PDF procesado.
    """
    # 1. Quitar restricciones y cargar PDF base
    if isinstance(input_pdf, str):
        with open(input_pdf, "rb") as f:
            input_bytes = BytesIO(f.read())
    elif isinstance(input_pdf, bytes):
        input_bytes = BytesIO(input_pdf)
    else:
        input_bytes = input_pdf

    with pikepdf.open(input_bytes) as pdf:
        temp_stream = BytesIO()
        pdf.save(temp_stream)
        temp_stream.seek(0)

    # 2. Crear la capa de texto (Overlay)
    packet = BytesIO()
    can = canvas.Canvas(packet)
    
    # IDENTIDAD: Dario Ponce (Production Supervisor) - Soluciones Farmacéuticas
    can.setFont("Helvetica-Bold", 8)
    can.setStrokeColorRGB(0.5, 0.5, 0.5)
    can.drawString(50, 20, "Production Supervisor: Dario Ponce (Soluciones Farmacéuticas)")

    # ETIQUETA OC/PO (Cuadrante Superior Derecho)
    can.setFont("Helvetica-Bold", 10)
    texto_final = f"{prefix}: {oc_text}"
    can.drawRightString(570, 808, texto_final)
    
    can.save()
    packet.seek(0)

    # 3. Fusionar capas usando pypdf
    overlay_pdf = PdfReader(packet)
    original_pdf = PdfReader(temp_stream)
    output_writer = PdfWriter()

    overlay_page = overlay_pdf.pages[0]
    
    # Iteramos sobre todas las páginas para no perder contenido (Ej: Facturas de >1 pág)
    for i, page in enumerate(original_pdf.pages):
        if i == 0:
            # Solo añadimos el label en la primera página
            page.merge_page(overlay_page)
        output_writer.add_page(page)

    # 4. Retornar stream de salida
    output_stream = BytesIO()
    output_writer.write(output_stream)
    output_stream.seek(0)
    
    return output_stream
