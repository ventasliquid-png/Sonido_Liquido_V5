import os
import datetime
import re

IDENTITY_FILE = ".gy_identity"
MEMORY_FILE = "MEMORIA_SESIONES.md"

def get_identity():
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE, 'r') as f:
            return f.read().strip()
    return "UNKNOWN"

def parse_sessions(content):
    # Regex to find session blocks. Assumes format:
    # ## Sesión [ID] - [DATE]
    # ... content ...
    # (End with next header or EOF)
    
    # We will split by "## Sesión"
    parts = re.split(r'(^## Sesión .*$)', content, flags=re.MULTILINE)
    
    sessions = []
    if not parts:
        return sessions
        
    # parts[0] is usually header/intro. parts[1] is header 1, parts[2] is body 1, etc.
    header_intro = parts[0]
    
    for i in range(1, len(parts), 2):
        header = parts[i]
        body = parts[i+1] if i+1 < len(parts) else ""
        
        # Extract Agent ID from header: "## Sesión Gy OF - 2025-11-27..."
        agent_match = re.search(r'Gy (\w+)', header)
        agent = agent_match.group(1) if agent_match else "UNKNOWN"
        
        sessions.append({
            'full_text': header + body,
            'agent': agent,
            'header': header,
            'body': body
        })
        
    return header_intro, sessions

def prune_sessions(sessions, current_agent):
    # Logic:
    # 1. Keep Current Chain (Continuous sessions of current_agent)
    # 2. Keep Last Session of Other Agent
    # 3. Keep Last Session of Current Agent BEFORE the Other Agent (Previous Own)
    
    kept = []
    other_found = False
    prev_own_found = False
    
    # Sessions are assumed to be passed in order: Newest First
    # But parse_sessions usually returns Top-Down (Newest First if file is prepended, or Oldest First if appended)
    # The user wants a log. Usually logs are appended. But for "Memory" usually we want to see latest first?
    # Let's assume the file structure is Newest Block at the TOP.
    
    for s in sessions:
        if s['agent'] == current_agent:
            if not other_found:
                kept.append(s) # Continuous Chain
            elif other_found and not prev_own_found:
                kept.append(s) # Previous Own
                prev_own_found = True
            # Else: Drop older own sessions
        else: # Other Agent
            if not other_found:
                kept.append(s) # Last Other
                other_found = True
            # Else: Drop older other sessions
            
    return kept

def start_session():
    identity = get_identity()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    new_block = f"""
## Sesión Gy {identity} - {now} (EN CURSO)
**Inicio:** {now}
**Estado:** Abierta

"""
    
    content = ""
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            
    # Prepend new session
    # We need to make sure we don't double-open if already open? 
    # For simplicity, we just prepend. The user can manually clean if needed or we rely on pruning.
    
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(new_block + "\n" + content)
        
    print(f"Sesión iniciada para Gy {identity}")

def end_session(summary):
    identity = get_identity()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    
    if not os.path.exists(MEMORY_FILE):
        print("No hay memoria de sesiones.")
        return

    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Update the current "EN CURSO" session
    # Find the first session block (which should be ours)
    # We'll just replace the first occurrence of "(EN CURSO)" and append summary
    
    if "(EN CURSO)" in content:
        content = content.replace("(EN CURSO)", f"(CERRADA {now})", 1)
        # Insert summary before the next "## Sesión" or end of first block
        # A simple way is to replace "**Estado:** Abierta" with "**Estado:** Cerrada\n**Cierre:** {now}\n\n### Resumen\n{summary}"
        content = content.replace("**Estado:** Abierta", f"**Estado:** Cerrada\n**Cierre:** {now}\n\n### Resumen\n{summary}", 1)
    
    # 2. Prune
    header_intro, sessions = parse_sessions(content)
    # parse_sessions returns list in order of appearance. 
    # If we prepended, sessions[0] is the one we just closed (Newest).
    
    kept_sessions = prune_sessions(sessions, identity)
    
    # Reconstruct file
    new_content = header_intro
    for s in kept_sessions:
        new_content += s['full_text']
        
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
        
    print(f"Sesión cerrada y memoria optimizada para Gy {identity}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Uso: python session_manager.py [start|end] [summary]")
        sys.exit(1)
        
    action = sys.argv[1]
    
    if action == "start":
        start_session()
    elif action == "end":
        summary = sys.argv[2] if len(sys.argv) > 2 else "Sin resumen."
        end_session(summary)
