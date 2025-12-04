from sqlmodel import Session, SQLModel
from typing import Generator
# Importación absoluta corregida para evitar errores de paquete (ImportError)
from config import engine
# Importamos el módulo completo de modelos para que SQLModel los conozca
import models


def create_db_and_tables():
    """
    Inicializa la base de datos:
    Crea las tablas (Cliente, Empresa, Compra) si no existen.
    """
    print("--- 💡 Inicializando base de datos (SQLite/PostgreSQL)... ---")
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependencia de FastAPI para obtener una sesión de base de datos.
    Asegura que la sesión se cierre después de cada petición.
    """
    with Session(engine) as session:
        yield session