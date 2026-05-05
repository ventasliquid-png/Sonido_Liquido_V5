import sqlite3

def get_stats(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        r = cur.execute('SELECT COUNT(*) FROM rubros').fetchone()[0]
        p = cur.execute('SELECT COUNT(*) FROM productos').fetchone()[0]
        pc = cur.execute('SELECT COUNT(*) FROM productos_costos').fetchone()[0]
        conn.close()
        return (r, p, pc)
    except Exception as e:
        return str(e)

d1 = 'c:/dev/Sonido_Liquido_V5/pilot_v5x.db'
d2 = 'C:/dev/V5-LS/data/V5_LS_MASTER.db'

s1 = get_stats(d1)
s2 = get_stats(d2)

print(f"--- COMPARATIVA DE SISTEMAS ---")
print(f"DEV (Sonido_Liquido_V5):  {s1[0]} Rubros | {s1[1]} Productos | {s1[2]} Costos")
print(f"PROD (V5-LS):             {s2[0]} Rubros | {s2[1]} Productos | {s2[2]} Costos")

if isinstance(s1, tuple) and isinstance(s2, tuple):
    print(f"Diferencia de Datos:      {s2[1] - s1[1]} productos de diferencia.")
    if s2[2] < s2[1]:
        print(f"ALERTA PROD: {s2[1] - s2[2]} productos en Producción NO tienen costos cargados.")
