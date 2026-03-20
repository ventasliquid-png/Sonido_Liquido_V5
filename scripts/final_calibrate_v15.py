import sqlite3
import os

db_path = 'pilot_v5x.db'
lavimar_id = 'e1be0585cd3443efa33204d00e199c4e'
jofre_name = 'SERGIO JOFRE'

def final_calibrate():
    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        print("Connected to database for final calibration.")

        # 1. Calibrar LAVIMAR a 8205
        cur.execute("UPDATE clientes SET flags_estado = 8205 WHERE id = ?", (lavimar_id,))
        print(f"LAVIMAR calibrated: {cur.rowcount}")

        # 2. Recalcular Blancos (Level 13)
        # 1048576 = Bit 20
        cur.execute("""
            UPDATE clientes 
            SET flags_estado = flags_estado | 1048576 
            WHERE id IN (
                SELECT c.id FROM clientes c 
                JOIN segmentos s ON c.segmento_id = s.id 
                WHERE s.nivel = 13
            )
        """)
        print(f"Blancos updated: {cur.rowcount}")

        # 3. Recalcular Rosas (Level 9/11 + Sergio Jofre)
        # 524288 = Bit 19
        cur.execute("""
            UPDATE clientes 
            SET flags_estado = flags_estado | 524288 
            WHERE id IN (
                SELECT c.id FROM clientes c 
                JOIN segmentos s ON c.segmento_id = s.id 
                WHERE s.nivel IN (9, 11)
            ) OR razon_social LIKE ?
        """, (f"%{jofre_name}%",))
        print(f"Rosas updated: {cur.rowcount}")

        conn.commit()
        
        # FINAL VERIFICATION
        cur.execute("SELECT razon_social, flags_estado FROM clientes WHERE id = ?", (lavimar_id,))
        print(f"VERIFY LAVIMAR: {cur.fetchone()}")
        
        cur.execute("SELECT razon_social, flags_estado FROM clientes WHERE razon_social LIKE ?", (f"%{jofre_name}%",))
        print(f"VERIFY JOFRE: {cur.fetchone()}")

        conn.close()
        print("Final calibration completed.")

    except Exception as e:
        print(f"Calibration Error: {e}")

if __name__ == "__main__":
    final_calibrate()
