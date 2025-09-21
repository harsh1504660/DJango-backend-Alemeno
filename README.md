# Credit Approval System - Django + DRF

This project implements the backend assignment "Credit Approval System" using Django, Django REST Framework, PostgreSQL, Celery (with Redis), and Docker Compose.

🔗 **Demo video Link**: [Link](https://voicecast-ai.netlify.app/)

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
git clone https://github.com/harsh1504660/DJango-backend-Alemeno.git
```
```bash
cd .\DJango-backend-Alemeno\
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
flowchart TD

    subgraph DataIngestion[Data Ingestion]
        A1[customer_data.xlsx] -->|Ingest| DB[(Postgres Database)]
        A2[loan_data.xlsx] -->|Ingest| DB
    end

    subgraph DjangoApp[Django + DRF APIs]
        B1[POST /api/register/] --> DB
        B2[POST /api/check-eligibility/] --> Logic[Rule-based Credit Scoring]
        Logic --> DB
        B3[POST /api/create-loan/] --> DB
        B4[GET /api/view-loan/loan_id/] --> DB
        B5[GET /api/view-loans/customer_id/] --> DB
    end

    subgraph CeleryWorker[Celery Worker]
        W1[Background Task: ingest_data] --> DB
    end

    subgraph Infra[Infrastructure]
        DB[(Postgres)]
        R[(Redis - Broker)]
    end

    DataIngestion --> CeleryWorker
    CeleryWorker --> DjangoApp
    DjangoApp --> R
    CeleryWorker --> R


