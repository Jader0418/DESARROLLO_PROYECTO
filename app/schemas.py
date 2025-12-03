from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Esquemas de Base y Creación para Producto
class ProductoBase(BaseModel):
    nombre: str = Field(..., min_length=3)
    categoria: str
    precio_unitario: float = Field(..., gt=0)

class ProductoCreate(ProductoBase):
    pass # Puede expandirse si se maneja la imagen en la API

# Esquemas para Exportación
class ExportacionBase(BaseModel):
    cantidad: int = Field(..., gt=0)
    pais_destino: str = Field(..., min_length=2)
    producto_id: int

class ExportacionCreate(ExportacionBase):
    pass

# Esquema de Respuesta (ORM mode es para FastAPI)
class ProductoResponse(ProductoBase):
    id: int
    imagen_url: Optional[str] = None
    class Config:
        orm_mode = True