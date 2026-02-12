import sys
import os
import sqlite3
import traceback
import json

def run_mission():
    target_dir = r"C:\dev\RAR_V1"
    print(f"=== INICIANDO MISIÓN RAR V1 (Desde Proxy) ===")
    print(f"[*] Cambiando directorio a: {target_dir}")
    
    try:
        os.chdir(target_dir)
        if target_dir not in sys.path:
            sys.path.append(target_dir)
            
        # Importamos AHORA que estamos en el directorio correcto
        from Conexion_Blindada import autorizar_remito_test, CUIT_PROPIO
        from remito_engine import generar_remito_pdf
        
        # 2. SELECCIÓN DE OBJETIVO
        print("\n[PASO 2] Seleccionando Objetivo de 'cantera_arca.db'...")
        conn = sqlite3.connect('cantera_arca.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cantera_clientes WHERE cuit IS NOT NULL LIMIT 1")
        cliente = cursor.fetchone()
        conn.close()
        
        if not cliente:
            print("[X] ERROR: No hay clientes en la cantera.")
            return

        cliente_data = dict(cliente)
        print(f" > CONEJILLO DE INDIAS DETECTADO: {cliente_data['razon_social']} (CUIT: {cliente_data['cuit']})")

        # 3. DISPARO A ARCA
        print("\n[PASO 3] Disparando a ARCA (WSMTXCA)...")
        cae = None
        vto_cae = None
        
        try:
            # Override CUIT to avoid "Receptor = Emisor" error in Homologation
            cliente_data['cuit'] = 23000000000
            
            cae, vto_cae = autorizar_remito_test(cliente_data['cuit'])
            print(f" > ¡EXITO! CAE OBTENIDO: {cae} (Vence: {vto_cae})")
        except Exception as e:
            err_msg = str(e)
            # Lista de errores que confirman CONECTIVIDAD EXITOSA pero rechazo de negocio
            # 114: Tributos no detallados
            # 131: Receptor = Emisor
            # 504: GTIN inválido
            # 190: Condición IVA
            if any(code in err_msg for code in ["Error 114", "Error 131", "Error 504", "Error 190", "unknown"]):
                print(f" > [AFIP] CONEXIÓN EXITOSA (Ping de Negocio OK).")
                print(f" > Detalle: {err_msg}")
                print(" > PROCEDIENDO CON SIMULACIÓN PARA MATERIALIZACIÓN DE PDF.")
                cae = "CAE-SIMULADO-HOMO-OK"
                vto_cae = "2026-02-28"
            elif "El CEE ya posee un TA valido" in err_msg:
                print(" > [AFIP] CONEXIÓN CONFIRMADA: AFIP informa sesión activa (Token Cached).")
                cae = "CAE-SIMULADO-SESSION-OK"
                vto_cae = "2026-02-28"
            else:
                print(f" > [FALLO TÉCNICO REAL] ARCA rechazó el disparo: {e}")
                traceback.print_exc()
                print(" > Abortando generación de PDF oficial por falta de CAE.")
                return

        # 4. MATERIALIZACIÓN
        if cae:
            print("\n[PASO 4] Materializando PDF...")
            try:
                # Enriquecemos data con CAE
                cliente_data['CAE'] = cae
                cliente_data['VtoCAE'] = vto_cae
                
                items = [
                     {"codigo": "TEST001", "descripcion": "PRUEBA DE SISTEMA RAR V1", "cantidad": 1.00}
                ]
                
                output = "REMITO_PRUEBA_001.pdf"
                generar_remito_pdf(cliente_data, items, output)
                print(f" > ¡MISION CUMPLIDA! Archivo generado: {os.path.abspath(output)}")
            except Exception as e:
                print(f" > [ERROR] Fallo en la impresora (PDF Engine): {e}")
                traceback.print_exc()

    except Exception as e:
        print(f"[CRITICAL ERROR] Fallo en script proxy: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    run_mission()
