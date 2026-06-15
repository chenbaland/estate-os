# Phase 6 — Mobile Implementation

**EstateOS Mobile Application**

Cross-platform resident and security app built with Expo SDK 52, React Native 0.76, and Expo Router. Covers visitor passes, gate scanning, SOS, billing, facilities, and AI concierge.

---

## Overview

| Attribute | Value |
|-----------|-------|
| Framework | Expo SDK 52 |
| Runtime | React Native 0.76 |
| Navigation | Expo Router (file-based) |
| Styling | NativeWind 4 (Tailwind) + StyleSheet tokens |
| State | Zustand (persisted via AsyncStorage) |
| Data Fetching | TanStack React Query v5 |
| Auth Storage | expo-secure-store |
| Biometrics | expo-local-authentication |
| Push | expo-notifications |
| QR | react-native-qrcode-svg + expo-camera |

---

## Folder Structure

```
mobile/
├── app/                        # Expo Router screens (file-based routing)
│   ├── _layout.tsx             # Root layout (providers, splash)
│   ├── index.tsx               # Entry redirect (auth check)
│   ├── (auth)/                 # Authentication flow
│   │   ├── _layout.tsx
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/                 # Main tab navigation
│   │   ├── _layout.tsx         # Tab bar configuration
│   │   ├── index.tsx           # Home dashboard
│   │   ├── visitors.tsx        # Visitor pass list
│   │   ├── community.tsx       # Announcements, polls
│   │   ├── marketplace.tsx     # Product browse
│   │   └── profile.tsx         # Settings, biometric toggle
│   ├── visitors/
│   │   ├── create.tsx          # Create visitor pass + QR
│   │   └── scan.tsx            # Gate QR scanner (security)
│   ├── sos/
│   │   └── index.tsx           # Emergency SOS trigger
│   ├── billing/
│   │   └── index.tsx           # Invoices and payment
│   ├── facilities/
│   │   └── book.tsx            # Amenity booking
│   ├── maintenance/
│   │   └── create.tsx          # Submit maintenance ticket
│   └── ai/
│       └── chat.tsx            # AI concierge chat
├── src/
│   ├── components/             # Shared UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   ├── Avatar.tsx
│   │   ├── Badge.tsx
│   │   ├── Header.tsx
│   │   ├── TabBar.tsx
│   │   └── index.ts
│   ├── constants/
│   │   └── theme.ts            # Design tokens (matches web)
│   ├── hooks/
│   │   ├── useAuth.ts          # Login, logout, biometric unlock
│   │   └── useNotifications.ts # Push token registration
│   ├── lib/
│   │   └── api.ts              # API client (Bearer + X-Estate-Id)
│   ├── stores/
│   │   ├── auth.ts             # Auth state + secure token storage
│   │   └── estate.ts           # Active estate context
│   └── types/
│       └── index.ts
├── assets/                     # App icon, splash, notification icon
├── app.json                    # Expo configuration
├── Dockerfile                  # Web export container (optional)
├── global.css                  # NativeWind global styles
├── tailwind.config.js
├── metro.config.js
├── babel.config.js
└── package.json
```

---

## Architecture Rationale

### Expo Router File-Based Navigation

Screens map directly to file paths, mirroring Next.js App Router conventions. Route groups `(auth)` and `(tabs)` provide layout nesting without URL segments. Deep links (visitor pass share URLs) resolve to specific screens automatically.

### Shared Design Tokens

`src/constants/theme.ts` mirrors `frontend/src/styles/tokens.css` with HSL-to-hex conversion for React Native StyleSheet usage. Spacing, radius, font sizes, and shadows are exported as constants ensuring visual parity with the web app.

### Secure Token Management

Unlike web localStorage, mobile tokens use `expo-secure-store` (Keychain on iOS, EncryptedSharedPreferences on Android). The auth store handles:

- Login → store access + refresh tokens
- API 401 → silent refresh → retry
- Logout → clear secure store + AsyncStorage preferences
- Biometric unlock → re-authenticate without re-entering password

### API Client Parity

`src/lib/api.ts` mirrors `frontend/src/lib/api.ts`:

- Base URL: `EXPO_PUBLIC_API_URL` (default `http://localhost:8000/api/v1`)
- Headers: `Authorization: Bearer`, `X-Estate-Id`
- Error normalization for alert/toast display

