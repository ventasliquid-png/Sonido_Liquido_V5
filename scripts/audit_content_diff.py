import difflib
import os

FILES_TO_DIFF = [
    r"backend\pedidos\router.py",
    r"backend\pedidos\models.py",
    r"frontend\src\views\Pedidos\PedidoList.vue",
    r"frontend\src\views\Pedidos\PedidoInspector.vue",
    r"frontend\src\services\pedidos.js",
    r"frontend\src\views\Hawe\ClientCanvas.vue",
    r"frontend\src\composables\useFormHistory.js"
]

DEV_ROOT = r"C:\dev\Sonido_Liquido_V5"
PROD_ROOT = r"C:\dev\V5-LS\current"

def diff_files():
    print("=== AUDITORÍA DE CONTENIDO: DIFF LÍNEA A LÍNEA ===")
    
    for rel_path in FILES_TO_DIFF:
        dev_path = os.path.join(DEV_ROOT, rel_path)
        prod_path = os.path.join(PROD_ROOT, rel_path)
        
        print(f"\n--- Analizando: {rel_path} ---")
        
        if not os.path.exists(dev_path):
            print(f" [!] Error: {dev_path} no existe en DEV")
            continue
        if not os.path.exists(prod_path):
            print(f" [!] Error: {prod_path} no existe en PROD")
            continue
            
        with open(dev_path, 'r', encoding='utf-8', errors='ignore') as f_dev:
            dev_lines = f_dev.readlines()
        with open(prod_path, 'r', encoding='utf-8', errors='ignore') as f_prod:
            prod_lines = f_prod.readlines()
            
        diff = list(difflib.unified_diff(
            dev_lines, prod_lines, 
            fromfile='DEV', tofile='PROD', 
            lineterm=''
        ))
        
        if not diff:
            print(" [OK] Contenido idéntico.")
        else:
            print(f" [!] Divergencia encontrada ({len(diff)} líneas de diff):")
            # Limit output to first 20 lines of diff
            for line in diff[:30]:
                print(line)
            if len(diff) > 30:
                print(" (...) diff truncado por brevedad.")

if __name__ == "__main__":
    diff_files()
