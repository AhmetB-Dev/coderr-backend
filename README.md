# Coderr Backend

Coderr Backend is a REST API built with Django and Django REST Framework.

This repository contains my backend implementation for the Coderr project. The frontend was provided by the **Developer Akademie** as part of the Backend course and was not developed by me.

Frontend repository:

[Developer Akademie – project.Coderr](https://github.com/Developer-Akademie-Backendkurs/project.Coderr)

It provides the backend functionality for the Coderr platform, including authentication, customer and business profiles, offers, orders, reviews, platform statistics, media uploads, and role-based permissions.

The project uses token-based authentication and communicates with the provided Coderr frontend through a REST API.

---

## Quick Start

### 1. Get the repository

Clone this backend repository using GitHub's **Code** button, then open the project directory:

```bash
cd backend
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Activate it on Linux or macOS:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root directory.

You can use `.env.example` as a template:

```env
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
```

Generate a secure Django secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Never commit the real `.env` file to version control.

### 5. Apply database migrations

```bash
python manage.py migrate
```

### 6. Create an administrator

This step is optional, but required if you want to use the Django admin interface.

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The API is available at:

```text
http://127.0.0.1:8000/api/
```

The Django admin interface is available at:

```text
http://127.0.0.1:8000/admin/
```

---

## Frontend

The Coderr frontend was provided by the **Developer Akademie** as part of the Backend course.

It is maintained separately from this backend repository and communicates with the backend through the REST API.

Frontend repository:

[Developer Akademie – project.Coderr](https://github.com/Developer-Akademie-Backendkurs/project.Coderr)

This repository focuses on the backend implementation and its integration with the provided frontend.

---

## Features

* User registration and login
* Token-based authentication
* Customer and business user profiles
* Profile editing and profile image uploads
* Business offer creation and management
* Basic, standard, and premium offer packages
* Offer search, filtering, ordering, and pagination
* Customer order creation
* Order status management
* Business order statistics
* Customer reviews
* Review filtering and ordering
* Platform-wide statistics
* Role-based permissions
* Staff-only administrative actions
* Django admin interface
* Media file handling
* CORS support for frontend integration
* Automated API tests

---

## Tech Stack

* Python
* Django 6.1
* Django REST Framework 3.18
* DRF Token Authentication
* SQLite
* Pillow
* django-cors-headers
* django-filter
* python-dotenv
* Coverage.py

---

## User Roles and Permissions

Coderr uses two application-specific profile types in addition to Django staff permissions.

### Customer

Customers can:

* view profiles
* view offers and offer details
* create orders from offer details
* view orders related to their account
* create reviews for business users
* edit or delete their own reviews

### Business

Business users can:

* view profiles
* create offers
* edit and delete their own offers
* manage the details of their own offers
* view orders related to their account
* update the status of their own business orders

### Staff

Django staff users have additional administrative permissions.

Staff users can:

* access the Django admin interface
* delete orders through the API

---

## Project Structure

The backend is organized into multiple Django apps:

* `auth_app` – authentication and user profiles
* `offers_app` – offers and offer details
* `orders_app` – orders and order statistics
* `reviews_app` – reviews
* `core` – project-wide configuration and shared endpoints

Each app keeps API-related code inside its own `api/` directory, including serializers, views, permissions, and URL configuration.

---

## Environment Variables

The project reads sensitive and environment-specific settings from a `.env` file.

| Variable               | Description                    | Example               |
| ---------------------- | ------------------------------ | --------------------- |
| `DJANGO_SECRET_KEY`    | Secret key used by Django      | `your-secret-key`     |
| `DJANGO_DEBUG`         | Enables or disables debug mode | `True`                |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts  | `127.0.0.1,localhost` |

The `.env` file is ignored by Git and must not be uploaded to the repository.

---

## Authentication

Protected API endpoints use Django REST Framework token authentication.

After a successful registration or login, the API returns an authentication token.

Send the token in the `Authorization` header:

```text
Authorization: Token <your-token>
```

Public endpoints do not require this header.

---

## API Overview

All application endpoints are available below `/api/`.

### Authentication and Profiles

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

The offer list supports search, filtering, ordering, and pagination.

Supported query parameters include:

```text
creator_id
min_price
max_delivery_time
ordering
search
page_size
```

Business users create offers with exactly three offer details:

```text
basic
standard
premium
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

Orders are created from an existing offer detail. The order stores a snapshot of the selected offer detail so later offer changes do not change existing orders.

Supported order statuses are:

```text
in_progress
completed
cancelled
```

### Reviews

```text
GET    /api/reviews/
POST   /api/reviews/
PATCH  /api/reviews/{id}/
DELETE /api/reviews/{id}/
```

Customers can create one review per business user.

The review list supports filtering by:

```text
business_user_id
reviewer_id
```

and ordering by:

```text
updated_at
rating
```

### Platform Information

```text
GET /api/base-info/
```

This public endpoint returns aggregated platform information such as:

* review count
* average rating
* business profile count
* offer count

---

## Offer Pagination

The offer list uses page-number pagination.

The default page size is configured by the backend, while clients can request a different size with the `page_size` query parameter.

Example:

```text
GET /api/offers/?page_size=6
```

---

## Media Files

Profile images and offer images are stored as media files.

During local development they are served through Django when debug mode is enabled.

The project uses:

```text
MEDIA_URL=/media/
```

Uploaded media files are ignored by Git.

---

## CORS and Frontend Integration

CORS is configured for the local Coderr frontend.

The default allowed development origins are:

```text
http://127.0.0.1:5500
http://localhost:5500
```

If the frontend runs on a different host or port, update `CORS_ALLOWED_ORIGINS` in `core/settings.py`.

The backend API runs locally at:

```text
http://127.0.0.1:8000/api/
```

---

## Django Admin

The project uses Django's administration interface for managing application data.

Create an administrator with:

```bash
python manage.py createsuperuser
```

Then start the server and open:

```text
http://127.0.0.1:8000/admin/
```

The admin interface provides access to users, profiles, authentication tokens, offers, offer details, orders, and reviews.

---

## Testing

Run the complete automated test suite with:

```bash
python manage.py test
```

Run a specific application test suite with:

```bash
python manage.py test auth_app
python manage.py test offers_app
python manage.py test orders_app
python manage.py test reviews_app
python manage.py test core
```

Check the Django project configuration with:

```bash
python manage.py check
```

---

## Test Coverage

Run the test suite with Coverage.py:

```bash
coverage erase
coverage run manage.py test
coverage report -m
```

An HTML coverage report can also be generated with:

```bash
coverage html
```

The generated coverage files should not be committed to the repository.

---

## Database

The development environment uses SQLite.

Create or update the local database with:

```bash
python manage.py migrate
```

The database file is intentionally excluded from version control.

Do not commit:

```text
db.sqlite3
```

---

## Git and Repository Notes

This repository contains only the backend implementation.

The following local or generated files are excluded from Git:

```text
.venv/
.env
db.sqlite3
media/
__pycache__/
*.pyc
.coverage
coverage.xml
```

Migration files are part of the source code and should remain in version control.

---

## Development Notes

* Keep secrets outside the source code.
* Keep the backend and frontend in separate repositories.
* Do not commit the SQLite database.
* Do not commit uploaded media files.
* Keep migrations in version control.
* Use the API documentation as the source of truth for endpoint behavior.
* Use role-specific permissions for protected actions.
* Keep serializers responsible for validation and transformation.
* Keep views focused on request and API logic.
* Keep permissions focused on access control.
