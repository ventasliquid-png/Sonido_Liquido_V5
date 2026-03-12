import shutil
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RELEASES_DIR = BASE_DIR / "VERSIONES_LIBERADAS"
DRIVE_PATH = Path("O:/")

def deploy():
    print("--- DESPLIEGUE A UNIDAD DE RED (O:) ---")
    
    # 1. Encontrar la última versión
    if not RELEASES_DIR.exists():
        print("❌ No existe carpeta VERSIONES_LIBERADAS")
        return

    versions = sorted([d for d in RELEASES_DIR.iterdir() if d.is_dir()], key=os.path.getmtime, reverse=True)
    if not versions:
        print("❌ No hay versiones generadas.")
        return

    latest_version = versions[0]
    print(f"📦 Versión seleccionada: {latest_version.name}")

    # 2. Zipear
    zip_name = "Sonido_Liquido_V5_Instalador"
    zip_output_path = RELEASES_DIR / zip_name # sin extension .zip, shutil la agrega
    
    print(f"📚 Comprimiendo a {zip_name}.zip ...")
    shutil.make_archive(str(zip_output_path), 'zip', latest_version)
    
    final_zip_path = RELEASES_DIR / f"{zip_name}.zip"
    
    # 3. Copiar a O:
    if not os.path.exists(str(DRIVE_PATH)):
        print(f"⚠️  UNIDAD O: NO DETECTADA. El archivo queda local en: {final_zip_path}")
        return

    try:
        dest_path = DRIVE_PATH / f"{zip_name}.zip"
        print(f"🚀 Subiendo a {dest_path} ...")
        shutil.copy2(final_zip_path, dest_path)
        print("✅ SUBIDA EXITOSA.")
    except Exception as e:
        print(f"❌ Error al copiar al Drive: {e}")
        print(f"   El archivo está seguro localmente en: {final_zip_path}")

if __name__ == "__main__":
    deploy()
