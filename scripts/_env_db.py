# [IDENTIDAD] - scripts/_env_db.py
"""
Resolución de entorno/DB compartida — sin dependencias externas (no openpyxl).
Usada por exportar_pedidos_excel.py y sincronizar_historial_notas.py para no
duplicar la lógica de detección de entorno una tercera vez (reconciliación S849,
Card #93-bis — ningún feature debe existir únicamente en un script/repo).
"""
import os

SILO_DIR = r'Q:\Mi unidad\V5_Silo_Claude'


def detectar_entorno_db():
    """
    Lee DATABASE_URL de .env — prueba raíz del proyecto primero (D),
    current/.env después (B). Misma función en ambos repos.
    Retorna (db_path, entorno) — entorno es 'TOM' (V5_LS_MASTER.db) o 'DEV' (cualquier otro).
    """
    aqui         = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(aqui, '..'))

    candidatos = [
        os.path.join(project_root, '.env'),               # D: raíz directa
        os.path.join(project_root, 'current', '.env'),     # B: bajo current/
    ]
    env_path = next((p for p in candidatos if os.path.isfile(p)), None)

    db_path = None
    if env_path:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('DATABASE_URL='):
                    val = line.split('=', 1)[1].strip().strip('"').strip("'")
                    if val.startswith('sqlite:///'):
                        db_path = val[len('sqlite:///'):]
                    break

    if not db_path:
        db_path = 'pilot_v5x.db'   # fallback legacy

    entorno = 'TOM' if os.path.basename(db_path) == 'V5_LS_MASTER.db' else 'DEV'
    return db_path, entorno
