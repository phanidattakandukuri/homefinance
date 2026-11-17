# Security

Secrets belong in environment variables and must not be committed. The
provided `.env.example` contains placeholders only. PostgreSQL is bound to the
local host for development and is not intended for public exposure.

Authentication uses Argon2 password hashing and JWTs stored securely on mobile.
Backend authorization enforces household membership, member privacy, and roles;
client-side checks are not trusted. Bank passwords, UPI PINs, OTPs, CVVs, and
EPFO passwords are never stored.

Household invitations store only a SHA-256 token hash, expire after seven days,
and can be accepted once. The current API returns the raw token to the
authorized administrator for manual delivery; production should deliver it
through a trusted email or messaging provider and avoid logging it.

Household invitations store only a SHA-256 token hash, expire after seven days,
and can be accepted once. The current API returns the raw token to the
authorized administrator for manual delivery; production should deliver it
through a trusted email or messaging provider and avoid logging it.
