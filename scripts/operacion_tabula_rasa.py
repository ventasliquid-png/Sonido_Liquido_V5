import sqlite3
import os

DB_PATH = 'pilot_v5x.db'

def operacion_tabula_rasa():
    if not os.path.exists(DB_PATH):
        print(f"[!] Error: No se encontró {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n--- INICIANDO OPERACIÓN TABULA RASA (PURGA DE HISTORIA) ---")

    # 1. Purga de Tablas Transaccionales
    tablas_transaccionales = [
        'pedidos_items',
        'pedidos',
        'remitos_items',
        'remitos',
        'notificaciones'
    ]

    for tabla in tablas_transaccionales:
        try:
            cursor.execute(f"DELETE FROM {tabla}")
            print(f"[OK] Tabla '{tabla}' purgada.")
        except sqlite3.OperationalError as e:
            print(f"[SKIP] Tabla '{tabla}' no existe o error: {e}")

    # 2. Limpieza de Caché y Contadores en Clientes
    print("[*] Limpiando historial_cache, contadores y saldos en clientes...")
    cursor.execute("""
        UPDATE clientes 
        SET historial_cache = '[]', 
            contador_uso = 0, 
            saldo_actual = 0.00
    """)
    print("[OK] Clientes saneados.")

    # 3. Reinicio de Autoincrementales (sqlite_sequence)
    print("[*] Reiniciando contadores de ID (sqlite_sequence)...")
    for tabla in tablas_transaccionales:
        try:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (tabla,))
        except sqlite3.OperationalError:
            pass # No sequence table yet, it's fine
    print("[OK] Contadores reseteados.")

    conn.commit()
    conn.close()

    print("\n--- OPERACIÓN TABULA RASA FINALIZADA (SISTEMA LIMPIO) ---")

if __name__ == "__main__":
    operacion_tabula_rasa()
