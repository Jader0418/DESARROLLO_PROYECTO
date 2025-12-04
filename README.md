# 🚀 Distribuidora JS | Plataforma de Gestión de Importaciones B2B

## ✨ Visión General del Proyecto

El sistema **Distribuidora JS** es una solución web de **Business-to-Business (B2B)** diseñada para modernizar la cadena de suministro en el sector tecnológico. La plataforma actúa como un **agregador digital**, simplificando la conexión entre **clientes mayoristas en Colombia** y **proveedores fabricantes en China**.

El objetivo es proporcionar **transparencia total en costos** y una gestión centralizada de pedidos, eliminando las complejidades logísticas y financieras de las importaciones.

| Característica Clave | Tecnología / Implementación |
| :--- | :--- |
| **Backend Core** | **FastAPI** (Python 3.11+) | Servicio web de alto rendimiento. |
| **Persistencia de Datos** | **SQLModel** (ORM) / PostgreSQL o SQLite | Modelado relacional de las tablas `Cliente`, `Empresa`, `Producto`, `Compra`. |
| **Multimedia** | **Supabase Storage** | Subida directa de imágenes (logos/productos) desde el frontend (JavaScript) a la nube. |
| **Frontend** | **Jinja2** / HTML5 / CSS (Poppins) | Interfaz moderna, responsive y renderizada por el servidor. |
| **Visualización** | **Chart.js** | Generación de reportes de negocio (dashboard) para mostrar hallazgos financieros. |

---

## 💼 Aspecto Práctico (Lógica de Negocio)

El proyecto simula un flujo de importación mayorista con las siguientes reglas:

### 1. Gestión de Proveedores y Catálogo

* **Proveedor:** Cada **Empresa** registrada es considerada un proveedor de origen chino.
* **Catálogo Dinámico:** La relación **Empresa (1:N) Producto** permite que cada proveedor maneje su propio inventario (`stock`, `precio_usd`, `imagen_url`).
* **Regla de Consistencia:** En la creación de una Compra, el sistema valida que el Producto seleccionado realmente pertenezca a la Empresa indicada.

### 2. Flujo de Compra y Alta Interactividad

* **Formulario Interactivo:** La página de **Nueva Compra** utiliza **JavaScript** para hacer una petición a la API (`GET /productos/{empresa_id}`). Al ingresar el ID del proveedor, el formulario carga y muestra **sólo los productos** que esa empresa tiene disponibles, haciendo el proceso de pedido rápido y preciso.
* **Precios Locales:** Los precios de los productos se muestran en **Pesos Colombianos (COP)** en el catálogo (simulando una tasa de cambio de 1 USD = 4000 COP) para una mejor contextualización del mercado objetivo.

### 3. Data Enriquecida y Hallazgos Financieros

* **Cálculo Automático de Margen:** Al registrar una nueva Compra (`POST /compras/`), el backend ejecuta la siguiente regla de negocio:
    * **Margen Estimado (35%)** se calcula sobre el `precio_total` de importación.
* **Impacto en el Dashboard:** Este dato enriquecido (`margen_estimado`) se persiste en la DB y alimenta el Dashboard, permitiendo la visualización inmediata de la **Venta Potencial Total** y el **Margen Bruto Acumulado**, cumpliendo el requisito de "hallazgos útiles".

---

## 💻 Aspecto Técnico (Arquitectura FastAPI)

### 1. Modelo Relacional y Persistencia

| Modelo | Clave Foránea (FK) | Relación |
| :--- | :--- | :--- |
| **Cliente** | N/A | 1:N con Compra |
| **Empresa** | N/A | 1:N con Producto, 1:N con Compra |
| **Producto** | `empresa_id` | N:1 con Empresa |
| **Compra** | `cliente_id`, `empresa_id`, `producto_id` | N:1 con Cliente, Empresa, Producto |

### 2. Desacoplamiento de Servicios y Escalabilidad

* **Subida de Multimedia:** Se evita la sobrecarga del servidor FastAPI. El JavaScript del frontend realiza la petición **POST** de la imagen binaria **directamente a Supabase Storage**, recibiendo a cambio la URL pública, que luego es guardada por FastAPI en la DB.
* **Ambiente de Despliegue:** El archivo `config.py` permite alternar sin esfuerzo entre la base de datos de desarrollo (`sqlite:///./distribuidora_datos.db`) y la base de datos de producción remota (`postgresql://...`).

### 3. Rutas Clave de la API (Endpoints)

| Método | Endpoint | Funcionalidad |
| :--- | :--- | :--- |
| **GET** | `/` | Vista de inicio y Catálogo (Renderiza `index.html`). |
| **GET** | `/productos/{id}` | **API Interactiva:** Devuelve productos de una empresa específica. |
| **POST** | `/productos/` | Registra Producto (Verifica existencia de Empresa). |
| **POST** | `/empresas/` | Registra Proveedor (Guarda URL de logo de Supabase). |
| **POST** | `/compras/` | **Transacción de Negocio:** Valida FK y calcula Margen. |
| **GET** | `/api/reportes/` | Genera los datos JSON para las gráficas del Dashboard. |

***

## ⚙️ Guía de Instalación y Uso

### A. Pre-requisitos

* Instalar dependencias: `pip install -r requirements.txt`
* Crear carpetas: `mkdir static` && `mkdir static/images`

### B. Ejecución

Asegúrese de estar en la carpeta raíz (`main.py`):

```bash
uvicorn main:app --reload