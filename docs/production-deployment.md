# Production deployment and recovery

Production must use a managed PostgreSQL provider or a private PostgreSQL
network. Do not publish port 5432 to the internet. Restrict database access to
the backend network, enable provider encryption, automated backups, retention,
monitoring, and credential rotation.

## Deploy

1. Provision a private managed PostgreSQL database and object storage bucket.
2. Configure `DATABASE_URL`, `APP_ENV=production`, `APP_SECRET_KEY`,
   `JWT_SECRET_KEY`, and private storage credentials in the deployment secret
   manager. Never commit them.
3. Build and deploy `backend/Dockerfile` behind an HTTPS reverse proxy.
4. Run `alembic upgrade head` as a reviewed release step before switching
   traffic. Do not use reload mode in production.
5. Monitor `/health` and `/health/database`, structured logs, error rates, and
   database pool saturation.

## Backup and restore

Use the managed provider's encrypted automated backups and periodically test a
restore into a separate isolated database. A PostgreSQL example is:

```powershell
pg_dump --format=custom --file=homefin.backup $env:PRODUCTION_DATABASE_URL
createdb $env:RESTORE_DATABASE_NAME
pg_restore --exit-on-error --dbname=$env:RESTORE_DATABASE_URL homefin.backup
alembic upgrade head
```

Verify row counts, household isolation, health endpoints, and a representative
report in the restored database before declaring recovery successful. Rotate
database credentials after a suspected exposure.

## Private documents

Use a private object-storage bucket in production. Store only opaque keys in the
database and issue short-lived signed URLs only after authorization. Never
serve the bucket publicly.

## Mobile builds

From `mobile`:

```powershell
npx eas login
npx eas build --profile development --platform android
npx eas build --profile preview --platform android   # family APK
npx eas build --profile production --platform android # Play Store AAB
```

Install the preview APK from the EAS link, enable “Install unknown apps” for
the browser/files app when Android asks, and verify the HTTPS API URL. Distribute
updates by publishing a new signed APK/AAB; keep backend API compatibility for
the previous mobile version during rollout. Family data is server-side and is
restored from the database backup, not from the APK.
