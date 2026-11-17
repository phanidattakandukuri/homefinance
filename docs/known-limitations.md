# Known limitations

- No hosted production environment is configured in this repository.
- No backup restore has been executed against a production-like database.
- JWT logout is client-side token deletion only; server-side revocation is required.
- Export formats, durable OCR workers, recurring schedulers, and push
  notifications remain incomplete. XIRR and EMI calculation primitives exist,
  but require complete dated inputs.
- Existing automated coverage is minimal and does not prove financial correctness
  or cross-household isolation.
- Mobile package vulnerability review is pending; do not distribute a release
  APK until it is resolved or formally accepted.

PF balances, interest credits, withdrawals, and gratuity receipts are manual
records; salary data alone never fabricates a balance. Invitation tokens are
currently returned to the authorized administrator for secure manual delivery;
production should connect a trusted email provider.
