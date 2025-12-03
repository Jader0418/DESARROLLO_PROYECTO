from sqlalchemy.orm import Session
from . import models, schemas
import pandas as pd
from sqlalchemy import func, text
import numpy as np

# --- Carga y Limpieza del Dataset (Requisito: Dataset Real) ---
DATASET_FILE = "ict_exports_data.csv"


def load_and_clean_dataset():
    """Carga el dataset real del Banco Mundial y lo prepara."""
    try:
        df = pd.read_csv(DATASET_FILE, skiprows=4)  # El CSV del Banco Mundial tiene 4 líneas de metadata

        # Renombra columnas clave
        df.rename(columns={'Country Name': 'Pais', 'Country Code': 'Codigo_Pais'}, inplace=True)

        # Selecciona columnas relevantes: País, Código, y años (de 1960 a 2024 en este caso)
        id_cols = ['Pais', 'Codigo_Pais']
        year_cols = [col for col in df.columns if str(col).isdigit() and 1960 <= int(col) <= 2024]

        # Desnormaliza los datos (wide-to-long)
        df_melted = df.melt(id_vars=id_cols, value_vars=year_cols,
                            var_name='Año', value_name='Porcentaje_Exportacion')

        # Limpieza: Convertir a numérico, ignorando valores '..' o NaN
        df_melted['Porcentaje_Exportacion'] = pd.to_numeric(df_melted['Porcentaje_Exportacion'], errors='coerce')
        df_melted.dropna(subset=['Porcentaje_Exportacion'], inplace=True)

        return df_melted

    except FileNotFoundError:
        print(f"ADVERTENCIA: Archivo {DATASET_FILE} no encontrado. Dashboard no funcionará.")
        return pd.DataFrame({'Pais': [], 'Año': [], 'Porcentaje_Exportacion': []})
    except Exception as e:
        print(f"Error al procesar el Dataset: {e}")
        return pd.DataFrame({'Pais': [], 'Año': [], 'Porcentaje_Exportacion': []})


DATASET_DF_CLEAN = load_and_clean_dataset()


def get_dataset_by_country(country_name: str):
    """Filtra los datos del dataset limpio para Chart.js."""
    data = DATASET_DF_CLEAN[DATASET_DF_CLEAN['Pais'] == country_name]

    # Ordena por año para la gráfica
    data = data.sort_values(by='Año')

    return {
        "years": data['Año'].tolist(),
        "exports": data['Porcentaje_Exportacion'].tolist(),
        "country": country_name
    }
# ----------------- Funciones CRUD y Reportes (Iguales a la versión anterior, pero limpias) -----------------

# (El resto del código CRUD, como create_product, get_all_products, get_top_countries, etc., es el mismo
# y cumple con el estándar modular.)
# ...