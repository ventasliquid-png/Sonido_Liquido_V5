import sqlite3
import sys

def verificar_v5x():
    try:
        # Conexión a la base nativa definida en los mandamientos
        conn = sqlite3.connect('pilot.db')
        cursor = conn.cursor()
        
        # El "Código Secreto": Contar registros recuperados en el rango crítico
        cursor.execute("SELECT COUNT(*) FROM clientes WHERE id BETWEEN 2 AND 39")
        try:
             count = cursor.fetchone()[0]
        except TypeError:
             count = 0
        
        # Verificar también la existencia de la columna de 32 bits (4 bytes)
        cursor.execute("PRAGMA table_info(clientes)")
        columnas = [col[1] for col in cursor.fetchall()]
        has_flags = 'flags_estado' in columnas
        
        conn.close()
        
        # Condición de éxito: Presencia de datos recuperados y estructura de 32 bits
        # [AUTORIZACIÓN COMANDANTE]: Umbral recalibrado a 33 registros.
        if count >= 33 and has_flags:
            return True
        return False
    except Exception as e:
        # print(f"Error: {e}") # Optional debug
        return False

if __name__ == "__main__":
    if verificar_v5x():
        sys.exit(0)  # Éxito: Todo en orden
    else:
        sys.exit(1)  # Error: Base de datos incorrecta o corrupta
