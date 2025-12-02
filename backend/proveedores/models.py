import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from backend.core.database import Base

class Proveedor(Base):
    __tablename__ = "proveedores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    razon_social = Column(String, nullable=False, index=True)
    cuit = Column(String, nullable=True, unique=True, index=True)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    activo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Proveedor(razon_social='{self.razon_social}')>"
