import os
from sqlalchemy import create_engine, text

DB_PATH = r"C:\dev\Sonido_Liquido_V5\pilot_v5x.db"

def migrate():
    print(f"Connecting to {DB_PATH}")
    url = f"sqlite:///{DB_PATH}".replace('\\', '/')
    engine = create_engine(url)
    
    with engine.begin() as conn:
        try:
            # Intentar ejecutar el ALTER TABLE
            conn.execute(text("ALTER TABLE rubros ADD COLUMN flags_estado BIGINT DEFAULT 0 NOT NULL;"))
            print("[OK] Columna flags_estado agregada a rubros.")
            
            # Aprovechamos de aplicar retroactividad para inactivos: si activo=0, aplicar bit 2 (4)
            res = conn.execute(text("UPDATE rubros SET flags_estado = 4 WHERE activo = 0;"))
            print(f"[OK] Se aplicó Bit 2 a {res.rowcount} rubros previamente inactivados.")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("[SKIP] La columna flags_estado ya existe.")
            else:
                print(f"[ERR] {e}")

if __name__ == "__main__":
    migrate()
