import sqlite3
import os

DB_PATH = 'pilot.db'

def wipe_db():
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: No se encuentra {DB_PATH}")
        return

    print(f"🔥 Iniciando WIPE masivo de {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Desactivar llaves foráneas para permitir borrado masivo
    cursor.execute("PRAGMA foreign_keys = OFF;")

    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        try:
            cursor.execute(f"DELETE FROM {table};")
            # Resetear secuencias de autoincremento si existen
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table}';")
            print(f"   🧹 {table}: Registros eliminados.")
        except Exception as e:
            print(f"   ❌ Error limpiando '{table}': {e}")

    conn.commit()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # VACUUM para reducir el tamaño del archivo y limpiar físicamente
    cursor.execute("VACUUM;")
    
    conn.close()
    print(f"\n✨ Tabula Rasa: {DB_PATH} está ahora vacía.")

if __name__ == "__main__":
    confirm = input("⚠️ ¿ESTÁS SEGURO DE QUE DESEAS BORRAR TODOS LOS DATOS OPERATIVOS? (S/N): ")
    if confirm.lower() == 's':
        wipe_db()
    else:
        print("❌ Operación cancelada.")
