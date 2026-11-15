# HomeFin AI final audit

Audit date: 2026-11-14. Scope: repository source, configuration, migrations,
backend tests, and mobile TypeScript checks. This is a code audit, not proof of
an external production deployment.

## Tested

- Backend Python compilation: passed.
- Backend pytest suite: `1 passed` (only the existing health test).
- Mobile TypeScript check from `mobile`: passed after installing `expo-network`.
- API route registration: verified for authentication, transactions, documents,
  wealth, analytics, assistant, budgets, goals, and recurring schedules.
- Compose health/startup was previously verified locally; port 5432 was occupied
  and PostgreSQL was tested on configurable port 55432.

## Critical findings

None fixed in this audit.

## High findings

- Production deployment, HTTPS, managed database, backup restore, object storage,
  monitoring, and EAS builds are documented but not executed in this workspace.
- The test suite does not cover financial reconciliation, household isolation,
  role escalation, token expiry, upload signatures, offline retries, or backup
  restore. The application must not be called production-ready on this evidence.
- OAuth/JWT refresh tokens are stateless and logout does not revoke an already
  issued token. Add token versioning or a server-side revocation store before
  production use.
- Rate limiting is process-local and unsuitable as the sole control with multiple
  workers. Put a gateway or Redis-backed limiter in front of production.

## Medium findings

- XIRR is not implemented; investment returns currently expose absolute and
  realized/unrealized foundations only.
- EPF/EPS passbook ingestion and separate EPS balance calculations are not complete.
- Report PDF/Excel/CSV export is not implemented; analytics JSON is available.
- Recurring schedules are stored and reviewable, but a production scheduler and
  notification delivery are not implemented.
- OCR uses FastAPI background tasks rather than durable Celery/Redis jobs; a
  process crash can lose an in-flight OCR task.
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

The repository has Decimal-backed records and explicit transaction types, but no
independent reconciliation test dataset was present and no XIRR implementation
exists. Transfers, investment contributions, and loan principal treatment are
encoded in analytics exclusions, but require dedicated fixture tests before
trusting reports for family decisions.

## Audit conclusion

Not production-ready. The repository is a substantial development foundation,
not an independently verified production financial system.
