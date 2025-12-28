
import os

files = [
    "BITACORA_DEV.md",
    "BITACORA_OF_PENDIENTE.md",
    "BITACORA_DEV_20251215.md"
]

for f in files:
    print(f"<<<FILE_START:{f}>>>")
    try:
        if os.path.exists(f):
            with open(f, "r", encoding="utf-8", errors="replace") as file:
                print(file.read())
        else:
            print("FILE_NOT_FOUND")
    except Exception as e:
        print(f"ERROR: {e}")
    print(f"<<<FILE_END:{f}>>>")
