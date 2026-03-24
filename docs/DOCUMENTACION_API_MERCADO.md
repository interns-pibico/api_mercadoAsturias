# Documentación Técnica — api_mercadoAsturias

> **Versión:** 1.0 · **Fecha:** 2026-03-23
> **Formato:** Optimizado para presentación / exportable a Notion o Word

---

## Tabla de Contenidos

1. [Información General y Contexto](#1-información-general-y-contexto)
2. [Arquitectura y Flujo del Sistema](#2-arquitectura-y-flujo-del-sistema)
3. [Modelo de Datos](#3-modelo-de-datos)
4. [Documentación de la API Pública](#4-documentación-de-la-api-pública)
5. [Panel de Administración](#5-panel-de-administración)
6. [Stack Técnico](#6-stack-técnico)
7. [Configuración y Despliegue](#7-configuración-y-despliegue)

---

## 1. Información General y Contexto

### 1.1 Elevator Pitch

**api_mercadoAsturias** es una API REST que gestiona el directorio de comercios y productos del mercado tradicional asturiano. Permite a otras aplicaciones (como `app_asturiasMobile`) consultar qué comercios existen en cada municipio, qué productos ofrecen y en qué categoría se encuadran.

Incluye un **panel de administración web** protegido con autenticación, desde el cual el equipo de pibiCo puede gestionar el catálogo completo: municipios, categorías, productos y comercios con su estado de suscripción.

### 1.2 Objetivo y Alcance

| Dimensión | Descripción |
|---|---|
| **Objetivo principal** | Servir datos de comercios y productos del mercado asturiano a otras apps |
| **Consumidores** | `app_asturiasMobile` (proxy `/api/mercado/{id}`), cualquier cliente HTTP |
| **Alcance geográfico** | Municipios de Asturias con comercios registrados |
| **Autenticación pública** | Sin autenticación — API pública de solo lectura |
| **Autenticación admin** | Cookie firmada con `itsdangerous` (sesión 8 horas) |

### 1.3 Integración con el Ecosistema

`api_mercadoAsturias` actúa como microservicio independiente dentro del ecosistema pibiCo:

```
app_asturiasMobile
  └── GET /api/mercado/{municipio_id}
        └── proxy → api_mercadoAsturias:8001
              └── GET /v1/municipios/{slug}/comercios
```

---

## 2. Arquitectura y Flujo del Sistema

### 2.1 Estructura de Directorios

```
api_mercadoAsturias/
├── app/
│   ├── main.py              ← FastAPI app factory, CORS, rutas
│   ├── core/
│   │   ├── config.py        ← Settings (pydantic-settings)
│   │   └── database.py      ← SQLAlchemy session + Base
│   ├── models/
│   │   └── models.py        ← ORM: Municipio, Categoria, Producto, Comercio
│   ├── schemas/
│   │   └── schemas.py       ← Pydantic: schemas de entrada y salida
│   ├── routers/
│   │   └── public.py        ← Endpoints públicos GET /v1/...
│   ├── admin/
│   │   └── admin.py         ← Panel admin (login, CRUD completo)
│   └── static/              ← Leaflet (JS + CSS + imágenes)
├── templates/
│   └── admin/               ← Jinja2 templates del panel admin
├── alembic/                 ← Migraciones de base de datos
├── scripts/
│   ├── seed.py              ← Datos semilla iniciales
│   └── DEPLOY.md            ← Guía de despliegue
└── deploy/
    └── nginx/nginx.conf     ← Configuración Nginx
```

### 2.2 Patrón de capas

```
HTTP Request
    ↓
FastAPI Router (public.py / admin.py)
    ↓
SQLAlchemy ORM (models.py)
    ↓
PostgreSQL — BD mercado_asturias
```

---

## 3. Modelo de Datos

### 3.1 Diagrama de entidades

```
Municipio (1) ──────────── (N) Comercio
                                  │
                                  N
                               [comercio_productos]
                                  M
                                  │
Categoria (1) ──────────── (N) Producto
```

### 3.2 Tablas

#### `municipios`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `nombre` | String(100) | Nombre del municipio |
| `slug` | String(100) unique | Identificador URL-friendly |
| `lat` | Float | Latitud geográfica |
| `lon` | Float | Longitud geográfica |
| `provincia` | String(100) | Provincia (default: "Asturias") |

#### `categorias`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `nombre` | String(100) | Nombre de la categoría |
| `slug` | String(100) unique | Identificador URL-friendly |
| `descripcion` | Text | Descripción de la categoría |
| `icono` | String(10) | Emoji o nombre de icono |

#### `productos`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `nombre` | String(150) | Nombre del producto |
| `slug` | String(150) unique | Identificador URL-friendly |
| `descripcion` | Text | Descripción del producto |
| `imagen_url` | String(300) | URL de imagen |
| `categoria_id` | FK → categorias | Categoría a la que pertenece |

#### `comercios`
| Campo | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `nombre` | String(150) | Nombre del comercio |
| `slug` | String(150) unique | Identificador URL-friendly |
| `descripcion` | Text | Descripción del comercio |
| `direccion` | String(250) | Dirección física |
| `lat` / `lon` | Float | Coordenadas geográficas |
| `telefono` | String(20) | Teléfono de contacto |
| `web` | String(250) | URL web |
| `horario` | Text | Horario de apertura |
| `municipio_id` | FK → municipios | Municipio donde está ubicado |
| `activo` | Boolean | `true` si la suscripción está activa |
| `api_key` | String(64) unique | Clave API generada automáticamente |
| `suscripcion_hasta` | DateTime | Fecha de fin de suscripción |

#### `comercio_productos` (tabla intermedia M:N)
| Campo | Tipo |
|---|---|
| `comercio_id` | FK → comercios |
| `producto_id` | FK → productos |

---

## 4. Documentación de la API Pública

**Base URL:** `https://cris.pibico.es/mercado/v1`
**Docs interactivos:** `https://cris.pibico.es/mercado/v1/docs`
**Autenticación:** Ninguna (solo lectura pública)

### 4.1 Municipios

#### `GET /municipios`
Lista todos los municipios ordenados por nombre.

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Gijón",
    "slug": "gijon",
    "lat": 43.5453,
    "lon": -5.6615,
    "provincia": "Asturias"
  }
]
```

#### `GET /municipios/{slug}`
Detalle de un municipio por su slug.

| Parámetro | Tipo | Descripción |
|---|---|---|
| `slug` | string | Identificador URL del municipio |

**Error:** `404` si el municipio no existe.

---

### 4.2 Categorías

#### `GET /categorias`
Lista todas las categorías de productos ordenadas por nombre.

**Respuesta:**
```json
[
  {
    "id": 1,
    "nombre": "Quesos",
    "slug": "quesos",
    "descripcion": "Quesos artesanos asturianos",
    "icono": "🧀"
  }
]
```

#### `GET /categorias/{slug}/productos`
Lista los productos de una categoría concreta.

**Error:** `404` si la categoría no existe.

---

### 4.3 Comercios

#### `GET /municipios/{municipio_slug}/comercios`
Lista los comercios activos en un municipio.

**Respuesta:** Array de `ComercioResumen` (sin lista de productos).

#### `GET /municipios/{municipio_slug}/categorias/{categoria_slug}/comercios`
Comercios activos en un municipio que venden productos de una categoría concreta.

**Ejemplo:** `/v1/municipios/gijon/categorias/quesos/comercios`

#### `GET /productos/{producto_slug}/comercios`
Todos los comercios activos que venden un producto concreto.

#### `GET /comercios/{slug}`
Detalle completo de un comercio: datos, municipio y lista de productos.

**Respuesta:**
```json
{
  "id": 3,
  "nombre": "Quesería El Cabrales",
  "slug": "queseria-el-cabrales",
  "descripcion": "Especialistas en queso Cabrales DOP",
  "direccion": "Calle Mayor 12, Carreña",
  "lat": 43.2912,
  "lon": -4.8921,
  "telefono": "985 123 456",
  "web": "https://ejemplo.com",
  "horario": "Lunes a Viernes 9:00-14:00",
  "activo": true,
  "municipio": { "id": 9, "nombre": "Cabrales", "slug": "cabrales" },
  "productos": [
    { "id": 1, "nombre": "Queso Cabrales DOP", "slug": "queso-cabrales-dop" }
  ],
  "suscripcion_hasta": "2027-01-01T00:00:00"
}
```

---

## 5. Panel de Administración

**URL:** `https://cris.pibico.es/mercado/admin/`
**Autenticación:** Usuario y contraseña configurados en `.env`
**Sesión:** Cookie firmada con `itsdangerous`, válida 8 horas

### 5.1 Funcionalidades

| Módulo | Operaciones |
|---|---|
| **Comercios** | Listar, crear, editar, activar/desactivar toggle |
| **Categorías** | Listar, crear |
| **Productos** | Listar, crear |
| **Municipios** | Listar (solo lectura en admin) |
| **Dashboard** | Estadísticas: total municipios, categorías, productos, comercios activos/inactivos |

### 5.2 Gestión de suscripciones

Cada comercio tiene un campo `activo` y `suscripcion_hasta`. El admin puede:
- Activar/desactivar un comercio con un solo click (toggle)
- Establecer la fecha de fin de suscripción
- Ver la `api_key` generada automáticamente al crear el comercio

---

## 6. Stack Técnico

| Capa | Tecnología |
|---|---|
| **Framework** | FastAPI (Python 3.x) |
| **ORM** | SQLAlchemy (síncrono) |
| **Driver BD** | psycopg2 (síncrono) |
| **Validación** | Pydantic v2 |
| **Config** | pydantic-settings |
| **Templates** | Jinja2 (panel admin) |
| **Auth admin** | itsdangerous (cookie firmada) |
| **Migraciones** | Alembic |
| **Mapa admin** | Leaflet 1.x (local, sin CDN) |
| **Base de datos** | PostgreSQL — BD `mercado_asturias` |
| **Proceso** | Uvicorn (2 workers, `--workers 2`) |
| **Proxy** | Nginx (`/mercado/`) |

---

## 7. Configuración y Despliegue

### 7.1 Variables de entorno (`.env`)

| Variable | Descripción |
|---|---|
| `DATABASE_URL` | URL de conexión PostgreSQL (`postgresql://user:pass@host/mercado_asturias`) |
| `SECRET_KEY` | Clave para firmar cookies de sesión del admin |
| `ADMIN_USERNAME` | Usuario del panel admin (default: `admin`) |
| `ADMIN_PASSWORD` | Contraseña del panel admin |

### 7.2 Instalación

```bash
git clone <repo>
cd api_mercadoAsturias
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Editar con credenciales reales

# Crear BD y aplicar migraciones
createdb mercado_asturias
alembic upgrade head

# Cargar datos semilla
python scripts/seed.py

# Arrancar
uvicorn app.main:app --port 8001
```

### 7.3 Nginx

La app se sirve bajo el path `/mercado/` configurado en `deploy/nginx/nginx.conf`. El `root_path="/mercado"` está definido en `app/main.py` para que los docs y redirects funcionen correctamente detrás del proxy.

### 7.4 Datos actuales en producción

| Tabla | Registros |
|---|---|
| municipios | 77 |
| categorias | 5 |
| productos | 29 |
| comercios | 16 (activos) |
