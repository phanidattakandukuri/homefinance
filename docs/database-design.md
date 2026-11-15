# Database design

PostgreSQL is the source of truth. Monetary values will use `NUMERIC` and map
to Python `Decimal`; floating-point values are prohibited for financial data.
Timestamps will be stored consistently and interpreted using each household's
configured IANA timezone.

Future schema work must use Alembic migrations. Financial records will carry a
household identifier and, where applicable, a member identifier. Transaction
classification will distinguish transfers, card bill payments, investment
contributions, redemptions, realized gains, and unrealized gains to prevent
double counting.

Phase 1 creates no financial tables yet.
