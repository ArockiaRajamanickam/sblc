# SBLC Digital Management Platform

A system for managing Standby Letters of Credit (SBLC) end to end: issuance, banking compliance checks (KYC/AML), ledger verification, loan disbursement, and role-based access for every party involved.

The backend follows Domain-Driven Design and Clean Architecture, mostly because SBLC workflows get complicated fast and I wanted the domain logic to stay readable.

## Stack

FastAPI with SQLAlchemy 2.0 and Alembic migrations, PostgreSQL for relational data, Redis for caching and idempotency, and a React frontend in `frontend/`.

## Running it

```bash
docker-compose up --build
```

API docs come up at `http://localhost:8000/docs`. Config is environment driven, see `docker-compose.yml` for the variables and override the defaults for anything past local development.

## Status

This is a development snapshot. The production work (tests, security review, deployment docs) continues in a private repo.
