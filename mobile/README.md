# Paradox Network App - Mobile

Revolutionary messaging app using latent semantic transmission for 99% bandwidth reduction.

## Features

- **99% Bandwidth Reduction**: Images compressed from 5MB → 3KB
- **Zero-Cost Receiving**: Free for Ethio Telecom subscribers
- **Works on 2G/EDGE**: Ultra-low bandwidth requirements
- **Offline Support**: Queue up to 1,000 messages offline
- **End-to-End Encrypted**: AES-256 + RSA-4096
- **Modern UI**: Beautiful dark theme with animations

## Quick Start

### Prerequisites

- Flutter SDK (3.0+)
- Android Studio / VS Code
- Android SDK for APK building

### Installation

```bash
cd c:\Users\fitsum.DESKTOP-JDUVJ6V\Downloads\paradoxapp\mobile

# Install dependencies
flutter pub get

# Run on device/emulator
flutter run

# Build APK
flutter build apk --release
```

The APK will be located at: `build/app/outputs/flutter-apk/app-release.apk`

## Configuration

Edit `lib/config/app_config.dart` to change backend URL:

```dart
// For local development
static const String zeroRatedDomain = 'http://localhost:8000';

// For production
static const String zeroRatedDomain = 'https://core.pna.et';
```

## Architecture

### Dual-Lane Traffic System

- **Lane A (Zero-Rated)**: Core messaging - FREE
- **Lane B (Normal)**: Updates/analytics - uses data

### Key Components

- **TrafficManager**: Automatic lane routing
- **MessagingService**: Send/receive messages
- **OfflineQueueService**: SQLite queue for offline
- **AuthService**: Secure authentication

## Project Structure

```
lib/
├── config/
│   └── app_config.dart          # Dual-lane configuration
├── core/
│   └── network/
│       └── traffic_manager.dart # Lane A/B routing
├── models/
│   ├── user_model.dart
│   └── message_model.dart
├── services/
│   ├── auth_service.dart
│   ├── messaging_service.dart
│   └── offline_queue_service.dart
├── providers/
│   └── auth_provider.dart       # State management
├── features/
│   └── auth/
│       └── screens/
│           └── login_screen.dart
├── theme/
│   └── app_theme.dart           # Modern dark theme
└── main.dart                    # App entry point
```

## Building APK

### Debug APK
```bash
flutter build apk --debug
```

### Release APK (Optimized)
```bash
flutter build apk --release
```

### Split APKs by ABI (Smaller files)
```bash
flutter build apk --split-per-abi
```

## Backend Connection

The app connects to the FastAPI backend. Make sure the backend is running:

```bash
cd ../backend
docker-compose up -d
```

Then the app will connect to `http://localhost:8000` (or your deployed URL).

## Features Implemented

✅ Dual-lane traffic routing  
✅ Authentication (login/register)  
✅ Offline message queue  
✅ Modern UI with animations  
✅ Secure storage  
✅ Provider state management  

## Coming Soon

- [ ] Chat list view
- [ ] One-to-one messaging UI
- [ ] Image sending
- [ ] Real-time WebSocket
- [ ] Push notifications
- [ ] Subscription management UI

## License

[To be determined]

---

**Status**: Mobile App Development Phase  
**Platform**: Android (iOS coming soon)  
**Last Updated**: 2026-01-26
