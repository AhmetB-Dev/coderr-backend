# Coderr Backend

**Production-ready REST API for a two-sided service marketplace.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-API-A30000)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Deployment-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

[**Live Demo**](https://ahmet-balci.de/projects/coderr/) · [**Provided Frontend**](https://github.com/Developer-Akademie-Backendkurs/project.Coderr)

Coderr connects customers with business providers. Businesses publish tiered service offers, customers place orders, and completed work can be reviewed.

> The frontend was provided by Developer Akademie. I designed and implemented the backend, including the REST API, data model, validation, permissions, tests, containerization, CI/CD and deployment.

## What makes this project interesting

- **Two distinct user roles** with role-specific actions and protected resources
- **Tiered offers** with Basic, Standard and Premium packages
- **Immutable order snapshots** that preserve purchased offer details after an offer changes
- **Ownership-based permissions** across profiles, offers, orders and reviews
- **Production delivery** using Docker, PostgreSQL, Gunicorn, Nginx and GitHub Actions

## Core features

### Accounts and profiles

- Registration and token-based login
- Customer and business profiles
- Profile editing and image uploads
- Role-aware access rules

### Offers and orders

- Create, edit and delete business offers
- Three pricing tiers per offer
- Search, filtering, ordering and pagination
- Create orders from a selected offer tier
- Persist offer data as an order snapshot
- Track orders as `in_progress`, `completed` or `cancelled`

### Reviews and platform data

- Customers can review business users
- Users can edit or delete only their own reviews
- Public statistics for ratings, profiles and offers

## Tech stack

| Area | Technology |
| --- | --- |
| Backend | Python, Django, Django REST Framework |
| Authentication | DRF Token Authentication |
| Database | SQLite for local development, PostgreSQL with Docker and in production |
| Querying | django-filter |
| Media | Pillow |
| Testing | Django Test Framework, Coverage.py |
| Delivery | Docker, Gunicorn, Nginx, GitHub Actions, GHCR |

## API overview

| Area | Main endpoints |
| --- | --- |
| Authentication | `/api/registration/`, `/api/login/` |
| Profiles | `/api/profile/{id}/`, `/api/profiles/business/`, `/api/profiles/customer/` |
| Offers | `/api/offers/`, `/api/offers/{id}/`, `/api/offerdetails/{id}/` |
| Orders | `/api/orders/`, `/api/orders/{id}/` |
| Reviews | `/api/reviews/`, `/api/reviews/{id}/` |
| Operations | `/api/base-info/`, `/api/health/` |

## Run locally

### Python

```bash
git clone https://github.com/AhmetB-Dev/coderr-backend.git
cd coderr-backend
python -m venv .venv
```

Activate the environment and create the local configuration:

```bash
# Linux / macOS
source .venv/bin/activate
cp .env.example .env
```

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Install and start:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/`.

### Docker

```bash
cp .env.example .env
docker compose up --build
```

## Tests and quality

```bash
python manage.py test
```

The test suite covers authentication, permissions and the main offer, order and review workflows. CI also validates code quality and dependencies before deployment.

## Security and deployment

- Server-side serializer validation
- Role- and ownership-based authorization
- Environment-based secrets
- Production-specific CORS, CSRF and Django settings
- PostgreSQL in the containerized production environment
- Immutable production images published through GHCR

Detailed production instructions are available in [`DEPLOYMENT.md`](./DEPLOYMENT.md).

---

Built as part of my Fullstack Developer portfolio.
