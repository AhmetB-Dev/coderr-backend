# Coderr Production Deployment

Coderr uses the shared `AhmetB-Dev/django-devops-template@v1` CI/CD standard.
The production target is a Docker Compose stack on the VPS behind the existing
host-level Nginx reverse proxy.

## Architecture

```text
GitHub push/merge to main
        |
        v
Reusable CI @v1
        |
        v
GHCR immutable image (sha-<commit>)
        |
        v
GitHub production environment gate
        |
        v
SSH to VPS
        |
        v
scripts/deploy.sh
        |
        v
Docker Compose: web + PostgreSQL
        |
        v
127.0.0.1:8001
        |
        v
Host Nginx / HTTPS
```

## GitHub repository configuration

Create these **Repository secrets** under `Settings -> Secrets and variables -> Actions`:

- `VPS_HOST` - only the server IP address or hostname. Do **not** enter `ssh ahmet@...`.
- `VPS_SSH_PRIVATE_KEY` - Coderr-specific private deploy key.
- `VPS_KNOWN_HOSTS` - trusted `known_hosts` entry for the VPS.

Create these **Repository variables**:

- `VPS_USER=ahmet`
- `VPS_APP_DIR=/home/ahmet/apps/coderr-backend`

Create a GitHub Environment named `production` and restrict deployment to `main`.
The VPS credentials stay at repository level; the Environment is the deployment gate.

## First VPS setup

Create the application directory and clone the repository once:

```bash
mkdir -p /home/ahmet/apps
cd /home/ahmet/apps
git clone https://github.com/AhmetB-Dev/Coderr-backend.git coderr-backend
cd coderr-backend
mkdir -p media
```

Create the production environment file from the example:

```bash
cp .env.production.example .env
nano .env
chmod 600 .env
```

At minimum replace:

- `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- `DJANGO_CORS_ALLOWED_ORIGINS`
- `DB_PASSWORD`
- the placeholder domain values

`APP_PORT=8001` keeps Coderr separate from Videoflix on the same VPS.

## Nginx

Copy `deploy/nginx/coderr-api.conf.example` to the host Nginx configuration and
replace `api.coderr.example.com` with the real API domain. The configuration proxies
Django to `127.0.0.1:8001` and serves uploaded media directly from
`/home/ahmet/apps/coderr-backend/media/`.

After editing Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

TLS/HTTPS should be configured on the host in the same way as the other projects.

## First manual Compose validation

Before enabling the first automated production deployment, the server can validate
the Compose configuration with:

```bash
docker compose -f compose.prod.yaml config
```

The actual application image is supplied by CI/CD as `APP_IMAGE`. Normal releases
should therefore happen through GitHub Actions rather than manual image tags.

## Deployment behavior

On a push to `main` after CI succeeds:

1. GitHub builds and publishes an immutable GHCR image.
2. The `production` Environment gate is checked.
3. The reusable deployment workflow logs in to the VPS.
4. The server pulls the repository with `git pull --ff-only`.
5. `scripts/deploy.sh` pulls the exact image and runs Docker Compose.
6. Docker waits for PostgreSQL and web health checks.
7. If the new application image fails health checks, the deploy script attempts an
   application-image rollback.

Django migrations and `collectstatic` run when the web container starts.

## Useful production commands

```bash
cd /home/ahmet/apps/coderr-backend

docker compose -f compose.prod.yaml ps
docker compose -f compose.prod.yaml logs --tail=150 web
docker compose -f compose.prod.yaml logs --tail=150 db
docker compose -f compose.prod.yaml exec web python manage.py check
docker compose -f compose.prod.yaml exec web python manage.py createsuperuser
```

Health endpoint after deployment:

```text
https://<api-domain>/api/health/
```

## Production data

PostgreSQL data is stored in the Compose volume `postgres_data`. Uploaded profile and
offer images are stored in the project-local `media/` directory so host Nginx can
serve them and so deployments do not delete uploads.

Backups, restore testing, SSH hardening, monitoring, and further DevSecOps hardening
are intentionally handled as a later shared infrastructure step after the projects
are online.
