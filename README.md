# api_mercadoAsturias

REST API and admin panel for the Asturias local market directory, managing producers, products, and municipalities across Asturias.

## Overview

`api_mercadoAsturias` is a FastAPI application served at `/mercado/` on the pibiCo server. It provides a backend for discovering and managing local markets, producers, and products in Asturias. It includes a web-based admin interface for content management.

## Features

- Product catalogue with categories, producers, and municipalities
- Admin panel with login-protected CRUD interface
- Slug-based URLs for SEO-friendly product and producer pages
- PostgreSQL backend with Alembic migrations
- Session-based authentication (itsdangerous, cookie 8h)
- Static file serving via Nginx

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (psycopg2) |
| Admin UI | Jinja2 templates |
| Auth | itsdangerous (signed session cookie, 8h) |
| Server | Uvicorn, Nginx, Supervisor |

## Project Structure

```
app/
├── admin/         # Admin panel routes and views
├── core/          # Config, database session
├── main.py        # FastAPI application entry point
├── models/        # SQLAlchemy ORM models
├── routers/       # API route definitions
├── schemas/       # Pydantic schemas
└── static/        # Static assets (Leaflet map library)
templates/
└── admin/         # Jinja2 templates (admin panel)
alembic/           # Alembic migrations
scripts/           # DB seed script and deployment reference configs
deploy/
└── nginx/         # Nginx reference configuration
```

## Quick Start (development)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with DATABASE_URL, SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD

alembic upgrade head

# Optional: seed initial data (77 municipalities, 5 categories, 29 products, 16 comercios)
python scripts/seed.py

uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | Key for signing admin session cookies (min 32 chars) |
| `ADMIN_USERNAME` | Admin panel username |
| `ADMIN_PASSWORD` | Admin panel password |
| `API_VERSION` | API version prefix (default: `v1`) |
| `PROJECT_NAME` | API title shown in docs (default: `Mercado Asturias API`) |

## Admin Panel

The admin panel is accessible at `/mercado/admin/login`. It provides a web interface for managing products, producers, and municipality associations.

---

## Despliegue en producción

### Prerequisitos

- Python 3.10+
- PostgreSQL 14+
- Nginx
- Supervisor (`python3-supervisor` o `supervisor` según distro)

### 1. Clonar el repositorio

```bash
git clone <tu-repo> /home/erpnext/.services/api_mercadoAsturias
cd /home/erpnext/.services/api_mercadoAsturias
mkdir -p logs
```

### 2. Crear la base de datos y el usuario PostgreSQL

```bash
sudo -u postgres psql <<EOF
CREATE USER mercado_user WITH PASSWORD 'elige-una-password-segura';
CREATE DATABASE mercado_asturias OWNER mercado_user;
GRANT ALL ON SCHEMA public TO mercado_user;
EOF
```

### 3. Entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar el .env

```bash
cp .env.example .env
nano .env
```

Genera una SECRET_KEY segura:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

El `.env` debe quedar así (cambia los valores marcados):

```
DATABASE_URL=postgresql://mercado_user:<PASSWORD>@localhost:5432/mercado_asturias
SECRET_KEY=<GENERATED_SECRET>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<TU_PASSWORD_ADMIN>
```

### 5. Aplicar migraciones y cargar datos semilla

```bash
source venv/bin/activate
alembic upgrade head
python scripts/seed.py
```

### 6. Nginx

El fichero `deploy/nginx/nginx.conf` contiene el upstream y los locations listos para copiar. Edita el fichero de configuración de tu servidor:

```bash
sudo nano /etc/nginx/conf.d/app_example.conf
```

**Añade el upstream** al principio del fichero, junto al resto de upstreams:

```nginx
upstream api_mercadoAsturias_backend {
    server 127.0.0.1:8001 fail_timeout=0;
}
```

**Añade los locations** dentro del bloque `server 443`, antes del `location /`:

```nginx
# Redirect sin trailing slash
location = /mercado {
    return 301 /mercado/;
}

# Redirect raíz → login del admin
location = /mercado/ {
    return 302 /mercado/admin/login;
}

# Archivos estáticos (servidos directamente por Nginx)
location /mercado/static/ {
    alias /home/erpnext/.services/api_mercadoAsturias/app/static/;
    expires 7d;
    add_header Cache-Control "public, immutable";
}

# Proxy al backend
location /mercado/ {
    proxy_pass http://api_mercadoAsturias_backend/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /mercado;
    proxy_connect_timeout 30s;
    proxy_read_timeout 60s;
}
```

Verifica y recarga Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 7. Supervisor

El fichero `scripts/supervisord.conf` contiene la configuración del proceso. Crea un symlink y arranca el servicio:

```bash
sudo ln -s /home/erpnext/.services/api_mercadoAsturias/scripts/supervisord.conf \
           /etc/supervisor/conf.d/mercado-asturias.conf

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mercado_asturias
sudo supervisorctl status
```

> **Importante:** las variables de entorno (`DATABASE_URL`, `SECRET_KEY`, etc.) deben estar definidas en el entorno del sistema antes de que Supervisor arranque el proceso, o edita directamente la línea `environment=` de `scripts/supervisord.conf` con los valores reales.

### 8. Verificación

```bash
# Estado del proceso
sudo supervisorctl status mercado_asturias

# Test rápido de la API
curl -s http://localhost:8001/v1/municipios | python3 -m json.tool | head -20

# Logs en tiempo real
tail -f logs/mercado_asturias.log
```

### URLs resultantes

| URL | Descripción |
|-----|-------------|
| `https://<tu-dominio>/mercado/` | Redirect al login del admin |
| `https://<tu-dominio>/mercado/admin/login` | Panel de administración |
| `https://<tu-dominio>/mercado/v1/docs` | Documentación Swagger |
| `https://<tu-dominio>/mercado/v1/municipios` | Endpoint público de ejemplo |

---

### Actualizar el código

```bash
cd /home/erpnext/.services/api_mercadoAsturias
git pull
source venv/bin/activate
pip install -r requirements.txt   # por si hay dependencias nuevas
alembic upgrade head               # por si hay migraciones nuevas
sudo supervisorctl restart mercado_asturias
```

---

## License

MIT — see [LICENSE](LICENSE)
