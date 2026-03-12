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
    total_clientes = db.query(func.count(Cliente.id)).scalar()
    active_clientes = db.query(func.count(Cliente.id)).filter(Cliente.activo == True).scalar()
    
    # 2. Productos
    total_productos = db.query(func.count(Producto.id)).scalar()
    
    # 3. Pedidos
    total_pedidos = db.query(func.count(Pedido.id)).scalar()
    pending_pedidos = db.query(func.count(Pedido.id)).filter(Pedido.estado == 'PENDIENTE').scalar()
    
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
