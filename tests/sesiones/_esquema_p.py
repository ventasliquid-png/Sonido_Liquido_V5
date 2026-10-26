r"""[S888] Copia una base de P para una prueba y le asegura el esquema que el codigo de hoy espera.

Por que existe: cuando el modelo declara una columna nueva (hoy pedidos_items.kit_grupo, migrate_063), toda consulta ORM sobre una copia VIEJA de P falla con «no such column».
Las copias de BACKUPS_DB son historia y no se tocan; la columna se agrega en la COPIA, con el mismo ALTER TABLE que la migracion. La migracion real tiene su propia prueba
(test_migrate_063_s888.py), que parte de la copia cruda.

Uso: en vez de shutil.copyfile(origen, destino): copiar_p(origen, destino). Si una migracion futura agrega otra columna al modelo, se suma aca (una sola vez para todas las pruebas)."""
import os
import shutil
import sqlite3
from contextlib import contextmanager

COLUMNAS_NUEVAS = [("pedidos_items", "kit_grupo", "INTEGER"), ("empresas_transporte", "web_retiro", "VARCHAR(255)"), ("remitos", "fecha_emision", "DATETIME"), ("remitos", "oc", "VARCHAR"), ("remitos_items", "corrige_item_id", "INTEGER"), ("remitos_items", "causa", "VARCHAR")]    # (tabla, columna, tipo): lo que agregan las migraciones posteriores a las copias mas viejas


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


_usos = 0


@contextmanager
def imagenes_aparte(raiz_app):
    """[S891] Desde el tramo 2 del paquete 2, el primer papel de cada remito queda como imagen en DOCUMENTOS_GENERADOS_RAR/Remitos emitidos
    (por número) y la reimpresión de un remito IMPRESO entrega esa imagen. Las pruebas trabajan sobre copias de P que repiten los mismos
    números: la imagen que deja una no tiene que llegarle a la siguiente. Esto aparta la carpeta mientras corre la prueba, borra lo que la
    prueba dejó y la devuelve como estaba. raiz_app: la carpeta del código que corre (D, o current/ del clon de B). Se puede anidar (el
    corredor la usa por prueba y una prueba puede usarla adentro): cada uso aparta con su propio nombre. Si una corrida se corta, la carpeta
    apartada queda al lado («Remitos emitidos__aparte_<proceso>_<n>») y se devuelve a mano."""
    global _usos
    _usos += 1
    carpeta = os.path.join(raiz_app, "DOCUMENTOS_GENERADOS_RAR", "Remitos emitidos")
    aparte = f"{carpeta}__aparte_{os.getpid()}_{_usos}"
    movida = os.path.isdir(carpeta)
    if movida:
        os.replace(carpeta, aparte)
    try:
        yield carpeta
    finally:
        shutil.rmtree(carpeta, ignore_errors=True)
        if movida:
            os.replace(aparte, carpeta)


def copiar_p(origen, destino, *args, **kwargs):
    resultado = shutil.copyfile(origen, destino, *args, **kwargs)
    if str(destino).lower().endswith(".db"):
        asegurar_esquema(destino)
    return resultado
