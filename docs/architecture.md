# Architecture

HomeFin AI uses a modular monolith. The backend is a FastAPI application with
separate API, schema, service, repository, and database layers. PostgreSQL is
the authoritative persistence store and is run locally through Docker Compose.

Planned bounded modules are auth, households, members, salary, transactions,
attachments, OCR, investments, PF, assets, liabilities, analytics, reports,
and the AI assistant. These are not separate deployables.

The AI assistant will only explain values calculated by backend services. It
will not be an authority for balances, returns, salary, or net worth.
