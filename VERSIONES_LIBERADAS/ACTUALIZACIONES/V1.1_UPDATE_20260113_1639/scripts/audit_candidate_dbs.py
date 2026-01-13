import sqlite3
import json
import os

CANDIDATES = [
    r"c:\dev\Sonido_Liquido_V5\pilot.db",
    r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\produccion.db",
    r"c:\dev\Sonido_Liquido_V5\pilot_transfer.db",
    r"c:\dev\Sonido_Liquido_V5\sql_app.db",
    r"c:\dev\Sonido_Liquido_V5\backend\data\cantera.db",
    r"c:\dev\Sonido_Liquido_V5\pilot_backup_132_old.db"
]

def check_db(path):
    if not os.path.exists(path):
        return {"path": path, "status": "NOT FOUND"}
    
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        
        counts = {}
        tables = ['clientes', 'productos', 'pedidos']
        
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                counts[table] = "N/A" # Table missing

        conn.close()
        return {"path": path, "counts": counts, "status": "OK"}
    except Exception as e:
        return {"path": path, "status": "ERROR", "error": str(e)}

def main():
    results = []
    for db_path in CANDIDATES:
        results.append(check_db(db_path))
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    main()
