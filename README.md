# api_mercadoAsturias

REST API and admin panel for the Asturias local market directory, managing producers, products, and municipalities across Asturias.

## Overview

`api_mercadoAsturias` is a FastAPI application served at `/mercado/` on the pibiCo server. It provides a backend for discovering and managing local markets, producers, and products in Asturias. It includes a web-based admin interface for content management.

## Features

- Product catalogue with categories, producers, and municipalities
- Admin panel with login-protected CRUD interface
- Slug-based URLs for SEO-friendly product and producer pages
- PostgreSQL backend with Alembic migrations
- JWT authentication
- Static file serving via Nginx

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI, SQLAlchemy, Alembic |
| Database | PostgreSQL (psycopg2) |
| Admin UI | Jinja2 + Starlette admin |
| Auth | JWT (python-jose, passlib/bcrypt) |
| Server | Uvicorn, Nginx |

## Project Structure

```
app/
├── admin/         # Admin panel routes and views
├── core/          # Config, security
├── main.py        # FastAPI application entry point
├── models/        # SQLModel ORM models
├── routers/       # API route definitions
├── schemas/       # Pydantic schemas
├── services/      # Business logic
├── static/        # Admin static assets
└── templates/     # Jinja2 templates (admin)
scripts/           # DB seed scripts and Supervisor/Nginx reference configs
migrations/        # Alembic migrations
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Edit .env with DATABASE_URL, SECRET_KEY, ADMIN_USERNAME, ADMIN_PASSWORD

alembic upgrade head

# Optional: seed initial data
python scripts/seed.py

uvicorn app.main:app --reload
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret |
| `ADMIN_USERNAME` | Admin panel username |
| `ADMIN_PASSWORD` | Admin panel password |
| `APP_ENV` | Environment (`development` / `production`) |

## Admin Panel

The admin panel is accessible at `/mercado/admin/login`. It provides a web interface for managing products, producers, and municipality associations.

## License

MIT — see [LICENSE](LICENSE)
