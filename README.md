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

## Setup

Cloneing the repo
```bash
git clone xyz
```
```bash
cd xyz
```
docker
```bash
jay hind
