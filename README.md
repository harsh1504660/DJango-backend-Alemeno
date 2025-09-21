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
git clone git@github.com:harsh1504660/DJango-backend-Alemeno.git
```
```bash
cd DJango-backend-Alemeno
```

Running the container
```bash
docker-compose up --build
```

Testing the cases
```bash
docker-compose exec web pytest -v
```

Shut down the container
```bash
docker-compose down -v
```

## Architecture Overview
```mermaid
graph TD
    A[customer_data.xlsx] -->|ingest_data| B[(Postgres DB)]
    C[loan_data.xlsx] -->|ingest_data| B

    subgraph API[REST API Endpoints]
        D1[POST /api/register/] --> B
        D2[POST /api/check-eligibility/] --> E[Eligibility Rules]
        E --> B
        D3[POST /api/create-loan/] --> B
        D4[GET /api/view-loan/(loan_id)] --> B
        D5[GET /api/view-loans/(customer_id)] --> B
    end

    subgraph Infra[Background Services]
        F[Celery Worker] -->|runs ingest_data| B
        G[Redis Broker] --> F
        G --> API
    end


