r"""[S888] Copia una base de P para una prueba y le asegura el esquema que el codigo de hoy espera.

Por que existe: cuando el modelo declara una columna nueva (hoy pedidos_items.kit_grupo, migrate_063), toda consulta ORM sobre una copia VIEJA de P falla con «no such column».
Las copias de BACKUPS_DB son historia y no se tocan; la columna se agrega en la COPIA, con el mismo ALTER TABLE que la migracion. La migracion real tiene su propia prueba
(test_migrate_063_s888.py), que parte de la copia cruda.

Uso: en vez de shutil.copyfile(origen, destino): copiar_p(origen, destino). Si una migracion futura agrega otra columna al modelo, se suma aca (una sola vez para todas las pruebas)."""
import shutil
import sqlite3

COLUMNAS_NUEVAS = [("pedidos_items", "kit_grupo", "INTEGER")]    # (tabla, columna, tipo): lo que agregan las migraciones posteriores a las copias mas viejas


def asegurar_esquema(db_path):
    con = sqlite3.connect(db_path)
    try:
        for tabla, columna, tipo in COLUMNAS_NUEVAS:
            if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabla,)).fetchone():
                continue
            if columna not in {r[1] for r in con.execute(f"PRAGMA table_info({tabla})")}:
                con.execute(f"ALTER TABLE {tabla} ADD COLUMN {columna} {tipo}")
        con.commit()
    finally:
        con.close()


def copiar_p(origen, destino, *args, **kwargs):
    resultado = shutil.copyfile(origen, destino, *args, **kwargs)
    if str(destino).lower().endswith(".db"):
        asegurar_esquema(destino)
    return resultado
