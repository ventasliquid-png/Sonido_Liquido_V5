import sys
import os
from decimal import Decimal
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.getcwd())

from backend.core.database import SessionLocal, engine, Base
from backend.pedidos.pricing import PricingEngine, SCENARIOS
from backend.productos.models import Producto, ProductoCosto
from backend.clientes.models import Cliente, ListaPrecios

def war_game_v3():
    print("\n--- 🛡️ WAR GAME 3.0: PRICING ENGINE VERIFICATION 🛡️ ---")
    print("Objetivo: Verificar matemática 'Roca y Máscara' en escenarios hostiles.\n")

    db = SessionLocal()
    try:
        # 1. SETUP: Crear Datos de Prueba (Temporales / Mockeados en Memoria si es posible, pero usaremos DB real y rollback)
        
        # Producto A: Standard (Costo 1000, Margen 30%) -> Roca = 1300
        prod_std = Producto(nombre="TEST_STD", rubro_id=1, sku=99001)
        db.add(prod_std)
        db.flush()
        
        costo_std = ProductoCosto(
            producto_id=prod_std.id, 
            costo_reposicion=1000, 
            margen_mayorista=30,  # 30%
            precio_fijo_override=None
        )
        db.add(costo_std)

        # Producto B: Override (Costo 1000, Override 2000) -> Roca = 2000 (Ignora margen)
        prod_ovr = Producto(nombre="TEST_OVERRIDE", rubro_id=1, sku=99002)
        db.add(prod_ovr)
        db.flush()
        
        costo_ovr = ProductoCosto(
            producto_id=prod_ovr.id, 
            costo_reposicion=1000, 
            margen_mayorista=30,
            precio_fijo_override=2000 
        )
        db.add(costo_ovr)

        # Lista Descuento 20% (Coef 0.80)
        lista_20 = ListaPrecios(nombre="LISTA TEST -20", coeficiente=0.80)
        db.add(lista_20)
        db.flush()

        # Cliente 1: Mayorista Fiscal (K=1.21) + Lista Base (Coef 1.0)
        cli_fiscal = Cliente(razon_social="CLI_FISCAL", cuit="30000000001", estrategia_precio="MAYORISTA_FISCAL")
        db.add(cli_fiscal)
        
        # Cliente 2: Mayorista X (K=1.105) + Lista -20%
        cli_x_desc = Cliente(
            razon_social="CLI_X_DESC", 
            cuit="30000000002", 
            estrategia_precio="MAYORISTA_X",
            lista_precios_id=lista_20.id
        )
        db.add(cli_x_desc)

        # Cliente 3: MELI (Markup 1.40 + 2100 Fijo)
        cli_meli = Cliente(razon_social="CLI_MELI", cuit="30000000003", estrategia_precio="MELI_CLASICO")
        db.add(cli_meli)

        db.commit() # Commit needed to query them inside engine logic properly? Or flush is enough?
        # Engine uses new query, so commit makes them visible to new sessions if needed, but safe here.
        # Actually Engine uses `self.db`, so passing current session is best.
        
        engine_logic = PricingEngine(db)

        # --- TEST 1: MAYORISTA FISCAL (STANDARD) ---
        print("\n[TEST 1] Mayorista Fiscal (Costo 1000 + 30% = 1300 Roca)")
        # Target: 1300 * 1.21 = 1573
        # Redondeo: >1000 -> 100. -> 1600
        # Lista Coef: 1.0 -> Vidriera 1600
        res1 = engine_logic.cotizar_producto(str(cli_fiscal.id), prod_std.id)
        print(f" > Resultado SDK: {res1['precio_final_sugerido']} (Esperado ~1600)")
        print(f" > Detalle: {res1['info_debug']}")
        assert res1['precio_final_sugerido'] == 1600.0, f"Fallo Test 1: {res1['precio_final_sugerido']}"

        # --- TEST 2: MAYORISTA X CON DESCUENTO (STANDARD) ---
        print("\n[TEST 2] Mayorista X + 20% Off (Costo 1000 + 30% = 1300 Roca)")
        # Target: 1300 * 1.105 = 1436.5
        # Redondeo Target: 1400.
        # Mascara: Vidriera = 1400 / 0.80 = 1750
        # Precio Final: 1750 * 0.80 = 1400.
        res2 = engine_logic.cotizar_producto(str(cli_x_desc.id), prod_std.id)
        print(f" > Resultado SDK: $ {res2['precio_final_sugerido']} (Lista {res2['precio_lista_sugerido']} - 20%)")
        assert res2['precio_final_sugerido'] == 1400.0, f"Fallo Test 2: {res2['precio_final_sugerido']}"

        # --- TEST 3: OVERRIDE MANUAL (PRODUCTO OVERRIDE) ---
        print("\n[TEST 3] Override Manual (Fijo 2000 -> Roca 2000)")
        # Cliente Fiscal
        # Target: 2000 * 1.21 = 2420
        # Redondeo: 2400
        res3 = engine_logic.cotizar_producto(str(cli_fiscal.id), prod_ovr.id)
        print(f" > Resultado SDK: {res3['precio_final_sugerido']} (Esperado 2400 confirmando Override)")
        assert res3['precio_final_sugerido'] == 2400.0 and res3['origen'] == 'OVERRIDE', "Fallo Test 3"

        # --- TEST 4: MELI (IMPUESTO DESPOTICO) ---
        print("\n[TEST 4] MELI Clásico (Roca 1300)")
        # Base Calc = 1300 * 1.21 (IVA) = 1573
        # Markup = (1573 * 1.40) + 2100 = 2202.2 + 2100 = 4302.2
        # Redondeo: 4300
        res4 = engine_logic.cotizar_producto(str(cli_meli.id), prod_std.id)
        print(f" > Resultado SDK: {res4['precio_final_sugerido']} (Esperado ~4300)")
        assert res4['precio_final_sugerido'] == 4300.0, f"Fallo Test 4: {res4['precio_final_sugerido']}"

        print("\n✅ V5 PRICING ENGINE: TODOS LOS SISTEMAS OPERATIVOS.")
        
    except Exception as e:
        print(f"\n❌ ERROR CRITICO EN WAR GAME: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # CLEANUP: No queremos basura en la DB real del piloto
        print("\nLimpiando campo de batalla...")
        # Rollback anula todo lo creado en esta sesion
        db.rollback() 
        db.close()

if __name__ == "__main__":
    war_game_v3()
