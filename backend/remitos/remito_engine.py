from fpdf import FPDF
import unittest
import os
from datetime import datetime
import textwrap
import qrcode
import tempfile

# Color Dominante: Azul Oscuro (#252b75) -> RGB (37, 43, 117)
COLOR_R = 37
COLOR_G = 43
COLOR_B = 117

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BG_IMAGE = os.path.join(BASE_DIR, "base_remito_v1.png")

class PDFRemito(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation, unit, format)
        self.is_preview = False
        self.copy_label = "ORIGINAL"
        self.copy_symbol = "*"
        self.remito_numero = None # Nuevo: Numero de Remito
        self.factura_vinculada = None # nuevo: Referencia a Factura
        self.vto_cae = None # nuevo: Vencimiento CAE
    
    def header(self):
        # 1. Background Image (Full Page)
        # Adjust path dynamically based on script location
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(current_dir, "base_remito_v1.png")
        
        if os.path.exists(bg_path):
            self.image(bg_path, x=0, y=0, w=210, h=297)
        
        # 2. Marca de Agua (VISTA PREVIA)
        if self.is_preview:
            self.set_font('Arial', 'B', 50)
            self.set_text_color(200, 200, 200)
            self.rotate(45, 105, 148)
            self.text(50, 190, "VISTA PREVIA - SIN VALIDEZ")
            self.rotate(0)
            
        # 3. Leyenda de Copia (Original, Dup, Trip)
        self.set_font('Arial', 'B', 10)
        self.set_text_color(COLOR_R, COLOR_G, COLOR_B)
        # 4. Numero de Remito (NUEVO)
        # 4. Numero de Remito (SIEMPRE MUESTRA EL NÚMERO DE REMITO/DOCUMENTO)
        # Posición: Caja Superior Derecha "REMITO Nº" (Y=25 por defecto)
        if self.remito_numero:
            self.set_xy(145, 25) 
            self.set_font('Arial', 'B', 16)
            self.set_text_color(COLOR_R, COLOR_G, COLOR_B)
            self.cell(50, 10, self.remito_numero, 0, 0, 'C')

            # [V5] Pseudo-Remito Logic (Factura Vinculada)
            if self.factura_vinculada:
                # Título Principal: "DOC. DE TRANSPORTE"
                current_y = self.get_y()
                self.set_y(15) 
                self.set_font('Arial', 'B', 14) 
                self.cell(0, 5, "DOC. DE TRANSPORTE", 0, 0, 'C')
                
                # Sub-bloque: "Corresponde a..." (Debajo del Remito Number)
                self.set_xy(130, 35) 
                self.set_font('Arial', '', 6) 
                self.cell(20, 6, "Corresponde a:", 0, 0, 'R') 
                
                self.set_font('Arial', 'B', 10) 
                self.cell(40, 6, str(self.factura_vinculada), 0, 0, 'L')

        # 5. Leyenda Vertical Izquierda (Sobre-escribir imagen)
        # Tapamos lo viejo (Extendemos desde el borde superior hasta abajo para asegurar limpieza)
        # Ancho 12mm para cubrir bien.
        self.set_fill_color(255, 255, 255)
        self.rect(0, 0, 12, 297, 'F') 
        
        # 6. TAPAR FLORCITA ORIGINAL (Si existe en la plantilla base)
        # Asumimos que está cerca del pie o donde pusimos los nuevos símbolos.
        # Creamos un parche blanco en la zona inferior central.
        self.rect(80, 270, 50, 20, 'F') 

        # Escribimos lo nuevo (Rotado)
        # Centrado verticalmente respecto al alto de la hoja (297mm / 2 = ~148mm)
        # Equidistante del margen físico (0) y borde dibujo (12) -> X=6 ? 
        # Pero rotate rota alrededor del origen dado.
        self.set_font('Arial', '', 8)
        self.set_text_color(COLOR_R, COLOR_G, COLOR_B)
        
        # Guardamos estado
        self.set_xy(8, 148) 
        # Rotamos 90 grados alrededor del centro aproximado
        # Ajuste manual: Text empieza en x,y. 
        # Probamos colocarlo centrado.
        with self.rotation(90, 6, 148):
            self.text(6, 148, f"* ORIGINAL   ** DUPLICADO   *** TRIPLICADO ({self.copy_label})")

        # 7. Símbolos Nuevos (ZapfDingbats)
        # "La estrella del original movela 2 posiciones a la derecha"
        # "y la hoja con 2 estrellas que queden equidistante... y la de 3 estrellas que quede la del medio a la misma altura que la del original"
        # INTERPRETACION: Mover el CENTRO del bloque de estrellas a la derecha.
        # Centro pagina = 105mm. Moveremos a 112mm (+7mm ~ 2 chars grandes).
        
        original_auto_page_break = self.auto_page_break
        self.set_auto_page_break(False)
        
        # Posición Y actual 275.
        # Usamos Cell con X especifico en lugar de 'C' pagina completa.
        NEW_CENTER_X = 112 
        SYMBOL_WIDTH = 20 # Ancho arbitrario para centrar texto dentro
        
        self.set_xy(NEW_CENTER_X - (SYMBOL_WIDTH/2), 275)
        self.set_font('ZapfDingbats', '', 24) 
        self.cell(SYMBOL_WIDTH, 10, self.copy_symbol, 0, 0, 'C')
        
        self.set_auto_page_break(original_auto_page_break, self.b_margin)

    def footer(self):
        # Pie de página manejado por coordenadas BAS (L60-62)
        pass

    def add_content(self, cliente_data, items):
        self.add_page()
        
        # --- CONFIGURACIÓN DE GRILLA BAS ---
        OFFSET_Y = 2  # Ajuste fino vertical top-margin
        OFFSET_X = 5  # Ajuste fino horizontal left-margin
        LH = 3.5      # Line Height
        CW = 2.2      # Char Width
        
        def set_bas_xy(line, col):
            x = OFFSET_X + (col * CW)
            y = OFFSET_Y + (line * LH)
            self.set_xy(x, y)

        # Configurar Fuente Principal
        self.set_text_color(0, 0, 0) # Negro
        self.set_font('Arial', 'B', 10) # Negrita para resaltar sobre fondo

        # --- ENCABEZADO ---
        
        # Fecha (L12, C71)
        set_bas_xy(12, 71) 
        fecha_str = datetime.now().strftime("%d/%m/%Y")
        self.cell(30, 6, fecha_str, 0)
        
        # Nombre (L18, C10)
        raw_nombre = str(cliente_data.get('razon_social', '')).upper()
        nombre_lines = textwrap.wrap(raw_nombre, 33)[:2] 
        
        for i, line_text in enumerate(nombre_lines):
            set_bas_xy(18 + i, 10)
            self.cell(80, 6, line_text, 0)
            
        # CUIT (L19, C52)
        set_bas_xy(19, 52)
        self.cell(40, 6, str(cliente_data.get('cuit', '')), 0)
        
        # IVA (L19, C71)
        set_bas_xy(19, 71) 
        cond_iva = str(cliente_data.get('condicion_iva', ''))
        if "INSCRIPTO" in cond_iva: cond_iva = "Resp. Inscripto"
        elif "CONSUMIDOR" in cond_iva: cond_iva = "Cons. Final"
        self.cell(40, 6, cond_iva, 0)

        # Domicilio (L20, C10)
        self.set_font('Arial', '', 8) 
        
        raw_dom = str(cliente_data.get('domicilio_fiscal', '')).upper().replace('SIN DOMICILIO FISCAL', '')
        if not raw_dom: raw_dom = str(cliente_data.get('domicilio', '')).upper()
        
        dom_lines = textwrap.wrap(raw_dom, 45)[:4] 
        
        last_dom_line_idx = 20
        for i, line_text in enumerate(dom_lines):
            set_bas_xy(20 + i, 10)
            self.cell(80, 5, line_text, 0)
            last_dom_line_idx = 20 + i
            
        # Ref (A facturar, Obs, Valor)
        ref = cliente_data.get('referencia', '')
        if ref:
             set_bas_xy(last_dom_line_idx + 4, 10)
             self.set_font('Arial', '', 6) 
             self.cell(100, 4, f"REF: {ref}", 0)
             
        self.set_font('Arial', 'B', 10) 

        # --- CUERPO (L31) ---
        Y_LIMIT = 58 
        current_line = 31
        
        self.set_font('Courier', '', 10) 
        
        for item in items:
            if current_line > Y_LIMIT: 
                self.add_page()
                current_line = 31
            
            # Cantidad (C4)
            set_bas_xy(current_line, 4)
            self.cell(15, 5, str(item.get('cantidad', '')), 0, 0, 'R')
            
            # Unidad (C16)
            set_bas_xy(current_line, 16)
            self.cell(10, 5, str(item.get('unidad', '')), 0)
            
            # Codigo (C20)
            set_bas_xy(current_line, 20)
            raw_code = str(item.get('codigo', ''))
            # Robust strip: SKU-, SKU , SKU (case insensitive)
            code_clean = raw_code.upper().replace('SKU-', '').replace('SKU ', '').replace('SKU', '').strip()
            self.cell(20, 5, code_clean, 0)
            
            # Descripcion (C28)
            set_bas_xy(current_line, 28)
            self.cell(100, 5, str(item.get('descripcion', '')), 0)
            
            current_line += 1.5

        # --- PIE DE PÁGINA (Observaciones, Valor, Bultos) ---
        # Se imprime siempre en la última página o donde caiga si hay espacio
        # Usamos filas 60+ (aprox 210mm)
        
        # Nota / Observaciones (C62 -> Y=219mm)
        set_bas_xy(60, 4) 
        self.set_font('Arial', 'B', 8)
        self.cell(20, 5, "NOTAS:", 0)
        
        set_bas_xy(60, 10)
        self.set_font('Arial', '', 8)
        obs_text = str(cliente_data.get('observaciones', ''))
        self.multi_cell(140, 4, obs_text, 0)
        
        # Valor Declarado y Bultos (C64 -> Y=226mm)
        set_bas_xy(64, 4)
        self.set_font('Arial', 'B', 8)
        self.cell(25, 5, "VALOR DECL.:", 0)
        
        set_bas_xy(64, 12)
        self.set_font('Arial', '', 8)
        val_text = str(cliente_data.get('valor_declarado', ''))
        self.cell(40, 5, val_text, 0)
        
        set_bas_xy(64, 25)
        self.set_font('Arial', 'B', 8)
        self.cell(20, 5, "BULTOS:", 0)
        
        set_bas_xy(64, 31)
        self.set_font('Arial', '', 8)
        bultos_text = str(cliente_data.get('bultos', ''))
        self.cell(20, 5, bultos_text, 0)

        # [V5] Invoice Link (Pie de Página Legal)
        # [V5] Invoice Link (Pie de Página Legal) + QR
        if self.factura_vinculada or self.remito_numero:
             # Generar QR si hay datos oficiales
             qr_str = f"https://www.afip.gob.ar/fe/qr/?p={self.remito_numero}" # Placeholder valid URL structure
             
             # Coords Pie
             Y_FOOTER = 275
             
             # QR Image
             try:
                 img = qrcode.make(qr_str)
                 temp_qr = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
                 img.save(temp_qr.name)
                 self.image(temp_qr.name, x=10, y=Y_FOOTER - 5, w=25, h=25)
                 temp_qr.close()
                 os.unlink(temp_qr.name)
             except Exception as e:
                 pass # Si falla QR, no rompe el PDF

             # Texto Legal
             # User Request V8: "X = 127"
             X_LEGALES = 127
             
             self.set_xy(X_LEGALES, Y_FOOTER)
             self.set_font('Arial', 'B', 10)
             if self.factura_vinculada:
                self.cell(0, 5, f"VINCULADO A FACTURA: {self.factura_vinculada}", 0, 1, 'L')
             
             self.set_x(X_LEGALES)
             self.set_font('Arial', '', 9)
             cae_txt = f"CAE: {cliente_data.get('cae', 'N/A')}"
             vto_txt = f"Vto. CAE: {self.vto_cae if self.vto_cae else 'N/A'}"
             self.cell(0, 5, f"{cae_txt}    -    {vto_txt}", 0, 1, 'L')
             
             self.set_x(X_LEGALES)
             self.set_font('Arial', 'I', 8)
             self.cell(0, 5, "Documento de Transporte amparado por Factura Electrónica.", 0, 1, 'L')

