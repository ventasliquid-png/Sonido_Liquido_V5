import sqlite3
import os

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"

def final_audit():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 1. Identificar a Sergio Jofre y verificar sus 4 pilares
    query = """
    SELECT c.id, c.razon_social, c.flags_estado, c.condicion_iva_id, c.lista_precios_id, c.segmento_id,
           (SELECT COUNT(*) FROM domicilios d WHERE d.cliente_id = c.id AND d.es_fiscal = 1 AND d.activo = 1) as has_fiscal
    FROM clientes c
    WHERE c.razon_social LIKE '%Jofre%';
    """
    cursor.execute(query)
    row = cursor.fetchone()
    
    if row:
        cid, name, flags, iva, lista, seg, has_fiscal = row
        print(f"CLIENTE: {name}")
        print(f"FLAGS ACTUALES: {flags}")
        
        # Verificar 4 Pilares
        pillars_met = all([iva, lista, seg, has_fiscal > 0])
        print(f"PILORES MET: {pillars_met} (IVA:{bool(iva)}, LISTA:{bool(lista)}, SEG:{bool(seg)}, FISCAL:{has_fiscal>0})")
        
        if pillars_met:
            # LIMPIEZA MANUAL (Simulando Escudo Doble exitoso)
            new_flags = flags & ~1048576
            if new_flags != flags:
                cursor.execute("UPDATE clientes SET flags_estado = ? WHERE id = ?", (new_flags, cid))
                conn.commit()
                print(f"✅ SOBERANÍA RECLAMADA: Bit 20 eliminado. Nuevos Flags: {new_flags}")
            else:
                print("✅ ESTADO NOMINAL: El Bit 20 ya estaba limpio.")
        else:
            print("⚠️ ADVERTENCIA: No cumple los 4 pilares. El Bit 20 debe permanecer activo.")
            
    conn.close()

if __name__ == "__main__":
    final_audit()
