import sqlite3
import os

DB_PATH = r"c:\dev\Sonido_Liquido_V5\pilot_v5x.db"
RESULT_PATH = r"c:\dev\Sonido_Liquido_V5\scripts\migration_results.txt"

def pure_sql_migration():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        with open(RESULT_PATH, "w", encoding="utf-8") as f:
            f.write("🚀 INICIANDO MIGRACIÓN SQL PAZ BINARIA V15.1...\n")
            
            # 1. Resetear Bits 19 y 20
            cursor.execute("UPDATE clientes SET flags_estado = flags_estado & ~1572864")
            
            # 2. Identificar Consumidor Final
            cursor.execute("SELECT id FROM condiciones_iva WHERE UPPER(nombre) LIKE '%CONSUMIDOR FINAL%'")
            cf_ids = [r[0] for r in cursor.fetchall()]
            cf_tuple = str(tuple(cf_ids)).replace(',)', ')') if len(cf_ids) > 1 else f"('{cf_ids[0]}')" if cf_ids else "('---')"

            # 3. Identificar clientes con Domicilio Fiscal Activo
            cursor.execute("SELECT cliente_id FROM domicilios WHERE es_fiscal = 1 AND activo = 1 GROUP BY cliente_id")
            active_fiscal_ids = [r[0] for r in cursor.fetchall()]
            fiscal_tuple = str(tuple(active_fiscal_ids)).replace(',)', ')') if len(active_fiscal_ids) > 1 else f"('{active_fiscal_ids[0]}')" if active_fiscal_ids else "('---')"

            # --- REGLA 1: POWER_PINK (Bit 19 - 524288) ---
            generic_cuits = "('00000000000', '11111111119', '11111111111', '99999999999')"
            update_19_query = f"""
            UPDATE clientes 
            SET flags_estado = flags_estado | 524288 
            WHERE 
                ((flags_estado & 15) IN (9, 11) AND lista_precios_id IS NOT NULL AND segmento_id IS NOT NULL AND id IN {fiscal_tuple})
                OR (cuit IN {generic_cuits} OR condicion_iva_id IN {cf_tuple})
            """
            cursor.execute(update_19_query)
            
            # --- REGLA 2: ARCA_OK (Bit 20 - 1048576) ---
            update_20_query = f"""
            UPDATE clientes 
            SET flags_estado = flags_estado | 1048576 
            WHERE 
                (flags_estado & 15) IN (13, 15) 
                AND condicion_iva_id IS NOT NULL 
                AND lista_precios_id IS NOT NULL 
                AND segmento_id IS NOT NULL 
                AND id IN {fiscal_tuple}
                AND cuit NOT IN {generic_cuits}
                AND condicion_iva_id NOT IN {cf_tuple}
            """
            cursor.execute(update_20_query)

            conn.commit()
            
            # CENSO FINAL
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE (flags_estado & 524288) AND (flags_estado & 1048576)")
            hybrid = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE (flags_estado & 524288) AND NOT (flags_estado & 1048576)")
            pink = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE NOT (flags_estado & 524288) AND (flags_estado & 1048576)")
            white = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM clientes WHERE NOT (flags_estado & 524288) AND NOT (flags_estado & 1048576)")
            yellow = cursor.fetchone()[0]

            res_text = f"\n📊 CENSO FINAL SQL V15.1:\n"
            res_text += f"🌸 Soberanos Rosas (Solo 19): {pink}\n"
            res_text += f"⚪ Soberanos Blancos (Solo 20): {white}\n"
            res_text += f"🧬 Híbridos / Evolucionados (19+20): {hybrid}\n"
            res_text += f"🟡 Pendientes (Amarillo): {yellow}\n"
            res_text += f"\n✅ MIGRACIÓN SQL COMPLETADA. PIN 1974.\n"
            f.write(res_text)
            print(res_text)

    except Exception as e:
        print(f"❌ ERROR SQL: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    pure_sql_migration()
