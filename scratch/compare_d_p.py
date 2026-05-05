import os
import filecmp

def print_diff(dc):
    for name in dc.diff_files:
        print(f"DIFF: {os.path.relpath(os.path.join(dc.left, name), dir1)}")
    for name in dc.left_only:
        if name not in ["__pycache__", "venv", ".git", "node_modules", "dist", ".gemini"]:
            print(f"ONLY D: {os.path.relpath(os.path.join(dc.left, name), dir1)}")
    for name in dc.right_only:
        if name not in ["__pycache__", "venv", ".git", "node_modules", "dist", ".gemini"]:
            print(f"ONLY P: {os.path.relpath(os.path.join(dc.right, name), dir1)}")
    for sub_name, sub_dc in dc.subdirs.items():
        if sub_name not in ["__pycache__", "venv", ".git", "node_modules", "dist", ".gemini"]:
            print_diff(sub_dc)

dir1 = r'c:\dev\Sonido_Liquido_V5\backend'
dir2 = r'c:\dev\V5-LS\current\backend'
dc = filecmp.dircmp(dir1, dir2)
print_diff(dc)
