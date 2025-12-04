from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime


# --- MODELO BASE ---
class BaseModel(SQLModel):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


# --- 1. MODELO CLIENTE (SIN CAMBIOS ESTRUCTURALES) ---
class ClienteBase(BaseModel):
    nombre: str = Field(index=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    pais: str
    ciudad: str
    direccion_envio: str
    telefono: Optional[str] = None


class Cliente(ClienteBase, table=True):
    compras: List["Compra"] = Relationship(back_populates="cliente")


class ClienteCreate(ClienteBase): pass


class ClienteRead(ClienteBase): id: int


class ClienteUpdate(SQLModel):
    nombre: Optional[str] = None
    email: Optional[str] = None
    password_hash: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    direccion_envio: Optional[str] = None
    telefono: Optional[str] = None


# --- 2. MODELO EMPRESA (PROVEEDOR CHINO) (ACTUALIZACIÓN) ---
class EmpresaBase(BaseModel):
    nombre_empresa: str = Field(unique=True, index=True)
    contacto_nombre: str
    contacto_email: str
    pais_origen: str = "China"
    tipo_producto: str
    imagen_url: Optional[str] = None


class Empresa(EmpresaBase, table=True):
    compras: List["Compra"] = Relationship(back_populates="empresa")
    # ¡NUEVA Relación! Una Empresa tiene muchos Productos
    productos: List["Producto"] = Relationship(back_populates="empresa")


class EmpresaCreate(EmpresaBase): pass


class EmpresaRead(EmpresaBase): id: int


class EmpresaUpdate(SQLModel):
    nombre_empresa: Optional[str] = None
    contacto_nombre: Optional[str] = None
    contacto_email: Optional[str] = None
    tipo_producto: Optional[str] = None
    imagen_url: Optional[str] = None


# --- 2.1. NUEVO MODELO PRODUCTO ---
class ProductoBase(SQLModel):
    empresa_id: int = Field(foreign_key="empresa.id")

    nombre: str = Field(index=True)
    descripcion: Optional[str] = None
    precio_usd: float  # Precio unitario del proveedor (USD)
    stock: int = Field(default=0)  # Stock disponible para importar
    imagen_url: Optional[str] = None  # URL de la imagen del producto (Supabase)


class Producto(ProductoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    empresa: Empresa = Relationship(back_populates="productos")
    compras: List["Compra"] = Relationship(back_populates="producto")


class ProductoRead(ProductoBase):
    id: int


# --- 3. MODELO COMPRA (PEDIDO/IMPORTACIÓN) (ACTUALIZACIÓN) ---
class CompraBase(BaseModel):
    cliente_id: int = Field(foreign_key="cliente.id")
    empresa_id: int = Field(foreign_key="empresa.id")
    producto_id: int = Field(foreign_key="producto.id")  # NUEVA CLAVE

    cantidad: int
    precio_total: float  # El costo total de importación
    estado_pedido: str = Field(default="Pendiente", index=True)

    margen_estimado: float = Field(default=0.0)

    fecha_envio_estimada: Optional[datetime] = None
    tracking_number: Optional[str] = None


class Compra(CompraBase, table=True):
    cliente: Cliente = Relationship(back_populates="compras")
    empresa: Empresa = Relationship(back_populates="compras")
    producto: Producto = Relationship(back_populates="compras")  # NUEVA RELACIÓN


class CompraCreate(CompraBase): pass


class CompraRead(CompraBase): id: int


class CompraUpdate(SQLModel):
    estado_pedido: Optional[str] = None
    fecha_envio_estimada: Optional[datetime] = None
    tracking_number: Optional[str] = None


class CompraReadWithRelations(CompraRead):
    cliente: ClienteRead
    empresa: EmpresaRead
    producto: ProductoRead