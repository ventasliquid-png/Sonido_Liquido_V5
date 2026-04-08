# [SANEAMIENTO] - scripts\reparacion\fix_pedidos_master.py
# Versión: V1.2 | Protocolo Nike | PIN 1974
# ---------------------------------------------------------

import sqlite3
import os

db_path = r'C:\dev\V5-LS\data\V5_LS_MASTER.db'

def fix_pedidos():
    if not os.path.exists(db_path):
        print(f"Error: Base de datos no encontrada en {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print(f"--- [OPERACION SANEAMIENTO] Conectado a {db_path} ---")
        
        # 1. Auditoria Previa
        cursor.execute("SELECT id, total, estado FROM pedidos WHERE id IN (6, 7)")
        rows = cursor.fetchall()
        print(f"Pedidos encontrados para borrar: {rows}")
        
        if not rows:
            print("No se encontraron los pedidos 6 y 7. Ya podrian haber sido borrados.")
        else:
            # 2. Borrado de Items
            print("Borrando items de pedidos 6 y 7...")
            cursor.execute("DELETE FROM pedidos_items WHERE pedido_id IN (6, 7)")
            print(f"Items eliminados: {cursor.rowcount}")
            
            # 3. Borrado de Pedidos
            print("Borrando pedidos 6 y 7...")
            cursor.execute("DELETE FROM pedidos WHERE id IN (6, 7)")
            print(f"Pedidos eliminados: {cursor.rowcount}")
        
        # Nota: En este esquema SQLite sin AUTOINCREMENT explicito, 
        # borrar el max ID ajusta automaticamente el proximo ID a MAX+1.
        
        conn.commit()
        print("\nEXITO: Saneamiento completado. La base de datos esta nominal.")
        
        # 4. Verificacion Final
        cursor.execute("SELECT MAX(id) FROM pedidos")
        max_id = cursor.fetchone()[0]
        print(f"Estado Final: MAX(id) = {max_id} (Proximo pedido sera {max_id + 1 if max_id else 1})")
        
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Fallo en la operacion: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_pedidos()
