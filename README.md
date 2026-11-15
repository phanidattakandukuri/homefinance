# HomeFin AI

HomeFin AI is a private household financial management application for multiple
household members and a combined household view.

## Current phase

Phase 2 establishes the modular FastAPI backend foundation. It includes
versioned API routes, environment configuration, CORS and logging, consistent
validation errors, SQLAlchemy 2.x sessions, and Alembic integration. Business
features are intentionally not implemented yet.

## Quick start

1. Copy `.env.example` to `.env` and set a local password and JWT secret.
2. Start PostgreSQL: `docker compose -f infrastructure/docker-compose.yml up -d postgres`.
3. Create a Python 3.12 virtual environment in `backend`.
4. Install the backend and test extras:
   `pip install -e ".[test]"`.
5. From `backend`, run the API:
   `uvicorn app.main:app --reload`.
6. Verify `http://127.0.0.1:8000/api/v1/health` and
   `http://127.0.0.1:8000/api/v1/health/database`.

OpenAPI is available at `http://127.0.0.1:8000/docs` and
`http://127.0.0.1:8000/openapi.json`. Run migrations from `backend` with
`alembic upgrade head`; Alembic reads `DATABASE_URL` from the environment.

The database data is stored in the named `homefin-postgres-data` volume. Do
not expose PostgreSQL publicly in deployment.

## Documentation

- [Architecture](docs/architecture.md)
- [Database design](docs/database-design.md)
- [API documentation](docs/api-documentation.md)
- [Security](docs/security.md)
- [Development setup](docs/development-setup.md)
- [Phase progress](docs/phase-progress.md)
