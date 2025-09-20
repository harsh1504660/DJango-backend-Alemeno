# Credit Approval System - Django + DRF

This project implements the backend assignment "Credit Approval System" using Django, Django REST Framework, PostgreSQL, Celery (with Redis), and Docker Compose.

Features:
- Data models for Customer and Loan data.
- Background ingestion of provided Excel files (`/data/customer_data.xlsx` and `/data/loan_data.xlsx`) using Celery task.
- APIs:
  - POST /api/register/
  - POST /api/check-eligibility/
  - POST /api/create-loan/
  - GET  /api/view-loan/<loan_id>/
  - GET  /api/view-loans/<customer_id>/
- Dockerized (web, db, redis, worker). Run `docker-compose up --build`.

Notes:
- The uploaded Excel files should be mounted into the container at `/data/customer_data.xlsx` and `/data/loan_data.xlsx`.
- For development without Docker you can run `pip install -r requirements.txt`, create a Postgres DB, update settings, run migrations, then start django and celery worker.

