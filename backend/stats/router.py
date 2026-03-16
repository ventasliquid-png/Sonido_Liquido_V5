from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.core.database import get_db
from backend.clientes.models import Cliente
from backend.pedidos.models import Pedido
from backend.productos.models import Producto

router = APIRouter(
    prefix="/stats",
    tags=["Stats"]
)

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Returns aggregated stats for the Dashboard/Home.
    """
    
    # 1. Clientes
    total_clientes = db.query(Cliente).count()
    active_clientes = db.query(Cliente).filter(Cliente.activo == True).count()
    
    # 2. Productos
    total_productos = db.query(Producto).count()
    
    # 3. Pedidos
    total_pedidos = db.query(Pedido).count()
    pending_pedidos = db.query(Pedido).filter(Pedido.estado == 'PENDIENTE').count()
    
    return {
        "clientes": {
            "total": total_clientes,
            "active": active_clientes
        },
        "productos": {
            "total": total_productos
        },
        "pedidos": {
            "total": total_pedidos,
            "pending": pending_pedidos
        }
    }
