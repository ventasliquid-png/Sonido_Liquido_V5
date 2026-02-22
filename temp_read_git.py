import os, zlib

repo = r"C:\dev\RAR_V1"
branch = "rescate-cache-lupa"
file_path = b"Conexion_Blindada.py\x00"

with open(os.path.join(repo, ".git", "refs", "heads", branch), "r") as f:
    commit_hash = f.read().strip()

def read_object(sha):
    path = os.path.join(repo, ".git", "objects", sha[:2], sha[2:])
    with open(path, "rb") as f:
        return zlib.decompress(f.read())

commit_data = read_object(commit_hash).decode('utf-8')
tree_hash = commit_data.split("tree ")[1].split("\n")[0]
tree_data = read_object(tree_hash)

idx = tree_data.find(file_path)
if idx != -1:
    sha = tree_data[idx + len(file_path) : idx + len(file_path) + 20].hex()
    blob_data = read_object(sha)
    content = blob_data.split(b'\x00', 1)[1].decode('utf-8')
    with open(r"c:\dev\Sonido_Liquido_V5\temp_cache_lupa.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Extracted")
else:
    print("Not found")
