import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

# Motor Oficial (Integrado en el Core V5)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    from backend.core.utils.pdf import add_oc_label
except ImportError as e:
    root_path = os.path.abspath(BASE_DIR)
    messagebox.showerror("Error de Configuración", 
                         f"No se pudo cargar el motor PDF.\n\nRuta: {root_path}\nError: {str(e)}")
    sys.exit(1)

# Configuración estética
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class EscritorioPDFApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Etiquetador Expreso de Facturas - Sonido Líquido")
        self.geometry("500x450")

        self.pdf_path = None

        # --- Interfaz ---
        ctk.CTkLabel(self, text="Etiquetado de OC / PO", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        # Archivo
        self.btn_file = ctk.CTkButton(self, text="1. Seleccionar Factura", command=self.pick_file)
        self.btn_file.pack(pady=10)
        
        self.lbl_file = ctk.CTkLabel(self, text="Ningún archivo seleccionado", font=ctk.CTkFont(size=12, slant="italic"))
        self.lbl_file.pack(pady=5)

        # Prefijo
        ctk.CTkLabel(self, text="2. Tipo de Referencia:").pack(pady=(15, 0))
        self.prefix_var = tk.StringVar(value="OC")
        self.radio_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.radio_frame.pack()
        
        ctk.CTkRadioButton(self.radio_frame, text="OC (Orden Compra)", variable=self.prefix_var, value="OC").pack(side="left", padx=10)
        ctk.CTkRadioButton(self.radio_frame, text="PO (Purchase Order)", variable=self.prefix_var, value="PO").pack(side="left", padx=10)

        # Número
        ctk.CTkLabel(self, text="3. Ingrese el Número:").pack(pady=(15, 0))
        self.entry_oc = ctk.CTkEntry(self, placeholder_text="Ej: 2563", width=250)
        self.entry_oc.pack(pady=10)

        # Botón Acción
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
            # Ejecutar el motor oficial
            with open(self.pdf_path, "rb") as f:
                output_stream = add_oc_label(f.read(), oc_val, prefix=pref)
            
            # Sugerir nombre basado en el original + sufijo _etq
            base_name = os.path.splitext(os.path.basename(self.pdf_path))[0]
            nombre_sugerido = f"{base_name}_etq.pdf"
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                       initialfile=nombre_sugerido)
            
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(output_stream.getbuffer())
                messagebox.showinfo("Éxito", f"Archivo generado: {os.path.basename(save_path)}")
                self.entry_oc.delete(0, tk.END)
                
        except Exception as e:
            messagebox.showerror("Error", f"Fallo al procesar: {str(e)}")

if __name__ == "__main__":
    app = EscritorioPDFApp()
    app.mainloop()
