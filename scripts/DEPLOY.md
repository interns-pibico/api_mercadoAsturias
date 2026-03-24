# Despliegue — Mercado Asturias API

## 0. Prerequisitos del sistema

Asegúrate de tener instalados:
- Python 3.10+
- PostgreSQL 14+
- Nginx
- Supervisor

```bash
# Debian/Ubuntu
sudo apt install python3 python3-venv python3-pip postgresql nginx supervisor
```

## 1. Subir el proyecto al servidor

```bash
git clone <tu-repo> /home/erpnext/.services/api_mercadoAsturias
cd /home/erpnext/.services/api_mercadoAsturias
mkdir -p logs
```

## 2. Crear la base de datos y usuario PostgreSQL

```bash
sudo -u postgres psql <<EOF
CREATE USER mercado_user WITH PASSWORD 'elige-una-password-segura';
CREATE DATABASE mercado_asturias OWNER mercado_user;
GRANT ALL ON SCHEMA public TO mercado_user;
EOF
```

## 3. Entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Configurar el .env

```bash
cp .env.example .env
nano .env
```

Genera una SECRET_KEY segura:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

## 5. Migraciones y seed

```bash
source venv/bin/activate
alembic upgrade head
python scripts/seed.py
```

## 6. Nginx

El fichero `deploy/nginx/nginx.conf` contiene el upstream y los locations ya preparados. Edita la configuración de tu servidor:

```bash
sudo nano /etc/nginx/conf.d/app_example.conf
```

Añade el **upstream** al principio del fichero, junto al resto de upstreams:
```nginx
upstream api_mercadoAsturias_backend {
    server 127.0.0.1:8001 fail_timeout=0;
}
```

Añade los **locations** dentro del bloque `server 443`, antes del `location /`:
```nginx
location = /mercado {
    return 301 /mercado/;
}

location = /mercado/ {
    return 302 /mercado/admin/login;
}

location /mercado/static/ {
    alias /home/erpnext/.services/api_mercadoAsturias/app/static/;
    expires 7d;
    add_header Cache-Control "public, immutable";
}

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

Verificar y recargar:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 7. Supervisord

```bash
# Crear symlink
sudo ln -s /home/erpnext/.services/api_mercadoAsturias/scripts/supervisord.conf \
           /etc/supervisor/conf.d/mercado-asturias.conf

# Arrancar
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start mercado_asturias
sudo supervisorctl status
```

> **Nota:** las variables de entorno deben estar disponibles en el entorno del sistema, o edita la línea `environment=` de `supervisord.conf` con los valores reales antes de arrancar.

---

## Comandos del día a día

```bash
# Ver estado
sudo supervisorctl status mercado_asturias

# Reiniciar tras cambios en el código
sudo supervisorctl restart mercado_asturias

# Logs en tiempo real
tail -f /home/erpnext/.services/api_mercadoAsturias/logs/mercado_asturias.log

# Logs de nginx
sudo tail -f /var/log/nginx/app_example_access.log
sudo tail -f /var/log/nginx/app_example_error.log
```

---

## Actualizar el código

```bash
cd /home/erpnext/.services/api_mercadoAsturias
git pull
source venv/bin/activate
pip install -r requirements.txt   # por si hay dependencias nuevas
alembic upgrade head               # por si hay migraciones nuevas
sudo supervisorctl restart mercado_asturias
```

---

## URLs una vez desplegado

| URL | Descripción |
|-----|-------------|
| `https://<tu-dominio>/mercado/` | Redirect al login del admin |
| `https://<tu-dominio>/mercado/admin/login` | Panel de administración |
| `https://<tu-dominio>/mercado/v1/docs` | Documentación Swagger |
| `https://<tu-dominio>/mercado/v1/municipios` | Endpoint público de ejemplo |