def generar_remito_pdf(cliente_data, items, is_preview=False, output_path="remito_final.pdf", numero_remito=None):
    """
    Genera el PDF con las 3 copias.
    numero_remito: string ej "0005-00000001"
    """
    pdf = PDFRemito()
    pdf.is_preview = is_preview
    if numero_remito:
        pdf.remito_numero = numero_remito
    
    # [V5] Pass Invoice Ref to PDF Object
    if cliente_data:
        if cliente_data.get('factura_vinculada'):
            pdf.factura_vinculada = cliente_data.get('factura_vinculada')
        if cliente_data.get('vto_cae'):
            pdf.vto_cae = cliente_data.get('vto_cae')
    
    # Definir Copias
    if is_preview:
        copias = [("VISTA PREVIA", "")]
    # Definir Copias
    if is_preview:
        copias = [("VISTA PREVIA", "")]
    else:
        # Usamos 'M' que en ZapfDingbats es una flor/asterisco (✲)
        copias = [
            ("ORIGINAL", "M"),
            ("DUPLICADO", "MM"),
            ("TRIPLICADO", "MMM")
        ]

    for label, symbol in copias:
        pdf.copy_label = label
        pdf.copy_symbol = symbol
        pdf.add_content(cliente_data, items)
        
    pdf.output(output_path)
    return output_path

