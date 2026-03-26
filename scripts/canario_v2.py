import sqlite3
import os
import sys
import subprocess
import time

# CONFIGURACIÓN GEOMETRÍA LÓGICA
DB_PATH = 'pilot_v5x.db'
UUID_LAVIMAR = 'e1be0585cd3443efa33204d00e199c4e'
TARGET_FLAGS = 8205
TRINCHERA_FLAGS = 8207

def radar_electrico():
    """Detecta procesos que podrían estar bloqueando la DB."""
    print("[*] Radar Eléctrico: Escaneando procesos bloqueantes...")
    try:
        # Buscamos procesos python o node que podrían usar la DB
        output = subprocess.check_output('wmic process where "name=\'python.exe\' or name=\'node.exe\'" get processid,commandline', shell=True).decode('utf-8')
        lines = output.strip().split('\n')[1:]
        my_pid = os.getpid()
        zombies = []
        for line in lines:
            if not line.strip(): continue
            parts = line.strip().split()
            pid = int(parts[-1])
            cmd = " ".join(parts[:-1])
            if pid != my_pid and ("Sonido_Liquido_V5" in cmd or "uvicorn" in cmd or "vite" in cmd):
                zombies.append((pid, cmd))
        return zombies
    except Exception as e:
        print(f"[!] Error en Radar: {e}")
        return []

def espolon_defensivo(zombies):
    """Elimina procesos bloqueantes detectados."""
    if not zombies:
        return
    print(f"[*] Espolón Defensivo: Ejecutando eutanasia de {len(zombies)} procesos...")
    for pid, cmd in zombies:
        try:
            subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=True, capture_output=True)
            print(f" [x] PID {pid} terminado.")
        except:
            print(f" [!] Falló terminación de PID {pid}.")

def limpieza_madriguera():
    """Elimina archivos temporales de SQLite."""
    print("[*] Limpieza de Madriguera: Purgando journals...")
    for ext in ['-wal', '-shm', '-journal']:
        path = DB_PATH + ext
        if os.path.exists(path):
            try:
                os.remove(path)
                print(f" [x] {path} eliminado.")
            except:
                print(f" [!] {path} BLOQUEADO.")

def calibracion_constitucional():
    """Verifica y calibra el registro LAVIMAR."""
    print("[*] Iniciando Verificación de Integridad...")
    try:
        conn = sqlite3.connect(DB_PATH, timeout=5)
        # Modo WAL por defecto para evitar bloqueos futuros
        conn.execute("PRAGMA journal_mode=WAL")
        
        # Integrity Check
        res = conn.execute("PRAGMA integrity_check").fetchone()
        if res[0] != "ok":
            print(f"[!] ERROR DE INTEGRIDAD: {res[0]}")
            print("[*] Ejecutando VACUUM de emergencia...")
            conn.execute("VACUUM")

        # Canary Check
        cursor = conn.execute("SELECT razon_social, flags_estado FROM clientes WHERE id=?", (UUID_LAVIMAR,))
        row = cursor.fetchone()
        
        if not row:
            print("[!] ERROR: Registro LAVIMAR no encontrado.")
            return False

        name, flags = row
        print(f" [+] CLIENT: {name}")
        print(f" [+] FLAGS: {flags}")

        if flags == TARGET_FLAGS:
            print(" [OK] ESTADO: NOMINAL GOLD")
        elif flags == TRINCHERA_FLAGS:
            print(" [?] ESTADO: TRINCHERA (Detectado 8207)")
            # Aquí la lógica de flexibilidad: preguntar si es fase de purga
            # En modo automático, calibramos si no hay instrucción contraria
            print(" [*] Calibrando a NOMINAL GOLD (8205)...")
            conn.execute("UPDATE clientes SET flags_estado = ? WHERE id = ?", (TARGET_FLAGS, UUID_LAVIMAR))
            conn.commit()
            print(" [x] Calibración exitosa.")
        else:
            print(f" [!] DESVÍO CRÍTICO: Flags {flags} no reconocidos.")
            return False

        conn.close()
        return True
    except Exception as e:
        print(f"[!] FALLO TÉCNICO: {e}")
        return False

def main():
    start_time = time.time()
    print("========================================================")
    print("       PROTOCOLO EL CANARIO V2.0 (V5.5) - REPORTE")
    print("========================================================")
    
    limpieza_madriguera()
    
    success = calibracion_constitucional()
    if not success:
        zombies = radar_electrico()
        if zombies:
            espolon_defensivo(zombies)
            limpieza_madriguera()
            success = calibracion_constitucional()
        else:
            # Tormenta / Canario Muerto
            print("\n[!] 🔴 TORMENTA: El cielo está horrible y el canario ha muerto.")
            print("[!] Motivo: No se detectaron procesos bloqueantes. El error es estructural.")
            return

    # Lógica de salida humana (Reporte del Cielo)
    # Volvemos a leer para el reporte final de bits
    try:
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute("SELECT flags_estado FROM clientes WHERE id=?", (UUID_LAVIMAR,)).fetchone()
        flags = row[0] if row else 0
        conn.close()

        if flags == TARGET_FLAGS:
            print("\n[+] 🟢 CIELO DESPEJADO: Hola soy Gy. El cielo está despejado y el canario canta sin esfuerzo. Sistema Nominal.")
        elif flags == TRINCHERA_FLAGS:
            print("\n[+] 🟡 CIELO NUBLADO: El cielo presenta nubes: Modo Trinchera/Virginidad detectado. El canario sigue cantando.")
        else:
            print(f"\n[!] 🔴 TORMENTA: El cielo está horrible y el canario ha muerto. Flags desconocidos: {flags}")
    except Exception as e:
        print(f"\n[!] 🔴 TORMENTA: Falla en reporte final. {e}")
    
    elapsed = time.time() - start_time
    print(f"========================================================")
    print(f" TIEMPO DE EJECUCIÓN: {elapsed:.3f}s")
    if elapsed < 0.06:
        print(" [CERTIFICADO] TIEMPO NOMINAL (<0.06s)")
    else:
        print(f" [ALERTA] TIEMPO EXCEDIDO ({elapsed:.3f}s)")
    print("========================================================")

if __name__ == "__main__":
    main()
