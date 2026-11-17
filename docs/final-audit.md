# HomeFin AI final audit

Audit date: 2026-11-16. Scope: repository source, configuration, migrations,
backend tests, and mobile TypeScript/bundle checks. This is a code audit, not proof of
an external production deployment.

## Tested

- Backend Python compilation: passed.
- Backend pytest suite: `12 passed`.
- Mobile TypeScript check from `mobile`: passed.
- Android Expo embed bundle: passed.
- API route registration: verified for authentication, transactions, documents,
  wealth, provident-fund/gratuity, analytics, assistant, budgets, goals,
  recurring schedules, exports, and password-reset flows.
- Compose health/startup was previously verified locally; port 5432 was occupied
  and PostgreSQL was tested on configurable port 55432.

## Critical findings

Member profiles, invitation linking, transaction privacy, typed wealth records,
PF/gratuity ledgers, transfer accounting, XIRR/EMI primitives, recurring
generation, CSV/XLSX/PDF transaction export, password reset, and token revocation were
  notification preferences, and persisted OCR jobs were implemented with
  Alembic migrations through `20261114_19`.

## High findings

- Production deployment, HTTPS, managed database, backup restore, object storage,
  monitoring, and EAS builds are documented but not executed in this workspace.
- The test suite does not cover financial reconciliation, household isolation,
  role escalation, token expiry, upload signatures, offline retries, or backup
  restore. The application must not be called production-ready on this evidence.
- JWT access and refresh tokens use server-side per-user token versioning;
  logout and password changes revoke previously issued tokens. Password-reset
  tokens are one-time, hashed, and expiring. A distributed session store may
  still be needed for independent multi-device revocation.
- Rate limiting is process-local and unsuitable as the sole control with multiple
  workers. Put a gateway or Redis-backed limiter in front of production.

## Medium findings

- XIRR and EMI calculation primitives are implemented and exposed through
  investment performance and loan schedule endpoints; input completeness still
  determines whether a result is available.
- EPF/EPS account types and separate EPS contribution/balance calculations are
  implemented; automated EPFO passbook ingestion remains future work.
- Transaction CSV, XLSX, and paginated PDF exports are implemented.
- Recurring schedules can be generated through an idempotent `run-due` endpoint
  and the Render cron runner in `app.jobs.run_recurring`; notification
  preferences are persisted per household/user, while provider delivery remains
  deployment work.
- OCR jobs now have persisted status, attempt counts, failure details, and a
  retry endpoint. The current execution path still uses FastAPI background
  tasks; a worker/cron is recommended to drain queued jobs at scale.
- Monthly snapshots have creation metadata but controlled recalculation/audit
  workflow is incomplete.
- The local rate limiter and local upload storage are development safeguards only.

## Low findings

- PyMuPDF emits a deprecation warning for the compatibility `fitz` import.
- Existing test execution emits pytest cache permission warnings in this managed
  workspace.
- Mobile npm audit could not reach the registry endpoint; the local install
  reported 33 vulnerabilities, including 6 high and 1 critical, requiring a
  dependency review before release.

## Financial review conclusion

The repository has Decimal-backed records, explicit transaction types, linked
transfers, ownership-aware analytics, XIRR/EMI services, and PF/gratuity
ledgers. Independent database-fixture reconciliation and end-to-end isolation
tests are still required before trusting reports for family decisions.

## Audit conclusion

Not production-ready. The repository is a substantial development foundation,
not an independently verified production financial system.
