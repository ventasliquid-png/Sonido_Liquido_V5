import shutil
import datetime
import os
from pathlib import Path

def main():
    """
    Script universal para realizar respaldo de la base de datos pilot.db y memoria vectorial.
    Reemplaza a backup_db.ps1.
    """
    base_dir = Path(__file__).resolve().parent.parent
    backup_dir = base_dir / "_BACKUPS_IOWA"
    
    # Asegurar que el directorio de backup existe
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # 1. Respaldo de pilot.db
    db_file = base_dir / "pilot.db"
    if db_file.exists():
        backup_file = backup_dir / f"pilot_backup_{timestamp}.db"
        print(f"📦 Copiando {db_file.name} a {backup_file.name}...")
        try:
            shutil.copy2(db_file, backup_file)
            print("✅ Respaldo de Base de Datos SQL completado.")
        except Exception as e:
            print(f"❌ Error al copiar pilot.db: {e}")
    else:
        print("⚠️ No se encontró pilot.db para respaldar.")

    # 2. Respaldo de Memoria Vectorial (Chroma / JSON local)
    # Buscamos carpetas comunes de chroma si existen
    chroma_dirs = ["chroma_db", "chroma", "vector_store"]
    found_vector = False
    for folder in chroma_dirs:
        chroma_path = base_dir / folder
        if chroma_path.exists() and chroma_path.is_dir():
            backup_chroma_zip = backup_dir / f"{folder}_backup_{timestamp}"
            print(f"🧠 Encontrada memoria vectorial en '{folder}'. Comprimiendo...")
            try:
                shutil.make_archive(str(backup_chroma_zip), 'zip', chroma_path)
                print(f"✅ Respaldo de Vector Store ({folder}) completado.")
                found_vector = True
            except Exception as e:
                print(f"❌ Error al respaldar {folder}: {e}")
    
    # También verificar archivos JSON de memoria si existen (ej: memory.json)
    json_memories = ["memory.json", "vector_store.json"]
    for json_file in json_memories:
        j_path = base_dir / json_file
        if j_path.exists():
            backup_j = backup_dir / f"{json_file}_{timestamp}.json"
            print(f"📄 Respaldo de archivo de memoria {json_file}...")
            shutil.copy2(j_path, backup_j)
            found_vector = True

    if not found_vector:
        print("ℹ️ No se detectaron almacenamientos vectoriales locales estándar (chroma/json).")
        # Si se usa PGVector externo, el respaldo debe ser vía dump, que no cubrimos aquí.

    print(f"\n🏁 Operación de respaldo finalizada. Destino: {backup_dir}")

if __name__ == "__main__":
    main()
