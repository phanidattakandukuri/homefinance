# API documentation

## Health

`GET /health` returns service metadata without requiring authentication:

```json
{
  "status": "ok",
  "service": "HomeFin AI API",
  "version": "0.1.0"
}
```

Interactive OpenAPI documentation is available at `/docs` in development.

## Member and account lifecycle

- `GET /api/v1/households/{household_id}/members/{member_id}` retrieves one
  member profile.
- `PATCH /api/v1/households/{household_id}/members/{member_id}` updates an
  authorized member profile or role.
- `DELETE /api/v1/households/{household_id}/members/{member_id}` deactivates a
  member while preserving historical records.
- `POST /api/v1/households/{household_id}/invitations` creates a seven-day,
  one-time invitation token.
- `POST /api/v1/auth/invitations/accept` creates or links the invited account.
- `POST /api/v1/auth/password` changes the authenticated user's password.
- `POST /api/v1/auth/password/reset-request` prepares a one-time reset token
  without revealing whether an email is registered.
- `POST /api/v1/auth/password/reset` consumes the expiring reset token.

## Wealth, PF, loans, and investment calculations

Wealth assets support ownership percentages and liabilities support lender,
interest type, EMI frequency, next EMI date, tenure, and associated assets.
Liability payment endpoints preserve principal and interest separately.

- `/api/v1/households/{household_id}/pf/accounts` and nested `entries` provide
  manual, auditable PF records.
- `/api/v1/households/{household_id}/pf/gratuity` stores estimated gratuity
  separately from actual receipts.
- `/api/v1/households/{household_id}/wealth/investments/{investment_id}/performance`
  returns invested amount, current valuation, gain/loss, and XIRR where the
  available dated cash flows are solvable.
- `/api/v1/households/{household_id}/wealth/liabilities/{liability_id}/schedule`
  returns a Decimal-based principal/interest amortization schedule when loan
  metadata is complete.

## Financial category and wealth contracts

Transaction categories now expose `category_type` values (`income`, `expense`,
`transfer`, `investment`, `debt`, or `other`). Transaction creation rejects
incompatible category/type combinations, preventing income from being entered
as an expense and keeping investment/debt activity distinct.

Wealth endpoints provide typed list and detail data for instruments,
investments, investment transactions, valuations, assets, and liabilities.
All endpoints require authenticated household membership.

`POST /api/v1/households/{household_id}/transfers` atomically creates linked
transfer-out and transfer-in records for two household members. Transfers are
excluded from household income and expense totals while remaining available in
each member's transaction history.

`GET /api/v1/households/{household_id}/analytics/export/transactions.csv`
exports authorized transaction history as CSV. Owners/admins may filter by
member and date range; regular members are automatically restricted to their
own records.

The same authorization and filters are available at
`GET /api/v1/households/{household_id}/analytics/export/transactions.xlsx`
for spreadsheet-compatible XLSX output.

PDF output is available at
`GET /api/v1/households/{household_id}/analytics/export/transactions.pdf`.
It contains a paginated, human-readable transaction summary and applies the
same authorization and filters.

`GET /api/v1/households/{household_id}/transactions/{transaction_id}/audit`
returns the authorized audit history for a transaction, including creation,
edits, voids, and transfer-side metadata.

`POST /api/v1/households/{household_id}/recurring/run-due` generates due
recurring transactions through an idempotency key and advances each schedule.
It is safe to invoke from a deployment cron or job runner; a durable scheduler
is still an operational deployment responsibility.

Document uploads create a persisted OCR job. Job state is available at
`GET /api/v1/households/{household_id}/documents/{document_id}/ocr-job`; failed
jobs can be retried with `POST .../ocr-job/retry`. This preserves job state and
retry metadata across API process restarts, while the deployment still needs a
worker/cron to drain queued jobs at scale.
