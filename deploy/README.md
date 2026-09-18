# Guía de Despliegue en Producción (VPS)

Esta carpeta contiene los archivos de configuración para poner la aplicación en producción en cualquier VPS (Hetzner, OVH, DigitalOcean, AWS, etc.).

---

## Opción A: Despliegue con Docker Compose (Recomendado)

En tu servidor VPS con Docker instalado:

```bash
# 1. Clonar repositorio
git clone https://github.com/marcosAlvarezCalabria/times-fm.git
cd times-fm

# 2. Levantar contenedor en segundo plano
docker compose up -d --build

# 3. Comprobar logs y estado
docker compose logs -f
```

La aplicación estará activa en el puerto `8000`.

---

## Opción B: Despliegue Nativo con Systemd + Nginx + SSL

1. **Copiar el servicio systemd**:
   ```bash
   sudo cp deploy/timesfm.service /etc/systemd/system/timesfm.service
   sudo systemctl daemon-reload
   sudo systemctl enable --now timesfm
   ```

2. **Configurar Nginx**:
   ```bash
   sudo cp deploy/nginx.conf /etc/nginx/sites-available/timesfm
   sudo ln -s /etc/nginx/sites-available/timesfm /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **Activar HTTPS gratuito con Certbot**:
   ```bash
   sudo certbot --nginx -d tu-dominio.com
   ```
