import sqlite3
import os

db_path = 'pilot_v5x.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print("Connected to database for migration.")

        # 1. Identificar Blancos (Nivel 13) y Rosas (Nivel 9, 11)
        # Sergio Jofre es una excepcion: es Rosa (Bit 19) independientemente de su nivel actual.
        
        # Bit 20 (Blancos/AUDIT_REQ): 1 << 20 = 1048576
        # Bit 19 (Rosas/PINK): 1 << 19 = 524288

        # --- RECALCULO DE BITS ---
        
        # Primero, limpiamos los bits 19 y 20 para recalcular (Opcional, pero para ser precisos)
        # cur.execute("UPDATE clientes SET flags_estado = flags_estado & ~(1048576 | 524288)")
        
        # 23 Blancos: Nivel 13 (Excluyendo a Sergio Jofre si llegara a tener nivel 13)
        cur.execute("""
            UPDATE clientes 
            SET flags_estado = flags_estado | 1048576 
            WHERE id IN (
                SELECT clientes.id 
                FROM clientes 
                JOIN segmentos ON clientes.segmento_id = segmentos.id 
                WHERE segmentos.nivel = 13 
                AND clientes.razon_social NOT LIKE '%JOFRE SERGIO%'
            )
        """)
        print(f"Blancos (Bit 20) updated: {cur.rowcount}")

        # 6 Rosas: Nivel 9 o 11 + Sergio Jofre
        cur.execute("""
            UPDATE clientes 
            SET flags_estado = flags_estado | 524288 
            WHERE id IN (
                SELECT clientes.id 
                FROM clientes 
                JOIN segmentos ON clientes.segmento_id = segmentos.id 
                WHERE segmentos.nivel IN (9, 11)
            ) OR razon_social LIKE '%JOFRE SERGIO%'
        """)
        print(f"Rosas (Bit 19) updated: {cur.rowcount}")

        conn.commit()
        
        # Verify counts
        cur.execute("SELECT count(*) FROM clientes WHERE (flags_estado & 1048576) != 0")
        print(f"Final Bit 20 count: {cur.fetchone()[0]}")
        cur.execute("SELECT count(*) FROM clientes WHERE (flags_estado & 524288) != 0")
        print(f"Final Bit 19 count: {cur.fetchone()[0]}")
        
        conn.close()
        print("Migration V15.1 completed successfully.")

    except Exception as e:
        print(f"Migration Error: {e}")

if __name__ == "__main__":
    migrate()
