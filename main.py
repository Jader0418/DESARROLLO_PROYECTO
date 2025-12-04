from typing import Annotated, List, Optional
from contextlib import asynccontextmanager
from decimal import Decimal
from collections import defaultdict
import datetime
import os

from fastapi import (
    FastAPI, Depends, HTTPException, status, Request
)
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse
from sqlmodel import Session, select

from database import create_db_and_tables, get_session
import models

# ----------------------------------------------------------------------
# CONFIGURACIÓN INICIAL
# ----------------------------------------------------------------------

SessionDep = Annotated[Session, Depends(get_session)]
templates = Jinja2Templates(directory="templates")
UPLOAD_DIR = "static/images"  # Mantenido para asegurar que la carpeta exista


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida que crea las tablas al iniciar el servidor y asegura el directorio estático.
    """
    create_db_and_tables()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    yield


app = FastAPI(
    title="API de Importaciones Distribuidora JS",
    description="Sistema CRUD, Multimedia y Dashboard para gestión de importaciones.",
    version="1.0.0",
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------------------------------------------------
# RUTAS DE HTML (VISTAS)
# ----------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, tags=["0. VISTAS"])
def read_index_html(request: Request):
    """ Muestra la página principal con formularios Cliente/Empresa y Catálogo. """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"titulo": "Portal Principal"}
    )


@app.get("/dashboard/", response_class=HTMLResponse, tags=["0. VISTAS"])
def get_dashboard_html(request: Request):
    """ Muestra la página del dashboard con gráficos y reportes. """
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"titulo": "Dashboard de Rendimiento B2B"}
    )


@app.get("/clientes/listado", response_class=HTMLResponse, tags=["0. VISTAS"])
def read_clientes_html(request: Request, session: SessionDep):
    """ Muestra la lista de clientes. """
    clientes = session.exec(select(models.Cliente)).all()
    return templates.TemplateResponse(
        request=request,
        name="listado_clientes.html",
        context={"clientes": clientes, "titulo": "Listado de Clientes"}
    )


@app.get("/empresas/listado", response_class=HTMLResponse, tags=["0. VISTAS"])
def read_empresas_html(request: Request, session: SessionDep, query: Optional[str] = None):
    """ Muestra la lista de empresas con funcionalidad de búsqueda. """
    statement = select(models.Empresa)
    if query:
        statement = statement.where(
            models.Empresa.nombre_empresa.contains(query) |
            models.Empresa.tipo_producto.contains(query)
        )
    empresas = session.exec(statement).all()
    return templates.TemplateResponse(
        request=request,
        name="empresas.html",
        context={"empresas": empresas, "titulo": "Listado de Proveedores", "query": query}
    )


@app.get("/compras/listado", response_class=HTMLResponse, tags=["0. VISTAS"])
def read_compras_html(request: Request, session: SessionDep):
    """ Muestra la lista de compras con relaciones. """
    compras = session.exec(select(models.Compra)).all()
    return templates.TemplateResponse(
        request=request,
        name="compras.html",
        context={"compras": compras, "titulo": "Listado de Compras (Pedidos)"}
    )


@app.get("/compras/registro", response_class=HTMLResponse, tags=["0. VISTAS"])
def get_compra_registro_html(request: Request):
    """ Muestra el formulario HTML interactivo para registrar una nueva orden de compra. """
    return templates.TemplateResponse(
        request=request,
        name="registro_compra.html",
        context={"titulo": "Registro de Orden de Compra"}
    )


@app.get("/productos/registro", response_class=HTMLResponse, tags=["0. VISTAS"])
def get_producto_registro_html(request: Request):
    """ Muestra el formulario HTML para registrar un nuevo producto. """
    return templates.TemplateResponse(
        request=request,
        name="registro_producto.html",
        context={"titulo": "Registro de Producto"}
    )


# ----------------------------------------------------------------------
# RUTAS DE API (JSON) - CRUD
# ----------------------------------------------------------------------

# --- Clientes ---
@app.post("/clientes/", response_model=models.ClienteRead, status_code=status.HTTP_201_CREATED, tags=["1. API CRUD"])
def create_cliente(cliente: models.ClienteCreate, session: SessionDep):
    """ [CREATE] Registra un nuevo cliente. """
    db_cliente = models.Cliente.model_validate(cliente)
    session.add(db_cliente)
    session.commit()
    session.refresh(db_cliente)
    return db_cliente


# --- Producto CRUD ---
@app.post("/productos/", tags=["1. API CRUD"])
def create_producto(producto: models.ProductoBase, session: SessionDep):
    """ [CREATE] Registra un nuevo producto. """
    if not session.get(models.Empresa, producto.empresa_id):
        raise HTTPException(status_code=404, detail="Empresa ID no encontrada para registrar el producto.")

    db_producto = models.Producto.model_validate(producto)
    session.add(db_producto)
    session.commit()
    session.refresh(db_producto)
    return db_producto


@app.get("/productos/{empresa_id}", tags=["1. API CRUD"])
def read_productos_by_empresa(empresa_id: int, session: SessionDep):
    """ [READ] Obtiene la lista de productos disponibles de una empresa específica (usado por JS interactivo). """
    productos = session.exec(
        select(models.Producto).where(models.Producto.empresa_id == empresa_id)
    ).all()
    return productos


# --- Empresas ---
@app.post("/empresas/", response_model=models.EmpresaRead, status_code=status.HTTP_201_CREATED, tags=["1. API CRUD"])
def create_empresa(empresa: models.EmpresaCreate, session: SessionDep):
    """ [CREATE] Registra una nueva empresa. Recibe la URL de Supabase. """
    db_empresa = models.Empresa.model_validate(empresa)
    session.add(db_empresa)
    session.commit()
    session.refresh(db_empresa)
    return db_empresa


# --- Compras (Lógica de negocio actualizada) ---
@app.post("/compras/", response_model=models.CompraRead, status_code=status.HTTP_201_CREATED, tags=["1. API CRUD"])
def create_compra(compra: models.CompraCreate, session: SessionDep):
    """
    [CREATE] Registra una nueva Compra.
    Regla de Negocio: Validar FK, obtener precio del Producto (Data Enriquecida) y calcular Margen.
    """
    # 1. Validación de Claves Foráneas
    cliente = session.get(models.Cliente, compra.cliente_id)
    producto = session.get(models.Producto, compra.producto_id)

    if not cliente:
        raise HTTPException(status_code=404, detail=f"Cliente ID {compra.cliente_id} no encontrado.")
    if not producto:
        raise HTTPException(status_code=404, detail=f"Producto ID {compra.producto_id} no encontrado.")

    # Regla de Consistencia: La Empresa de la Compra debe ser la misma que la del Producto
    if compra.empresa_id != producto.empresa_id:
        raise HTTPException(status_code=400, detail="El Producto no pertenece a la Empresa seleccionada.")

    # 2. Cálculo de Margen y Costo Total (Data Enriquecida)
    costo_unitario = Decimal(producto.precio_usd)
    precio_total_importacion = costo_unitario * Decimal(compra.cantidad)
    margen_estimado = precio_total_importacion * Decimal('0.35')  # 35% de margen

    # 3. Creación y Guardado
    db_compra = models.Compra.model_validate(compra)
    db_compra.precio_total = float(precio_total_importacion)
    db_compra.margen_estimado = float(margen_estimado)

    session.add(db_compra)
    session.commit()
    session.refresh(db_compra)
    return db_compra


# ----------------------------------------------------------------------
# RUTAS DE DASHBOARD Y REPORTES
# ----------------------------------------------------------------------

@app.get("/api/reportes/", tags=["2. REPORTES"])
def get_report_data(session: SessionDep):
    """ Calcula y retorna los datos clave de negocio para el dashboard. """
    compras = session.exec(select(models.Compra)).all()

    # ... (Lógica de reporte se mantiene) ...
    total_costo_importacion = Decimal(0)
    total_margen = Decimal(0)
    compras_por_proveedor = defaultdict(lambda: {'nombre': '', 'total_costo': Decimal(0)})

    for compra in compras:
        costo = Decimal(compra.precio_total or 0)
        margen = Decimal(compra.margen_estimado or 0)

        total_costo_importacion += costo
        total_margen += margen

        empresa = session.get(models.Empresa, compra.empresa_id)
        nombre_proveedor = empresa.nombre_empresa if empresa else f"ID {compra.empresa_id}"

        compras_por_proveedor[compra.empresa_id]['total_costo'] += costo
        compras_por_proveedor[compra.empresa_id]['nombre'] = nombre_proveedor

    proveedores_labels = [data['nombre'] for data in compras_por_proveedor.values()]
    costos_data = [float(data['total_costo']) for data in compras_por_proveedor.values()]

    return {
        "hallazgos": {
            "total_costo": float(total_costo_importacion),
            "total_margen_estimado": float(total_margen),
            "total_ventas_estimadas": float(total_costo_importacion + total_margen),
            "cantidad_pedidos": len(compras)
        },
        "grafico_proveedores": {
            "labels": proveedores_labels,
            "data": costos_data,
        }
    }



@app.get("/clientes/registro", response_class=HTMLResponse, tags=["0. VISTAS"])
def read_clientes_registro_html(request: Request, session: SessionDep):
    """
    [NUEVA RUTA SOLICITADA] Muestra la lista de clientes.
    (Sirve la misma plantilla que /clientes/listado para cumplir con el requisito).
    """
    clientes = session.exec(select(models.Cliente)).all()
    return templates.TemplateResponse(
        request=request,
        name="listado_clientes.html",
        context={"clientes": clientes, "titulo": "Listado de Clientes (Ruta Registro)"}
    )

@app.get("/empresas/registro", response_class=HTMLResponse, tags=["0. VISTAS"])
def read_empresas_registro_html(request: Request, session: SessionDep, query: Optional[str] = None):
    """
    [NUEVA RUTA SOLICITADA] Muestra la lista de empresas/proveedores.
    (Sirve la misma plantilla que /empresas/listado, incluyendo la lógica de búsqueda).
    """
    statement = select(models.Empresa)
    if query: # Lógica de búsqueda inmersa
        statement = statement.where(
            models.Empresa.nombre_empresa.contains(query) |
            models.Empresa.tipo_producto.contains(query)
        )
    empresas = session.exec(statement).all()
    return templates.TemplateResponse(
        request=request,
        name="empresas.html",
        context={"empresas": empresas, "titulo": "Listado de Proveedores (Ruta Registro)", "query": query}
    )

