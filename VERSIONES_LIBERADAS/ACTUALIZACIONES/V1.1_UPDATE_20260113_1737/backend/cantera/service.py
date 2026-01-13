import sqlite3
import json
import os
from pathlib import Path
from typing import List, Dict, Any

# Configuración de Rutas
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MIRROR_DIR = BASE_DIR / "backend" / "data" / "json_mirror"
CANTERA_DB_PATH = BASE_DIR / "backend" / "data" / "cantera.db"

class CanteraService:
    @staticmethod
    def get_connection():
        return sqlite3.connect(str(CANTERA_DB_PATH))

    @staticmethod
    def sync_from_json():
        """Sincroniza los espejos JSON hacia cantera.db"""
        print(f"📡 Cantera Sync: Sincronizando desde {MIRROR_DIR}...")
        
        if not MIRROR_DIR.exists():
            print("⚠️ Error: No existe el directorio de espejos JSON.")
            return False

        conn = sqlite3.connect(str(CANTERA_DB_PATH))
        cursor = conn.cursor()

        # 1. Crear Tablas de Consulta
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id TEXT PRIMARY KEY,
                razon_social TEXT,
                cuit TEXT,
                activo INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id TEXT PRIMARY KEY,
                sku TEXT,
                nombre TEXT,
                activo INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rubros (
                id INTEGER PRIMARY KEY,
                nombre TEXT,
                activo INTEGER
            )
        """)
        
        # 2. Limpiar datos viejos
        cursor.execute("DELETE FROM clientes")
        cursor.execute("DELETE FROM productos")
        cursor.execute("DELETE FROM rubros")

        # 3. Importar Clientes
        clientes_file = MIRROR_DIR / "clientes.json"
        if clientes_file.exists():
            with open(clientes_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    cursor.execute(
                        "INSERT INTO clientes (id, razon_social, cuit, activo) VALUES (?, ?, ?, ?)",
                        (str(item.get("id")), str(item.get("razon_social")), str(item.get("cuit")), item.get("activo", 1))
                    )
            print(f"   ✅ {len(data)} clientes cargados en Cantera.")

        # 4. Importar Productos
        productos_file = MIRROR_DIR / "productos.json"
        if productos_file.exists():
            with open(productos_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    cursor.execute(
                        "INSERT INTO productos (id, sku, nombre, activo) VALUES (?, ?, ?, ?)",
                        (str(item.get("id")), str(item.get("sku")), str(item.get("nombre")), item.get("activo", 1))
                    )
            print(f"   ✅ {len(data)} productos cargados en Cantera.")

        # 5. Importar Rubros
        rubros_file = MIRROR_DIR / "rubros.json"
        if rubros_file.exists():
            with open(rubros_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    cursor.execute(
                        "INSERT INTO rubros (id, nombre, activo) VALUES (?, ?, ?)",
                        (item.get("id"), str(item.get("nombre")), item.get("activo", 1))
                    )
            print(f"   ✅ {len(data)} rubros cargados en Cantera.")

        conn.commit()
        conn.close()
        return True

    @staticmethod
    def search_clientes(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn = CanteraService.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute(
            "SELECT * FROM clientes WHERE (razon_social LIKE ? OR cuit LIKE ?) AND activo = 1 LIMIT ?",
            (search_term, search_term, limit)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    @staticmethod
    def get_clientes(limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
        conn = CanteraService.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY razon_social LIMIT ? OFFSET ?", (limit, offset))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    @staticmethod
    def search_productos(query: str, limit: int = 10) -> List[Dict[str, Any]]:
        conn = CanteraService.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        search_term = f"%{query}%"
        cursor.execute(
            "SELECT * FROM productos WHERE (nombre LIKE ? OR sku LIKE ?) AND activo = 1 LIMIT ?",
            (search_term, search_term, limit)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    @staticmethod
    def get_productos(limit: int = 200, offset: int = 0) -> List[Dict[str, Any]]:
        conn = CanteraService.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM productos ORDER BY nombre LIMIT ? OFFSET ?", (limit, offset))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    @staticmethod
    def get_full_client_data(client_id: str) -> Dict[str, Any]:
        """Recupera el objeto completo del JSON para importación total"""
        clientes_file = MIRROR_DIR / "clientes.json"
        if not clientes_file.exists(): return None
        
        with open(clientes_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return next((c for c in data if str(c.get("id")) == client_id), None)

    @staticmethod
    def get_full_product_data(product_id: str) -> Dict[str, Any]:
        """Recupera el objeto completo del JSON de productos"""
        productos_file = MIRROR_DIR / "productos.json"
        if not productos_file.exists(): return None
        
        with open(productos_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # IDs de productos en el JSON pueden ser int
            return next((p for p in data if str(p.get("id")) == str(product_id)), None)

    @staticmethod
    def get_full_rubro_data(rubro_id: int) -> Dict[str, Any]:
        rubros_file = MIRROR_DIR / "rubros.json"
        if not rubros_file.exists(): return None
        with open(rubros_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return next((r for r in data if r.get("id") == rubro_id), None)

    @staticmethod
    def inactivate_client(client_id: str):
        # 1. Update SQLite
        conn = CanteraService.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE clientes SET activo = 0 WHERE id = ?", (client_id,))
        conn.commit()
        conn.close()
        
        # 2. Update JSON Mirror for persistence
        clientes_file = MIRROR_DIR / "clientes.json"
        if clientes_file.exists():
            with open(clientes_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                updated = False
                for c in data:
                    if str(c.get("id")) == client_id:
                        c["activo"] = 0
                        updated = True
                if updated:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

    @staticmethod
    def inactivate_product(product_id: str):
        # 1. Update SQLite
        conn = CanteraService.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE productos SET activo = 0 WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        
        # 2. Update JSON Mirror for persistence
        productos_file = MIRROR_DIR / "productos.json"
        if productos_file.exists():
            with open(productos_file, "r+", encoding="utf-8") as f:
                data = json.load(f)
                updated = False
                for p in data:
                    if str(p.get("id")) == product_id:
                        p["activo"] = 0
                        updated = True
                if updated:
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
