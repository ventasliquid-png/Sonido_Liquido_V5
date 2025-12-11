import pandas as pd
import os
import sys

# Configuración
DATA_DIR = r"c:\dev\Sonido_Liquido_V5\BUILD_PILOTO\data"
INPUT_CLIENTES = os.path.join(DATA_DIR, "clientes_candidatos.csv")
OUTPUT_CLIENTES = os.path.join(DATA_DIR, "clientes_limpios.csv")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    print("--- 🧹 LIMPIADOR INTERACTIVO V1 ---")
    if not os.path.exists(INPUT_CLIENTES):
        print(f"No encuentro {INPUT_CLIENTES}")
        return

    df = pd.read_csv(INPUT_CLIENTES)
    
    # Cargar progreso previo si existe
    processed_names = set()
    rows_clean = []
    if os.path.exists(OUTPUT_CLIENTES):
        df_prev = pd.read_csv(OUTPUT_CLIENTES)
        rows_clean = df_prev.to_dict('records')
        processed_names = set(df_prev['nombre_original'])
        print(f"Resumiendo sesión anterior... ({len(rows_clean)} ya procesados).")

    # Iterar
    total = len(df)
    count = 0
    
    try:
        for idx, row in df.iterrows():
            name = row['nombre']
            freq = row['frecuencia']
            cuit = row['cuit'] if not pd.isna(row['cuit']) else "S/D"
            
            if name in processed_names:
                count += 1
                continue

            clear_screen()
            print(f"Progreso: {count}/{total}")
            print("-" * 40)
            print(f"CLIENTE:  {name}")
            print(f"PEDIDOS:  {freq}")
            print(f"CUIT:     {cuit}")
            print("-" * 40)
            print("[ENTER]   Confirmar (Dejar igual)")
            print("[X]       Borrar / Ignorar")
            print("[A]       Agregar ALIAS (Ej: LABME)")
            print("[Texto]   Escribir nuevo nombre para renombrar")
            print("[Q]       Guardar y Salir")
            
            action = input("Acción > ").strip()
            
            if action.lower() == 'q':
                break
                
            final_name = name
            final_alias = ""
            final_status = "OK"
            
            if action.lower() == 'x':
                final_status = "IGNORAR"
            elif action.lower() == 'a':
                final_alias = input(f"Ingrese Alias para '{name}': ").strip().upper()
                print(f"✅ Alias asignado: {final_alias}")
                input("Presione ENTER para continuar...")
            elif action != "":
                final_name = action.upper() # Renombrar
            
            if final_status != "IGNORAR":
                rows_clean.append({
                    "nombre_original": name,
                    "nombre_final": final_name,
                    "alias": final_alias,
                    "cuit": cuit,
                    "frecuencia": freq
                })
                processed_names.add(name)
            
            count += 1
            
            # Guardado parcial cada 5
            if count % 5 == 0:
                pd.DataFrame(rows_clean).to_csv(OUTPUT_CLIENTES, index=False)

    except KeyboardInterrupt:
        print("\nInterrumpido por usuario.")
    
    # Guardado final
    pd.DataFrame(rows_clean).to_csv(OUTPUT_CLIENTES, index=False)
    print(f"\n✅ Guardado en: {OUTPUT_CLIENTES}")

if __name__ == "__main__":
    main()
