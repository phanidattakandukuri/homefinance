# Architecture

HomeFin AI uses a modular monolith. The backend is a FastAPI application with
separate API, schema, service, repository, and database layers. PostgreSQL is
the authoritative persistence store and is run locally through Docker Compose.

Planned bounded modules are auth, households, members, salary, transactions,
attachments, OCR, investments, PF, assets, liabilities, analytics, reports,
and the AI assistant. These are not separate deployables.

The AI assistant will only explain values calculated by backend services. It
will not be an authority for balances, returns, salary, or net worth.

Implemented domain boundaries include household/member profiles and
invitation linking, salary and transactions, typed wealth records, PF and
gratuity manual ledgers, planning, analytics, CSV export, and assistant
evidence. Financial records retain household/member ownership and use Decimal
values. Personal analytics applies member permissions and asset ownership
percentages; household analytics aggregates the full household.

Alembic migrations are the only supported schema-change mechanism. The mobile
client consumes backend-calculated dashboards and uses SecureStore for tokens;
public Expo environment variables contain only the HTTPS API URL.