class TestRemitoEngine(unittest.TestCase):
    def test_generacion_full(self):
        cli = {
            "razon_social": "LABORATORIO DE MEDICINA SOCIEDAD ANONIMA E INDUSTRIAL",
            "cuit": "30-58105030-1",
            "domicilio_fiscal": "TRELLES MANUEL R. 1566, CIUDAD AUTONOMA BUENOS AIRES (1416)",
            "condicion_iva": "RESPONSABLE INSCRIPTO",
            "referencia": "A FACTURAR"
        }
        items = [
            {"codigo": "1000", "descripcion": "TOALLA SUPER CORTA CAJA POR 2.500 U", "cantidad": 1, "unidad": "UN"}
        ]
        
        path_prev = generar_remito_pdf(cli, items, is_preview=True, output_path="test_preview_full.pdf", numero_remito="0005-00000001")
        self.assertTrue(os.path.exists(path_prev))

    def test_factura_masked(self):
        # Datos Reales extraidos de "factura_muestra.pdf" (GALAN SABRINA - 0001-00002487)
        cli = {
            "razon_social": "GALAN SABRINA",
            "cuit": "30-71560397-3", # CUIT from PDF? Wait, using 'SONIDO LIQUIDO' issuer data for client? No, client data. 
            # Reviewing extraction: "C.U.I.T.: 30-71560397-3" is visible in header, usually Issuer.
            # Client usually appears below. 
            # I will use generic client data but SPECIFIC INVOICE DATA as requested.
            "domicilio_fiscal": "DOMICILIO REAL DE PRUEBA",
            "condicion_iva": "RESPONSABLE INSCRIPTO",
            "factura_vinculada": "0001-00002487",
            "cae": "86073791502109",
            "vto_cae": "23/02/2026"
        }
        items = [
            {"codigo": "SURG-03", "descripcion": "Surgizime O3 botella 1 litro", "cantidad": 18, "unidad": "UN"},
            {"codigo": "SURG-BAC", "descripcion": "Surgibac PA botella 1 litro", "cantidad": 18, "unidad": "UN"}
        ]
        
        # Generamos PDF "Disfrazado" (V8 Real Data)
        # Remito Espejo: 0001-00002487 -> 0016-00002487
        path = generar_remito_pdf(cli, items, is_preview=False, output_path="test_factura_masked_v8.pdf", numero_remito="0016-00002487")
        self.assertTrue(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()
