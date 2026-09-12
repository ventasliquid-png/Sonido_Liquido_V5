import os
import sys
import argparse
from datetime import datetime, timedelta

# Asegurar que el entorno reconozca el proyecto base para importar los módulos de V5
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.core.database import SessionLocal

# Mapeo Universal: mismo orden que backend/main.py. Sin cargar todos los modelos antes
# de consultar, SQLAlchemy no resuelve las relaciones declaradas como string
# (ej. VinculoGeografico -> 'Domicilio') y la consulta falla al inicializar mappers.
import backend.auth.models  # noqa: F401
import backend.maestros.models  # noqa: F401
import backend.logistica.models  # noqa: F401
import backend.contactos.models  # noqa: F401
import backend.clientes.models  # noqa: F401
import backend.productos.models  # noqa: F401
import backend.pedidos.models  # noqa: F401
import backend.proveedores.models  # noqa: F401
import backend.agenda.models  # noqa: F401
import backend.remitos.models  # noqa: F401
import backend.facturacion.models  # noqa: F401
import backend.ingesta.models  # noqa: F401
import backend.core.models  # noqa: F401
from sqlalchemy.orm import configure_mappers
configure_mappers()

from backend.pedidos.models import Pedido
from backend.pedidos.constants import PedidoFlags as PF

def run_audit(days_limit: int):
    print(f"\n=======================================================")
    print(f"🕵️‍♂️ SABUESO AUDITOR: FRACTURAS MELI / ORIGEN FACTURA")
    print(f"=======================================================\n")

    db = SessionLocal()
    try:
        # Extraer pedidos que NACIERON DE INGESTA (Bit 38 encendido)
        # Y que NO ESTÁN CUMPLIDOS NI ANULADOS (O sea, siguen vivos como PENDIENTES o PRESUPUESTOS)
        time_threshold = datetime.now() - timedelta(days=days_limit)
        
        query = db.query(Pedido).filter(
            Pedido.flags_estado.op('&')(PF.ORIGEN_FACTURA.value) == PF.ORIGEN_FACTURA.value,
            Pedido.flags_estado.op('&')(PF.ES_CUMPLIDO.value | PF.ES_ANULADO.value) == 0,
            Pedido.fecha <= time_threshold
        ).order_by(Pedido.fecha.asc())

        resultados = query.all()

        if not resultados:
            print(f"✅ EXCELENTE: No se encontraron pedidos atascados (con más de {days_limit} días) nacidos desde Ingesta.")
        else:
            print(f"⚠️ ATENCIÓN: Se encontraron {len(resultados)} pedidos estancados nacidos desde Facturas (MELI / Atrasadas):\n")
            
            print(f"{'ID':<6} | {'FECHA':<12} | {'CLIENTE':<35} | {'ESTADO':<12} | {'TOTAL':<12}")
            print("-" * 85)
            for p in resultados:
                cliente_nombre = p.cliente.razon_social[:33] + ".." if len(p.cliente.razon_social) > 35 else p.cliente.razon_social
                print(f"#{p.id:<4} | {p.fecha.strftime('%Y-%m-%d'):<12} | {cliente_nombre:<35} | {p.estado:<12} | ${p.total:,.2f}")
            
            print("-" * 85)
            print("\n🔍 ACCIÓN REQUERIDA: Revise estos pedidos. Es probable que la mercadería haya sido entregada físicamente y el pedido haya quedado 'huérfano' en el sistema, o que haya inconsistencias en el despacho.")

    except Exception as e:
        print(f"❌ Error durante la auditoría: {e}")
    finally:
        db.close()
        print("\n[Auditoría Finalizada]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audita pedidos huérfanos generados a partir de Facturas.")
    parser.add_argument("--dias", type=int, default=3, help="Cantidad de días de tolerancia antes de reportar el pedido (Por defecto: 3)")
    args = parser.parse_args()

    run_audit(args.dias)
