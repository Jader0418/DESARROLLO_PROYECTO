# 🚀 Distribuidora JS | Plataforma de Gestión de Importaciones B2B

## ✨ Visión General del Proyecto

El sistema **Distribuidora JS** es una solución de gestión **Business-to-Business (B2B)** enfocada en el sector tecnológico. La plataforma actúa como un puente digital entre **clientes mayoristas en Colombia** y **proveedores fabricantes en China**, automatizando el ciclo de vida de las órdenes de importación.

El desarrollo cumple con todos los requisitos académicos, incluyendo **CRUD completo**, **Data Enriquecida**, y **despliegue en servidor web** accesible.

### 💡 Propuesta de Valor

Facilitar el aprovisionamiento de tecnología mediante la transparencia de costos y la consolidación de proveedores.

***

## 🛠️ Stack Tecnológico Detallado

| Componente | Tecnología | Versión | Propósito Principal |
| :--- | :--- | :--- | :--- |
| **Backend Core** | **Python** | 3.11+ | Lógica del servidor y ejecución de la API. |
| **Framework API** | **FastAPI** | Última | Creación de endpoints HTTP de alto rendimiento. |
| **Persistencia** | **SQLModel** | Última | Modelado ORM y gestión de la base de datos (PostgreSQL/SQLite). |
| **Frontend/Vistas** | **Jinja2** / HTML / CSS (Poppins) | N/A | Renderizado de formularios, listados y diseño "confort". |
| **Multimedia** | **Supabase Storage** | N/A | Almacenamiento directo de logos y fotos de productos. |
| **Visualización** | **Chart.js** | N/A | Presentación de reportes y estadísticas en el Dashboard. |
| **Despliegue (URL)** | **Render** | N/A | Alojamiento para acceso público (URL disponible). |

***

## ⚙️ Arquitectura de Datos y Lógica de Negocio

### 1. Diagrama de Clases UML (Modelos y Relaciones)

El sistema se basa en cuatro modelos interconectados para gestionar la relación Proveedor-Producto-Cliente-Pedido.

```plantuml
@startuml
skinparam ClassAttributeIconStyle relevant

class Cliente {
    + id : int <<PK>>
    + nombre : str
    + email : str <<Unique>>
    + direccion_envio : str
}

class Empresa {
    + id : int <<PK>>
    + nombre_empresa : str <<Unique>>
    + tipo_producto : str
    + imagen_url : str <<Multimedia>>
}

class Producto {
    + id : int <<PK>>
    + empresa_id : int <<FK>>
    + nombre : str
    + precio_usd : float
    + stock : int
    + imagen_url : str <<Multimedia>>
}

class Compra {
    + id : int <<PK>>
    + cliente_id : int <<FK>>
    + empresa_id : int <<FK>>
    + producto_id : int <<FK>>
    + cantidad : int
    + estado_pedido : str
    -- Data Enriquecida --
    + precio_total : float
    + margen_estimado : float
}

Cliente "1" -- "N" Compra : realiza
Empresa "1" -- "N" Producto : ofrece
Empresa "1" -- "N" Compra : es_proveedor_de
Producto "1" -- "N" Compra : se_compra
@enduml