### Push Notifications

`useNotifications` hook registers device tokens with the backend after login:

1. Request permission via `expo-notifications`
2. Obtain Expo push token (requires `EXPO_PUBLIC_PROJECT_ID`)
3. Register token via `POST /api/v1/notifications/devices/`
4. Handle foreground/background notification taps with deep links

---

## Key Screens

| Screen | Route | Description |
|--------|-------|-------------|
| Home | `(tabs)/index` | Dashboard stats, quick actions, activity feed |
| Visitors | `(tabs)/visitors` | Active/expired passes list |
| Create Pass | `visitors/create` | Form → QR code generation |
| Gate Scan | `visitors/scan` | Camera QR scanner for security role |
| SOS | `sos/index` | Long-press emergency alert |
| Billing | `billing/index` | Outstanding balance, pay invoice |
| Marketplace | `(tabs)/marketplace` | Product browse and cart |
| AI Chat | `ai/chat` | Conversational estate assistant |
| Profile | `(tabs)/profile` | Settings, biometric toggle, logout |

Wireframes: [`docs/phase-03/wireframes.md`](../phase-03/wireframes.md)

---

## Local Development

### Prerequisites

- Node.js 20+
- Expo CLI (`npx expo`)
- iOS Simulator (macOS) or Android Emulator
- Backend running on port 8000

### Setup

```bash
cd mobile
npm install

cp .env.example .env
# EXPO_PUBLIC_API_URL=http://localhost:8000/api/v1
# EXPO_PUBLIC_PROJECT_ID=your-expo-project-id
```

### Run

```bash
npm start          # Expo dev server (QR code for Expo Go)
npm run ios        # iOS Simulator
npm run android    # Android Emulator
npm run typecheck  # TypeScript validation
npm run lint       # Expo lint
```

### Physical Device Testing

1. Install [Expo Go](https://expo.dev/go) on device
2. Ensure device and dev machine share network
3. Scan QR from terminal output
4. For camera (gate scan) and biometrics, use development build:

```bash
npx expo run:ios
npx expo run:android
```

---

## Production Build

### EAS Build (Recommended)

```bash
npx eas build --platform all
```

Configure `eas.json` with production credentials. Update `app.json`:

```json
{
  "expo": {
    "extra": {
      "eas": {
        "projectId": "your-expo-project-id"
      }
    }
  }
}
```

### App Store / Play Store

| Platform | Requirement |
|----------|-------------|
| iOS | Apple Developer account, provisioning profiles |
| Android | Google Play Console, `google-services.json` for push |

### Environment Variables (Production)

| Variable | Description |
|----------|-------------|
| `EXPO_PUBLIC_API_URL` | Production API URL (`https://api.estateos.app/api/v1`) |
| `EXPO_PUBLIC_PROJECT_ID` | Expo project ID for push tokens |

### Docker Web Preview

Optional static web export for demos:

```bash
docker build -t estateos-mobile \
  --build-arg EXPO_PUBLIC_API_URL=https://api.estateos.app/api/v1 .
docker run -p 8080:80 estateos-mobile
```

---

## Platform-Specific Features

| Feature | Library | Notes |
|---------|---------|-------|
| Biometric unlock | expo-local-authentication | Face ID, Touch ID, fingerprint |
| QR generation | react-native-qrcode-svg | Visitor pass sharing |
| QR scanning | expo-camera | Gate security workflow |
| Push notifications | expo-notifications | Requires physical device |
| Secure storage | expo-secure-store | JWT tokens |
| Haptic feedback | expo-haptics | SOS trigger confirmation |

---

## Security Considerations

- Tokens never stored in AsyncStorage (only secure store)
- SOS requires 3-second long-press to prevent accidental triggers
- Biometric unlock optional; password always available as fallback
- Certificate pinning planned for production API calls
- Deep links validated against allowed route patterns

---

## Related Documentation

- [Mobile README](../../mobile/README.md) — Quick start guide
- [Design System](../phase-03/design-system.md)
- [Screen Specifications](../phase-03/screens.md)
- [Backend Implementation](../phase-04/README.md)
- [Frontend Implementation](../phase-05/README.md)
- [Testing Strategy](../phase-07/README.md)
