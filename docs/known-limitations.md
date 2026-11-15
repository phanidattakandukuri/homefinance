# Known limitations

- No hosted production environment is configured in this repository.
- No backup restore has been executed against a production-like database.
- JWT logout is client-side token deletion only; server-side revocation is required.
- XIRR, export formats, durable OCR workers, recurring schedulers, and push
  notifications remain incomplete.
- Existing automated coverage is minimal and does not prove financial correctness
  or cross-household isolation.
- Mobile package vulnerability review is pending; do not distribute a release
  APK until it is resolved or formally accepted.
