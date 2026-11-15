# Development setup

## Prerequisites

- Docker Desktop with Compose
- Python 3.12

## Backend

```powershell
Copy-Item .env.example .env
docker compose --env-file .env -f infrastructure/docker-compose.yml up -d postgres
Set-Location backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[test]"
uvicorn app.main:app --reload
```

Run tests from `backend` with `pytest`. Test the endpoints with
`Invoke-RestMethod http://127.0.0.1:8000/health` and
`Invoke-RestMethod http://127.0.0.1:8000/health/db`.

## PostgreSQL commands

Run these from the repository root:

```powershell
# Status, logs, stop, and restart
docker compose --env-file .env -f infrastructure/docker-compose.yml ps
docker compose --env-file .env -f infrastructure/docker-compose.yml logs -f postgres
docker compose --env-file .env -f infrastructure/docker-compose.yml stop
docker compose --env-file .env -f infrastructure/docker-compose.yml restart postgres

# Readiness check
docker compose --env-file .env -f infrastructure/docker-compose.yml exec postgres pg_isready -U homefin -d homefin

# Connect with psql inside the container
docker compose --env-file .env -f infrastructure/docker-compose.yml exec postgres psql -U homefin -d homefin

# Reset the development database (deletes all data)
docker compose --env-file .env -f infrastructure/docker-compose.yml down -v
docker compose --env-file .env -f infrastructure/docker-compose.yml up -d postgres
```

Docker reads `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and
`POSTGRES_PORT` to initialize and publish PostgreSQL. FastAPI reads
`DATABASE_URL`, `APP_ENV`, `APP_SECRET_KEY`, and `JWT_SECRET_KEY` from `.env`.
When FastAPI runs directly on Windows, use `localhost` and the published port
in `DATABASE_URL`. A containerized backend must instead use the Compose service
hostname `postgres` (for example, `...@postgres:5432/...`). The named volume
`homefin-postgres-data` survives container restarts and ordinary `down`; only
`down -v` removes it.
