import sqlite3
import os
import uuid

def normalize_db(db_path):
    print(f"🚀 Iniciando normalización de IDs en: {db_path}")
    if not os.path.exists(db_path):
        print("❌ Error: Archivo no encontrado.")
        return

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Obtener todas las tablas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cur.fetchall()]
    
    for table in tables:
        # Obtener columnas de la tabla
        cur.execute(f"PRAGMA table_info({table});")
        columns = cur.fetchall()
        
        for col in columns:
            col_name = col[1]
            type_name = col[2].upper()
            
            # Solo procesar si el nombre sugiere un ID o el tipo es CHAR(32)/GUID
            if 'ID' in col_name.upper() or 'CHAR(32)' in type_name or 'GUID' in type_name:
                print(f"  🔍 Procesando {table}.{col_name}...")
                
                # Buscar registros con guiones
                cur.execute(f"SELECT {col_name} FROM {table} WHERE {col_name} LIKE '%-%'")
                rows = cur.fetchall()
                
                if rows:
                    print(f"    ✨ Normalizando {len(rows)} registros...")
                    for r in rows:
                        old_val = r[0]
                        try:
                            # Convertir a hex-32 (sin guiones)
                            new_val = uuid.UUID(old_val).hex
                            cur.execute(f"UPDATE {table} SET {col_name} = ? WHERE {col_name} = ?", (new_val, old_val))
                        except Exception as e:
                            # print(f"    ⚠️ Saltando {old_val}: {e}")
                            pass
        conn.commit()
    
    conn.close()
    print("✅ Normalización completada.")

normalize_db('pilot.db')
