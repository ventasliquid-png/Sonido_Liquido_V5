import sqlite3
import os
import shutil

DB_PATH = 'pilot_v5x.db'
MASTER_DB_PATH = r'C:\dev\V5_RELEASE_09\V5_LS_MASTER.db'

def purga_catalogo_fantasma():
    if not os.path.exists(DB_PATH):
        print(f"[!] Error: No se encontró {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n--- INICIANDO PURGA DE CATÁLOGO FANTASMA (V5-LS) ---")

    # 1. Identificar IDs de productos de prueba
    test_keywords = ['Agua', 'Soda', 'Sifón', 'Pack', 'Soda-01', 'Agua-01', 'Pack-Mix']
    test_ids = []
    
    for kw in test_keywords:
        cursor.execute("SELECT id FROM productos WHERE nombre LIKE ? OR sku LIKE ?", (f'%{kw}%', f'%{kw}%'))
        test_ids.extend([row[0] for row in cursor.fetchall()])
    
    test_ids = list(set(test_ids))
    print(f"[*] Encontrados {len(test_ids)} SKUs de prueba para purgar.")

    # 2. Borrar de productos_costos
    if test_ids:
        placeholders = ', '.join(['?'] * len(test_ids))
        cursor.execute(f"DELETE FROM productos_costos WHERE producto_id IN ({placeholders})", test_ids)
        print(f"[OK] {cursor.rowcount} registros de costos eliminados.")

        # 3. Borrar de productos
        cursor.execute(f"DELETE FROM productos WHERE id IN ({placeholders})", test_ids)
        print(f"[OK] {cursor.rowcount} productos eliminados.")

    # 4. Asegurar Purga de Pedidos y Remitos (Tabula Rasa Total)
    tablas_transaccionales = ['pedidos_items', 'pedidos', 'remitos_items', 'remitos', 'notificaciones']
    for tabla in tablas_transaccionales:
        try:
            cursor.execute(f"DELETE FROM {tabla}")
            print(f"[OK] Tabla '{tabla}' purgada (Tabula Rasa).")
        except:
            pass

    # 5. Limpieza de Clientes
    print("[*] Saneando historial_cache y saldos de clientes...")
    cursor.execute("UPDATE clientes SET historial_cache = '[]', contador_uso = 0, saldo_actual = 0.00")
    print("[OK] Clientes saneados.")

    # 6. Reset Sequences
    try:
        cursor.execute("DELETE FROM sqlite_sequence")
        print("[OK] Contadores reseteados.")
    except sqlite3.OperationalError:
        print("[*] No se encontró sqlite_sequence (Base ya limpia).")

    conn.commit()
    
    # 7. Conteo Final
    cursor.execute("SELECT count(*) FROM productos WHERE activo=1")
    count_final = cursor.fetchone()[0]
    print(f"\n[CERTIFICACIÓN] SKUs Reales Restantes: {count_final}")

    conn.close()

    # 8. Clonación Maestra
    print(f"[*] Clonando a {MASTER_DB_PATH}...")
    try:
        shutil.copy2(DB_PATH, MASTER_DB_PATH)
        print(f"[OK] Malla de Oro V5_LS_MASTER.db creada exitosamente.")
    except Exception as e:
        print(f"[!] Error en clonación: {e}")

    print("\n--- PURGA Y CLONACIÓN FINALIZADA ---")

if __name__ == "__main__":
    purga_catalogo_fantasma()
