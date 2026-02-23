import tkinter as tk
import threading
import requests
import time

API_URL = "http://127.0.0.1:8000/atenea/telemetria"

class RadarFlotante(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configuración de ventana
        self.title("Radar Atenea V5")
        self.geometry("380x30")
        self.attributes("-topmost", True)  # Siempre visible
        self.overrideredirect(True)        # Sin bordes nativos
        
        # Iniciar posición en la pantalla (esquina superior derecha por ej.)
        screen_width = self.winfo_screenwidth()
        self.geometry(f"+{screen_width - 400}+50")

        # Configuración visual
        self.configure(bg="#222")
        self.label = tk.Label(
            self, text="Inicializando Radar...", 
            font=("Consolas", 10, "bold"), 
            bg="#222", fg="#aaa"
        )
        self.label.pack(expand=True, fill=tk.BOTH)
        
        # Permitir arrastrar la ventana
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        # Iniciar hilo de chequeo
        self.running = True
        self.thread = threading.Thread(target=self.poll_telemetry, daemon=True)
        self.thread.start()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        x = self.winfo_pointerx() - self.x
        y = self.winfo_pointery() - self.y
        self.geometry(f"+{x}+{y}")

    def update_ui(self, data):
        """Actualiza el label con base en la telemetría."""
        try:
            is_cooldown = data.get("is_cooldown", False)
            flash_count = data.get("flash_count", 0)
            pro_count = data.get("pro_count", 0)
            total_flash = data.get("total_flash_count", 0)
            total_pro = data.get("total_pro_count", 0)
            seg_restantes = data.get("segundos_restantes", 0)

            total_ses = flash_count + pro_count
            flash_perc = int((flash_count / total_ses * 100)) if total_ses > 0 else 0
            pro_perc = int((pro_count / total_ses * 100)) if total_ses > 0 else 0
            
            total_dia = total_flash + total_pro
            tot_flash_perc = int((total_flash / total_dia * 100)) if total_dia > 0 else 0
            tot_pro_perc = int((total_pro / total_dia * 100)) if total_dia > 0 else 0

            if is_cooldown:
                # Formatear a HH:MM:SS
                horas = seg_restantes // 3600
                mins = (seg_restantes % 3600) // 60
                secs = seg_restantes % 60
                if horas > 0:
                    time_str = f"{horas:02d}:{mins:02d}:{secs:02d}"
                else:
                    time_str = f"{mins:02d}:{secs:02d}"
                    
                self.configure(bg="#8b0000")  # Fondo rojo oscuro
                self.label.configure(
                    text=f"⏳ PRO SUSPENDIDO EN: {time_str}", 
                    bg="#8b0000", fg="#ffcc00"
                )
            else:
                self.configure(bg="#222")
                self.label.configure(
                    text=f"S: ⚡{flash_perc}% 🧠{pro_perc}% | T: ⚡{tot_flash_perc}% 🧠{tot_pro_perc}%",
                    bg="#222", fg="#8be9fd"
                )
        except Exception as e:
            self.label.configure(text="Error de Parseo", bg="#222", fg="red")

    def poll_telemetry(self):
        """Hilo en background que hace peticiones al backend."""
        while self.running:
            try:
                response = requests.get(API_URL, timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    # Actualizar UI siempre a través del hilo principal (after)
                    self.after(0, self.update_ui, data)
                else:
                    self.after(0, lambda: self.label.configure(text="Sin Conexión...", fg="#ff5555"))
            except requests.exceptions.RequestException:
                self.after(0, lambda: self.label.configure(text="Backend Inactivo", fg="#ff5555", bg="#222"))
            
            time.sleep(2)

if __name__ == "__main__":
    app = RadarFlotante()
    app.mainloop()
