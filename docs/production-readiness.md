# Production readiness gate

Status: **BLOCKED — development only**.

Required before family production use:

1. Deploy behind HTTPS with a managed PostgreSQL instance on a private network.
2. Run all migrations in a controlled release job.
3. Configure private object storage and signed URLs.
4. Add server-side token revocation/rotation and Redis or gateway rate limiting.
5. Add fixture-based financial reconciliation and authorization/security tests.
6. Implement and test backup restoration.
7. Integrate XIRR/EMI calculations into all required reports, add report
   exports, EPF/EPS separation, durable OCR jobs, and recurring transaction
   review/generation.
8. Resolve the mobile dependency audit findings and verify EAS APK/AAB builds.
9. Perform a penetration test and review sensitive logging before onboarding
   family data.
