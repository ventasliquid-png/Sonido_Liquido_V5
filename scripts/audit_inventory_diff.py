import os

def inventory_diff(dir_dev, dir_prod):
    inventory = {}
    
    for root, dirs, files in os.walk(dir_dev):
        rel_path = os.path.relpath(root, dir_dev)
        for f in files:
            f_rel = os.path.join(rel_path, f)
            inventory[f_rel] = {"dev": True, "prod": False}

    for root, dirs, files in os.walk(dir_prod):
        rel_path = os.path.relpath(root, dir_prod)
        for f in files:
            f_rel = os.path.join(rel_path, f)
            if f_rel in inventory:
                inventory[f_rel]["prod"] = True
            else:
                inventory[f_rel] = {"dev": False, "prod": True}

    only_dev = [k for k, v in inventory.items() if v["dev"] and not v["prod"]]
    only_prod = [k for k, v in inventory.items() if not v["dev"] and v["prod"]]
    common = [k for k, v in inventory.items() if v["dev"] and v["prod"]]
    
    return only_dev, only_prod, common

DEV_ROOT = r"C:\dev\Sonido_Liquido_V5"
PROD_ROOT = r"C:\dev\V5-LS\current"

def main():
    print("=== AUDITORÍA ESTRUCTURAL: DEV VS PROD ===")
    
    # Check Backend
    only_dev_b, only_prod_b, common_b = inventory_diff(
        os.path.join(DEV_ROOT, "backend"),
        os.path.join(PROD_ROOT, "backend")
    )
    
    print(f"\n[BACKEND] Comunes: {len(common_b)}")
    if only_dev_b:
        print(f" [!] Solo en DEV ({len(only_dev_b)}): {only_dev_b[:10]}...")
    if only_prod_b:
        print(f" [!] Solo en PROD ({len(only_prod_b)}): {only_prod_b[:10]}...")

    # Check Frontend
    only_dev_f, only_prod_f, common_f = inventory_diff(
        os.path.join(DEV_ROOT, "frontend", "src"),
        os.path.join(PROD_ROOT, "frontend", "src")
    )
    
    print(f"\n[FRONTEND/SRC] Comunes: {len(common_f)}")
    if only_dev_f:
        print(f" [!] Solo en DEV ({len(only_dev_f)}): {only_dev_f[:10]}...")
    if only_prod_f:
        print(f" [!] Solo en PROD ({len(only_prod_f)}): {only_prod_f[:10]}...")

if __name__ == "__main__":
    main()
