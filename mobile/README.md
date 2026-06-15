# EstateOS Mobile

React Native mobile app for the EstateOS estate management platform. Built with Expo SDK 52, Expo Router, React Query, Zustand, and NativeWind.

## Features

- **Authentication** — Email/password login, registration, secure token storage (`expo-secure-store`)
- **Biometric unlock** — Face ID / fingerprint via `expo-local-authentication`
- **Push notifications** — `expo-notifications` with device token registration
- **Visitor management** — Create QR passes, gate scanning for security roles
- **SOS emergency** — One-tap alert to estate security
- **Billing, facilities, maintenance, AI concierge** — Core resident workflows
- **Design system** — Tokens aligned with the EstateOS web app (`src/constants/theme.ts`)

## Tech Stack

| Layer | Library |
|-------|---------|
| Framework | Expo SDK 52, React Native 0.76 |
| Navigation | Expo Router (file-based) |
| API | React Query + custom `api.ts` client |
| State | Zustand (persisted with AsyncStorage) |
| Styling | NativeWind 4 (Tailwind) + StyleSheet tokens |
| Auth storage | expo-secure-store |
| Biometrics | expo-local-authentication |
| Notifications | expo-notifications |

## Getting Started

### Prerequisites

- Node.js 20+
- [Expo CLI](https://docs.expo.dev/get-started/installation/) or `npx expo`
- iOS Simulator (macOS) or Android Emulator
- [Expo Go](https://expo.dev/go) for physical device testing

### Install

```bash
cd mobile
npm install
```

### Environment

Create `.env` in the `mobile/` directory:

```env
EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
EXPO_PUBLIC_PROJECT_ID=your-expo-project-id
```

`EXPO_PUBLIC_PROJECT_ID` is required for push notification token registration on physical devices. Obtain it from [expo.dev](https://expo.dev) after creating a project.

### Run

```bash
# Start dev server
npm start

# iOS
npm run ios

# Android
npm run android
```

### Type Check

```bash
npm run typecheck
```

## Project Structure

```
mobile/
├── app/                    # Expo Router screens
│   ├── (auth)/             # Login, register
│   ├── (tabs)/             # Home, visitors, community, marketplace, profile
│   ├── sos/                # Emergency SOS
│   ├── visitors/           # Create pass, gate scan
│   ├── billing/
│   ├── facilities/
│   ├── maintenance/
│   └── ai/
├── src/
│   ├── components/         # Button, Card, Input, Avatar, Badge, Header, TabBar
│   ├── constants/theme.ts  # Design tokens (matches web)
│   ├── hooks/              # useAuth, useNotifications
│   ├── lib/api.ts          # API client (Bearer + X-Estate-Id)
│   ├── stores/             # auth.ts, estate.ts
│   └── types/
├── assets/                 # App icons and splash
├── Dockerfile              # Optional web export container
└── app.json
```

## API Integration

The mobile client mirrors the web frontend API client:

- Base URL: `EXPO_PUBLIC_API_URL` (default `http://localhost:8000/api/v1`)
- Auth: `Authorization: Bearer <access_token>`
- Tenant scope: `X-Estate-Id: <estate_uuid>`
- Tokens stored in `expo-secure-store`, auto-refreshed on 401

## Push Notifications

1. Create an Expo project at [expo.dev](https://expo.dev)
2. Set `EXPO_PUBLIC_PROJECT_ID` in `.env`
3. For production Android, add `google-services.json` (gitignored)
4. Notifications register automatically after login via `useNotifications`

## Biometric Authentication

Enable from **Profile → Biometric unlock**. Requires enrolled Face ID or fingerprint on the device. Biometric preference is persisted in the auth store.

## Docker (Web Preview)

Build a static web export served by nginx:

```bash
docker build -t estateos-mobile \
  --build-arg EXPO_PUBLIC_API_URL=https://api.estateos.app/api/v1 .
docker run -p 8080:80 estateos-mobile
```

## Building for Production

Use [EAS Build](https://docs.expo.dev/build/introduction/):

```bash
npx eas build --platform all
```

Configure `eas.json` and update `app.json` `extra.eas.projectId` with your Expo project ID.

## License

Proprietary — EstateOS
