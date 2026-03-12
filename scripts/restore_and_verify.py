import shutil
import sqlite3
import os
import sys

src = 'pilot.db'
dst = os.path.join('backend', 'data', 'pilot.db')

print(f"--- OPERACION RESTAURACION ---")
print(f"Fuente: {src}")
print(f"Destino: {dst}")

if not os.path.exists(src):
    print(f"ERROR: Fuente no encontrada.")
    sys.exit(1)

try:
    # 1. COPY
    print("Copiando archivo...")
    shutil.copy2(src, dst)
    print("Copia completada.")

    # 2. VERIFY
    print(f"Verificando {dst}...")
    conn = sqlite3.connect(dst)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM clientes")
    count = cursor.fetchone()[0]
    print(f"CLIENTES EN DESTINO: {count}")
    
    conn.close()
    
    if count == 0:
        print("ALERTA: Copia exitosa pero 0 clientes detectados (¿o archivo origen estaba mal?)")
    else:
        print("VERIFICACION EXITOSA.")

except Exception as e:
    print(f"ERROR CRITICO: {e}")
    sys.exit(1)
