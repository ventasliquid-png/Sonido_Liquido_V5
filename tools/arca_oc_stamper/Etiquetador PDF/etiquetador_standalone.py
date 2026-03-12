import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from io import BytesIO

# --- MOTOR PDF (INCORPORADO PARA PORTABILIDAD) ---
try:
    import pikepdf
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
except ImportError:
    # No fallar al importar, manejaremos el error si no están instaladas
    pass

def add_oc_label_standalone(input_pdf_bytes: bytes, oc_text: str, prefix: str = "OC") -> BytesIO:
    """Añade la etiqueta OC en el PDF (Logic extracted from Core V5)"""
    # 1. Quitar restricciones y cargar PDF
    input_bytes = BytesIO(input_pdf_bytes)
    with pikepdf.open(input_bytes) as pdf:
        temp_stream = BytesIO()
        pdf.save(temp_stream)
        temp_stream.seek(0)

    # 2. Crear capa de texto
    packet = BytesIO()
    can = canvas.Canvas(packet)
    
    # Identidad funcional
    can.setFont("Helvetica-Bold", 8)
    can.setStrokeColorRGB(0.5, 0.5, 0.5)
    can.drawString(50, 20, "Production Supervisor: Dario Ponce (Soluciones Farmacéuticas)")

    # Etiqueta
    can.setFont("Helvetica-Bold", 10)
    texto_final = f"{prefix}: {oc_text}"
    can.drawRightString(570, 808, texto_final)
    
    can.save()
    packet.seek(0)

    # 3. Fusionar
    overlay_pdf = PdfReader(packet)
    original_pdf = PdfReader(temp_stream)
    output_writer = PdfWriter()

    overlay_page = overlay_pdf.pages[0]
    for i, page in enumerate(original_pdf.pages):
        if i == 0:
            page.merge_page(overlay_page)
        output_writer.add_page(page)

    output_stream = BytesIO()
    output_writer.write(output_stream)
    output_stream.seek(0)
    return output_stream

# --- INTERFAZ GRÁFICA ---
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class PortablePDFApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Etiquetador Portátil - Sonido Líquido")
        self.geometry("500x450")
        self.pdf_path = None

        ctk.CTkLabel(self, text="Etiquetado de OC / PO (Portable)", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        self.btn_file = ctk.CTkButton(self, text="1. Seleccionar Factura", command=self.pick_file)
        self.btn_file.pack(pady=10)
        
        self.lbl_file = ctk.CTkLabel(self, text="Ningún archivo seleccionado", font=ctk.CTkFont(size=12, slant="italic"))
        self.lbl_file.pack(pady=5)

        ctk.CTkLabel(self, text="2. Tipo de Referencia:").pack(pady=(15, 0))
        self.prefix_var = tk.StringVar(value="OC")
        self.radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_frame.pack()
        ctk.CTkRadioButton(self.radio_frame, text="OC", variable=self.prefix_var, value="OC").pack(side="left", padx=10)
        ctk.CTkRadioButton(self.radio_frame, text="PO", variable=self.prefix_var, value="PO").pack(side="left", padx=10)

        ctk.CTkLabel(self, text="3. Ingrese el Número:").pack(pady=(15, 0))
        self.entry_oc = ctk.CTkEntry(self, placeholder_text="Ej: 2563", width=250)
        self.entry_oc.pack(pady=10)

        self.btn_run = ctk.CTkButton(self, text="Generar PDF Etiquetado", 
                                    command=self.process, 
                                    fg_color="#2ecc71", hover_color="#27ae60",
                                    height=40, font=ctk.CTkFont(weight="bold"))
        self.btn_run.pack(pady=30)

    def pick_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.pdf_path = path
            self.lbl_file.configure(text=os.path.basename(path), text_color="#3498db")

    def process(self):
        oc_val = self.entry_oc.get().strip()
        pref = self.prefix_var.get()
        if not self.pdf_path or not oc_val:
            messagebox.showwarning("Faltan datos", "Seleccione un PDF e ingrese el número.")
            return
        
        try:
            with open(self.pdf_path, "rb") as f:
                output = add_oc_label_standalone(f.read(), oc_val, prefix=pref)
            
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                     initialfile=f"{os.path.splitext(os.path.basename(self.pdf_path))[0]}_etq.pdf")
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(output.getbuffer())
                messagebox.showinfo("Éxito", "Archivo generado correctamente.")
        except NameError:
             messagebox.showerror("Librerías Faltantes", "Asegúrese de ejecutar el archivo .bat para instalar dependencias.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = PortablePDFApp()
    app.mainloop()
