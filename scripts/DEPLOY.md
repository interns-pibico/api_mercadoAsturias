# Despliegue — Mercado Asturias API

## 1. Subir el proyecto al servidor

```bash
git clone <tu-repo> /home/erpnext/.services/api_mercadoAsturias
```

## 2. Crear carpeta de logs

```bash
mkdir -p /home/erpnext/.services/api_mercadoAsturias/logs
```

## 3. Entorno virtual e instalar dependencias

```bash
cd /home/erpnext/.services/api_mercadoAsturias
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
alembic revision --autogenerate -m "initial"
alembic upgrade head
python scripts/seed.py
```

## 6. Nginx

No hay symlink. Los cambios van directamente en el nginx del proyecto
Three.js. Edita este fichero en el servidor:

```bash
sudo nano /etc/nginx/conf.d/app_example.conf
```

Añade el upstream al principio del fichero, junto al de app_example:
```nginx
upstream mercado_asturias_backend {
    server 127.0.0.1:8001 fail_timeout=0;
}
```

Añade el location dentro del bloque server 443, antes del location /:
```nginx
location /api/ {
    proxy_pass http://mercado_asturias_backend/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /api;
    proxy_connect_timeout 90s;
    proxy_send_timeout 90s;
    proxy_read_timeout 90s;
    proxy_redirect off;
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
| `https://cris.pibico.es/api/` | Info de la API |
| `https://cris.pibico.es/api/v1/docs` | Documentación Swagger |
| `https://cris.pibico.es/api/admin/` | Panel de administración |
| `https://cris.pibico.es/api/v1/municipios` | Endpoint público ejemplo |