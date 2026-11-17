# Database design

PostgreSQL is the source of truth. Monetary values will use `NUMERIC` and map
to Python `Decimal`; floating-point values are prohibited for financial data.
Timestamps will be stored consistently and interpreted using each household's
configured IANA timezone.

All schema work uses Alembic migrations. Financial records carry a
household identifier and, where applicable, a member identifier. Transaction
classification will distinguish transfers, card bill payments, investment
contributions, redemptions, realized gains, and unrealized gains to prevent
double counting.

Current migrations include authentication/households, salary, transactions,
documents, wealth, analytics, planning, member profiles, invitations, and
manual PF/gratuity ledgers. Ownership percentages and linked transfer records
are used to keep household and personal calculations reconcilable.
