from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


# Modelo 1: Producto Tecnológico (Entidad principal + Multimedia)
class ProductoTecnologico(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    categoria = Column(String)
    precio_unitario = Column(Float)
    imagen_url = Column(String)  # URL de la imagen (Cloudinary o /static)

    exportaciones = relationship("RegistroExportacion", back_populates="producto")


# Modelo 2: Registro de Exportación (Entidad secundaria + Relación)
class RegistroExportacion(Base):
    __tablename__ = "exportaciones"

    id = Column(Integer, primary_key=True, index=True)
    cantidad = Column(Integer)
    pais_destino = Column(String)
    fecha_venta = Column(DateTime(timezone=True), server_default=func.now())

    producto_id = Column(Integer, ForeignKey("productos.id"))

    producto = relationship("ProductoTecnologico", back_populates="exportaciones")