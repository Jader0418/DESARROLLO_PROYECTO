import os
from sqlmodel import create_engine

# --- CONFIGURACIÓN DE BASE DE DATOS ---

# Si se usa en Render (Producción), Render proveerá la variable DATABASE_URL de PostgreSQL.
SUPABASE_DB_URL = "postgresql://postgres:[TU_PASS]@db.[TU_PROJECT_ID].supabase.co:5432/postgres"

# Usamos la URL de Supabase para forzar PostgreSQL. Cambia SUPABASE_DB_URL por tu conexión real.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite:///./distribuidora_datos.db" # Usamos SQLite por defecto para la estabilidad local
)

# Argumentos de conexión
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False
elif DATABASE_URL.startswith("postgresql"):
    connect_args["sslmode"] = "require"

# Crea el motor de la base de datos
engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args=connect_args
)