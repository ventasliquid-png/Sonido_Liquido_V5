from fastapi import APIRouter

router = APIRouter(
    prefix="/facturacion",
    tags=["Facturación (Soberana)"],
    responses={404: {"description": "Not found"}},
)
