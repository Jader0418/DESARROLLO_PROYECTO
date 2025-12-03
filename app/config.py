from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """Carga la URL de la BD desde el archivo .env."""
    # Si no encuentra la variable, usará SQLite como fallback (solo desarrollo)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./local_temp.db")


settings = Settings()