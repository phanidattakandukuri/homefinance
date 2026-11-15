# Security

Secrets belong in environment variables and must not be committed. The
provided `.env.example` contains placeholders only. PostgreSQL is bound to the
local host for development and is not intended for public exposure.

Planned authentication will use Argon2 password hashing and JWTs stored
securely on mobile. Backend authorization will enforce household membership
and roles; client-side checks are not trusted. Bank passwords, UPI PINs, OTPs,
CVVs, and EPFO passwords will never be stored.
