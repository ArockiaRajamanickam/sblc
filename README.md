# SBLC Digital Management Platform

A digital **Standby Letter of Credit (SBLC)** management and issuance system covering the full SBLC lifecycle — issuance, banking compliance (KYC/AML), ledger verification, loan disbursement, and multi-party **role-based access control**.

Built with **Domain-Driven Design** and **Clean Architecture** principles for maintainability and security.

## Tech stack

- **Backend** — FastAPI (Python), SQLAlchemy 2.0 + Alembic migrations
- **Data** — PostgreSQL (relational), Redis (caching & idempotency)
- **Frontend** — React (`frontend/`)
- **Infra** — Docker Compose

## Run it

```bash
docker-compose up --build
```

Then open the API docs at `http://localhost:8000/docs`. Configuration is environment-driven — see `docker-compose.yml` for the variables (`DATABASE_URL`, `SECRET_KEY`, …) and override the defaults for anything beyond local development.

## Status

Development snapshot. The production line — test suite, security review, and deployment docs — continues in a private repository.
