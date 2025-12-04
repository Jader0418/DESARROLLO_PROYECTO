# 🚀 Distribuidora JS | Sistema de Gestión de Importaciones B2B

## 🎯 Descripción del Proyecto

El sistema **Distribuidora JS** es una plataforma web desarrollada para facilitar el comercio B2B (Business-to-Business) en el sector tecnológico. Actúa como un *agregador* que conecta compradores mayoristas en Colombia con proveedores fabricantes en China.

El proyecto cumple con los requisitos de un sistema CRUD completo, gestión de reglas de negocio, manejo de multimedias (subida a la nube) y presentación de informes/estadísticas.

### Funcionalidades y Reglas de Negocio Implementadas

| Funcionalidad | Cumplimiento | Detalle |
| :--- | :--- | :--- |
| **Persistencia de Datos** | ✅ Servidor de Base de Datos | **PostgreSQL (Render)** o **SQLite (Local)** configurado vía `config.py`. |
| **CRUD & Relaciones** | ✅ Modelos con Relación | **Cliente (1:N) Compra**, **Empresa (1:N) Producto**, y **Producto (N:1) Compra**. |
| **Data Enriquecida** | ✅ Cálculo Automático | Se calcula un **Margen de Ganancia Estimado del 35%** en cada orden de Compra. |
| **Multimedia** | ✅ Subida a Servidor Externo | Subida de logos de Empresas y fotos de Productos directamente a **Supabase Storage**. |
| **Interacción** | ✅ Formularios HTML Interactivos | El formulario de Compra es dinámico: los productos cambian según el proveedor seleccionado. |
| **Reportes** | ✅ Dashboard con Estadísticas | Muestra el **Costo Total de Importación** y el **Margen Bruto Estimado** con gráficos (Chart.js). |
| **Usabilidad** | ✅ Estilos y Búsqueda | Diseño "confort" con tipografía Poppins y funcionalidad de **Búsqueda Inmersa** en el listado de Proveedores. |

***

## 🛠️ Stack Tecnológico

| Componente | Tecnología | Propósito |
| :--- | :--- | :--- |
| **Backend / API** | Python 3.11, **FastAPI** | Servicio web de alto rendimiento y lógica de negocio. |
| **Base de Datos** | **SQLModel** (ORM) / **SQLite** (Dev) | ORM que facilita la conexión y el manejo de tablas. |
| **Multimedia** | **Supabase Storage** | Almacenamiento de archivos en la nube y generación de URLs públicas. |
| **Despliegue** | **Render** | Alojamiento para acceso público a la URL. |
| **Frontend** | HTML5, Jinja2, **JavaScript (Fetch API)** | Manejo de vistas y peticiones asíncronas para el CRUD. |

***

## 📊 Documentación de Modelos y Procesos

### 1. Diagrama de Clases UML (Estructura de la DB)

Muestra la estructura de las tablas (`table=True`) y las relaciones 1:N que utiliza el sistema.

```plantuml
@startuml
skinparam ClassAttributeIconStyle relevant

class Cliente {
    + id : int <<PK>>
    -- Datos Personales --
    + nombre : str
    + email : str <<Unique>>
    + pais : str
    + direccion_envio : str
    -- Relación --
    + compras : List<Compra>
}

class Empresa {
    + id : int <<PK>>
    -- Datos de Proveedor --
    + nombre_empresa : str <<Unique>>
    + contacto_email : str
    + tipo_producto : str
    + imagen_url : str <<Multimedia>>
    -- Relación --
    + productos : List<Producto>
    + compras : List<Compra>
}

class Producto {
    + id : int <<PK>>
    + empresa_id : int <<FK>>
    -- Detalle --
    + nombre : str
    + precio_usd : float
    + stock : int
    + imagen_url : str <<Multimedia>>
    -- Relación --
    + compras : List<Compra>
}

class Compra {
    + id : int <<PK>>
    + cliente_id : int <<FK>>
    + empresa_id : int <<FK>>
    + producto_id : int <<FK>>
    -- Datos de Pedido --
    + cantidad : int
    + precio_total : float
    + estado_pedido : str
    -- Data Enriquecida --
    + margen_estimado : float
    + created_at : datetime
}

Cliente "1" -- "N" Compra : realiza
Empresa "1" -- "N" Producto : ofrece
Empresa "1" -- "N" Compra : es_proveedor_de
Producto "1" -- "N" Compra : contiene
@enduml 