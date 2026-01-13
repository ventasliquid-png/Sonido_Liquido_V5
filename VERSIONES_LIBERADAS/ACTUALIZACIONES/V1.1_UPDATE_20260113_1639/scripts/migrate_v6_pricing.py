import sqlite3

def run_migration():
    conn = sqlite3.connect('pilot.db')
    cursor = conn.cursor()
    
    print("🚀 Inyectando columnas para el Motor de Precios V6...")
    
    try:
        # Agregar margen_default a rubros
        cursor.execute("ALTER TABLE rubros ADD COLUMN margen_default NUMERIC(6, 2) DEFAULT 0.0")
        print("✅ Columna 'margen_default' añadida a 'rubros'")
    except sqlite3.OperationalError:
        print("⚠️ Columna 'margen_default' ya existía en 'rubros'")
        
    try:
        # Agregar cm_objetivo a productos_costos
        cursor.execute("ALTER TABLE productos_costos ADD COLUMN cm_objetivo NUMERIC(6, 2) DEFAULT NULL")
        print("✅ Columna 'cm_objetivo' añadida a 'productos_costos'")
    except sqlite3.OperationalError:
        print("⚠️ Columna 'cm_objetivo' ya existía en 'productos_costos'")
        
    conn.commit()
    conn.close()
    print("🏁 Migración completada.")

if __name__ == "__main__":
    run_migration()
