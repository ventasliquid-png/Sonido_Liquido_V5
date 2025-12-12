import os

env_path = ".env"
new_content = []
found = False

if os.path.exists(env_path):
    with open(env_path, "r") as f:
        lines = f.readlines()
        for line in lines:
            if line.startswith("DATABASE_URL="):
                new_content.append('DATABASE_URL="sqlite:///./pilot.db"\n')
                new_content.append('# OLD_' + line)
                found = True
            else:
                new_content.append(line)

if not found:
    new_content.append('DATABASE_URL="sqlite:///./pilot.db"\n')

with open(env_path, "w") as f:
    f.writelines(new_content)

print("✅ .env actualizado a SQLite (pilot.db)")
