# HomeFin AI mobile app

This Expo Router app uses TypeScript, TanStack Query for server state, Zustand
for session state, and Expo SecureStore for tokens. The app intentionally does
not use mock financial data: dashboard and activity screens remain empty until
an authenticated household ID is configured.

## Windows setup

```powershell
Set-Location mobile
npm install
Copy-Item .env.example .env
# Replace 192.168.1.100 with the Windows computer's LAN IPv4 address.
npx expo start
```

For Expo Go on a physical Android device, do not use `localhost`; that points
to the phone. Use the development computer's LAN address, for example
`http://192.168.1.100:8000/api/v1`, and allow the backend port through the
Windows firewall. For deployment, use the hosted HTTPS API URL.

The current backend exposes authentication, household onboarding, analytics,
transactions, and household/member read endpoints. The dashboard and activity
screens use those real responses only; empty and error states are shown when
there is no household or no data. Wealth totals are shown through the
dashboard, while detailed wealth screens remain explicitly disabled because
the current backend has write endpoints but no corresponding list endpoints.
Receipt upload, OCR, notifications, and investment-specific forms are also
not enabled until their full backend workflows are available.

The app validates registration and transaction inputs with React Hook Form and
Zod. Tokens are persisted in Expo SecureStore and refreshed through
`POST /auth/refresh?refresh_token=...`. The API client accepts an `AbortSignal`
through standard `RequestInit` options for cancellable requests.

Run checks with `npm run typecheck` and `npm run lint`.
