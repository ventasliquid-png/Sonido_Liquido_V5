import sqlite3
import os
import sys

# Si le pasamos un argumento usa ese, si no, usa el default
DB_PATH = sys.argv[1] if len(sys.argv) > 1 else "backend/data/cantera.db"

def inspect():
    print(f"\n🔎 INSPECCIONANDO: {DB_PATH}")
    print("=" * 40)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: No encuentro el archivo: {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener lista de tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        if not tables:
            print("👻 LA BASE DE DATOS ESTÁ VACÍA (0 tablas).")
            print("   Es un cascarón creado automáticamente por SQLAlchemy.")
        else:
            print(f"📂 Tablas encontradas ({len(tables)}): {', '.join(tables)}\n")

            # CONTEO
            target_tables = ['clientes', 'productos', 'pedidos', 'listas_precios', 'items_pedido']
            
            for table in target_tables:
                if table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"📊 {table.upper().ljust(15)}: {count} registros")
                    
                    if count > 0:
                        try:
                            # Intenta mostrar algo útil
                            cursor.execute(f"PRAGMA table_info({table})")
                            columns = [info[1] for info in cursor.fetchall()]
                            col_to_show = '*'
                            if 'nombre' in columns: col_to_show = 'nombre'
                            elif 'razon_social' in columns: col_to_show = 'razon_social'
                            
                            cursor.execute(f"SELECT {col_to_show} FROM {table} ORDER BY rowid DESC LIMIT 3")
                            rows = cursor.fetchall()
                            print(f"   Últimos: {rows}")
                        except:
                            pass
                    print("-" * 30)
                else:
                    # Si la tabla no está en la lista standard pero existe en la base, no decimos nada
                    # Solo reportamos si FALTA una de las importantes
                    pass

        # Verificamos tamaño del archivo
        size_kb = os.path.getsize(DB_PATH) / 1024
        print(f"\n💾 TAMAÑO FÍSICO: {size_kb:.2f} KB")
        conn.close()

    except Exception as e:
        print(f"🔥 ERROR AL LEER LA BASE: {e}")

if __name__ == "__main__":
    inspect()