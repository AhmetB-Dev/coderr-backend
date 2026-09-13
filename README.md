# Coderr Backend

Django REST Framework backend for a service marketplace with authentication, customer and business profiles, offers, orders, reviews and role-based permissions.

[Live Demo](https://ahmet-balci.de/projects/coderr/) · [Provided Frontend](https://github.com/Developer-Akademie-Backendkurs/project.Coderr)

> The frontend was provided by Developer Akademie as part of the backend course. My work focuses on the backend implementation, REST API, permissions, data model, tests and deployment.

## Highlights

- Django REST Framework API
- Token-based authentication
- Customer and business user roles
- Role-based and ownership-based permissions
- Offer management with Basic, Standard and Premium packages
- Search, filtering, ordering and pagination
- Order workflow with persisted offer snapshots
- Review system with validation and permissions
- PostgreSQL for Docker and production
- Automated API tests and coverage support
- Docker-based runtime
- GitHub Actions CI/CD with reusable workflows
- Production deployment with Gunicorn and Nginx

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend | Python, Django, Django REST Framework |
| Authentication | DRF Token Authentication |
| Database | SQLite locally, PostgreSQL with Docker/production |
| Filtering | django-filter |
| Media | Pillow |
| Deployment | Docker, Gunicorn, Nginx |
| CI/CD | GitHub Actions, GHCR |
| Testing | Django Test Framework, Coverage.py |

## Quick Start

### Local Python

```bash
git clone https://github.com/AhmetB-Dev/coderr-backend.git
cd coderr-backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
```

Linux/macOS:

```bash
source .venv/bin/activate
cp .env.example .env
```

Then:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Local API:

```text
http://127.0.0.1:8000/api/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

### Docker

After configuring `.env`:

```bash
docker compose up --build
```

The Docker development setup runs Django with PostgreSQL.

### Run Tests

```bash
python manage.py test
```

## Core Features

### Authentication & Profiles

- User registration and login
- Token-based authentication
- Customer and business profiles
- Profile editing
- Profile image uploads

### Offers

Business users can create and manage offers with three pricing tiers:

- Basic
- Standard
- Premium

The offer list supports:

- search
- filtering
- ordering
- pagination

### Orders

Customers can create orders from offer details.

Orders store a snapshot of the selected offer data so later changes to an offer do not modify existing orders.

Supported states:

- `in_progress`
- `completed`
- `cancelled`

Business users can manage the status of their own orders.

### Reviews

Customers can review business users.

The API supports filtering and ordering, while permissions restrict users to allowed review actions.

### Platform Statistics

The public platform-info endpoint returns aggregated values such as:

- number of reviews
- average rating
- number of business profiles
- number of offers

## Roles & Permissions

### Customer

Customers can:

- browse profiles and offers
- create orders
- access their related orders
- create reviews
- edit or delete their own reviews

### Business

Business users can:

- create and manage their own offers
- manage offer details
- access their related orders
- update the status of their own business orders

### Staff

Django staff users have additional administrative permissions, including access to Django Admin.

## API Overview

All application endpoints are available below `/api/`.

### Authentication & Profiles

```text
POST  /api/registration/
POST  /api/login/

GET   /api/profile/{id}/
PATCH /api/profile/{id}/

GET   /api/profiles/business/
GET   /api/profiles/customer/
```

### Offers

```text
GET    /api/offers/
POST   /api/offers/
GET    /api/offers/{id}/
PATCH  /api/offers/{id}/
DELETE /api/offers/{id}/

GET    /api/offerdetails/{id}/
```

### Orders

```text
GET    /api/orders/
POST   /api/orders/
PATCH  /api/orders/{id}/
DELETE /api/orders/{id}/

GET /api/order-count/{business_user_id}/
GET /api/completed-order-count/{business_user_id}/
```

### Reviews

```text
GET    /api/reviews/
POST   /api/reviews/
PATCH  /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

### Platform Information

```text
GET /api/base-info/
GET /api/health/
```

## Tests

Run all tests:

```bash
python manage.py test
```

Run individual app suites:

```bash
python manage.py test auth_app
python manage.py test offers_app
python manage.py test orders_app
python manage.py test reviews_app
python manage.py test core
```

Coverage:

```bash
coverage erase
coverage run manage.py test
coverage report -m
```

The tests cover authentication, permissions and the main offer, order and review workflows.

## CI/CD

Pull requests run the shared Django CI workflow.

Pushes to `main` additionally:

- build and publish an immutable container image
- pass through the protected production environment
- deploy the selected image to the VPS

The workflow uses the reusable CI/CD workflows from `AhmetB-Dev/django-devops-template`.

Production details are documented in [`DEPLOYMENT.md`](./DEPLOYMENT.md).

## Security

The backend uses:

- token-based authentication
- role-specific permissions
- ownership checks for protected resources
- serializer validation
- environment-based secrets
- CORS and CSRF configuration
- production-specific Django settings
- PostgreSQL in the containerized production environment

---

Built as part of my Fullstack Developer portfolio.
