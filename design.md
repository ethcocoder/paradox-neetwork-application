# Paradox Network App - Mobile Design Document

## Overview

The Paradox Network Application is a React Native mobile app for Android that enables ultra-low bandwidth communication by transmitting semantic meaning (latent vectors) instead of raw data. The app includes image and text clipping features with local encoding/decoding to minimize bandwidth usage while maintaining privacy.

## Screen List

1. **Splash Screen** - App launch with logo and branding
2. **Authentication Screen** - Firebase login/signup
3. **Home Screen** - Main dashboard with conversation list
4. **Chat Screen** - Message conversation with sender/receiver
5. **Image Clipper Screen** - Capture/select and clip images
6. **Text Input Screen** - Compose messages with text clipping
7. **Settings Screen** - App configuration and preferences
8. **Profile Screen** - User profile and account management

## Primary Content and Functionality

### Splash Screen
- **Content**: App logo, brand name, loading indicator
- **Functionality**: Auto-navigate to auth or home based on login state

### Authentication Screen
- **Content**: Firebase login form (email/password), signup option
- **Functionality**: 
  - Email/password authentication
  - Firebase integration
  - Redirect to home on success

### Home Screen
- **Content**: 
  - List of active conversations
  - User profile header
  - Quick action buttons (new chat, settings)
- **Functionality**:
  - Tap conversation to open chat
  - Pull-to-refresh conversation list
  - Search conversations
  - Delete conversation option

### Chat Screen
- **Content**:
  - Message list (sender/receiver bubbles)
  - Input area with image/text buttons
  - Recipient info header
- **Functionality**:
  - Display encoded/decoded messages
  - Show bandwidth savings indicator
  - Send image (clipped) or text
  - Local encoding before sending
  - Local decoding on receive
  - Offline queue support

### Image Clipper Screen
- **Content**:
  - Image preview with clipping overlay
  - Crop/adjust controls
  - Confirm/cancel buttons
- **Functionality**:
  - Select image from gallery or camera
  - Define clipping region
  - Encode clipped image to latent vector
  - Send to recipient

### Text Input Screen
- **Content**:
  - Text input field
  - Character count
  - Encoding preview
- **Functionality**:
  - Compose message text
  - Show estimated bandwidth savings
  - Encode text to latent vector
  - Send message

### Settings Screen
- **Content**:
  - Theme toggle (light/dark)
  - Notification settings
  - Privacy settings
  - About section
- **Functionality**:
  - Change app theme
  - Configure notifications
  - Manage privacy options
  - View app version

### Profile Screen
- **Content**:
  - User avatar
  - Display name
  - Email
  - Account status
  - Logout button
- **Functionality**:
  - Edit profile information
  - Change password
  - Logout

## Key User Flows

### Flow 1: Send Encoded Image
1. User taps "Send Image" on Chat Screen
2. Navigate to Image Clipper Screen
3. Select image from gallery or camera
4. Define clipping region
5. Tap "Confirm" to encode
6. Image encoded to 512D latent vector locally
7. Vector sent to Firebase
8. Show bandwidth savings (e.g., "2MB → 4KB")
9. Return to Chat Screen with message sent

### Flow 2: Send Encoded Text
1. User taps "Send Message" on Chat Screen
2. Navigate to Text Input Screen
3. Type message
4. Tap "Send"
5. Text encoded to 512D latent vector locally
6. Vector sent to Firebase
7. Show bandwidth savings
8. Return to Chat Screen with message sent

### Flow 3: Receive and Decode Message
1. Message arrives from Firebase (latent vector)
2. App automatically decodes locally
3. Display decoded content in chat bubble
4. Show sender info and timestamp

### Flow 4: User Authentication
1. App launches, checks login state
2. If not logged in, show Authentication Screen
3. User enters email and password
4. Firebase authenticates
5. On success, navigate to Home Screen
6. On failure, show error message

## Color Choices

### Brand Colors
- **Primary**: `#0a7ea4` (Teal/Blue) - Main accent, buttons, highlights
- **Secondary**: `#6366f1` (Indigo) - Alternative accent for UI elements
- **Success**: `#22c55e` (Green) - Positive actions, confirmations
- **Warning**: `#f59e0b` (Amber) - Alerts, cautions
- **Error**: `#ef4444` (Red) - Errors, destructive actions

### Neutral Colors
- **Background**: `#ffffff` (Light) / `#151718` (Dark)
- **Surface**: `#f5f5f5` (Light) / `#1e2022` (Dark)
- **Foreground**: `#11181c` (Light) / `#ecedee` (Dark)
- **Muted**: `#687076` (Light) / `#9ba1a6` (Dark)
- **Border**: `#e5e7eb` (Light) / `#334155` (Dark)

### Message Colors
- **Sender Bubble**: Primary teal (`#0a7ea4`)
- **Receiver Bubble**: Surface gray (`#f5f5f5` light / `#1e2022` dark)
- **Encoded Indicator**: Secondary indigo (`#6366f1`)

## Typography

- **Heading 1**: 32px, Bold, Primary color
- **Heading 2**: 24px, Semibold, Foreground color
- **Heading 3**: 20px, Semibold, Foreground color
- **Body**: 16px, Regular, Foreground color
- **Caption**: 12px, Regular, Muted color
- **Button**: 16px, Semibold, White text on primary background

## Layout Principles

- **Safe Area**: All content respects safe area (notches, home indicators)
- **One-Handed Usage**: Primary actions within thumb reach (bottom half of screen)
- **Spacing**: 8px, 12px, 16px, 24px, 32px grid
- **Corner Radius**: 8px (small), 12px (medium), 16px (large)
- **Shadow**: Subtle elevation for cards and modals
- **Responsive**: Portrait orientation (9:16 aspect ratio)

## Interaction Patterns

- **Buttons**: Tap feedback with 0.97 scale + haptic
- **Lists**: Swipe to delete, pull-to-refresh
- **Input Fields**: Clear button on focus, keyboard handling
- **Modals**: Slide up from bottom, swipe down to dismiss
- **Navigation**: Bottom tab bar for main sections, stack navigation for details

## Data Models

### User
```typescript
interface User {
  id: string;
  email: string;
  displayName: string;
  avatar?: string;
  createdAt: Date;
}
```

### Message
```typescript
interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  receiverId: string;
  latentVector: number[]; // 512D encoded vector
  messageType: 'text' | 'image';
  originalSize: number; // bytes
  encodedSize: number; // bytes
  timestamp: Date;
  isDecoded: boolean;
  decodedContent?: string | Uint8Array;
}
```

### Conversation
```typescript
interface Conversation {
  id: string;
  participants: string[]; // [userId1, userId2]
  lastMessage?: Message;
  lastMessageTime?: Date;
  createdAt: Date;
}
```

## Firebase Integration

- **Authentication**: Firebase Auth (email/password)
- **Database**: Firestore for conversations and messages
- **Storage**: Firebase Storage for user avatars
- **Realtime**: Firestore listeners for live message updates

## Performance Considerations

- **Local Encoding**: All encoding/decoding happens on device (no server processing)
- **Bandwidth Savings**: 99% reduction (2MB image → 4KB vector)
- **Offline Support**: Queue messages locally, sync on reconnect
- **Caching**: Cache decoded messages locally
- **Lazy Loading**: Load conversation history on demand

## Accessibility

- **Text Contrast**: WCAG AA compliant
- **Touch Targets**: Minimum 44x44 pt
- **Labels**: All interactive elements have labels
- **Dark Mode**: Full support for light and dark themes
