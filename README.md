# Paradox Network Application

![Paradox Network](https://img.shields.io/badge/Paradox-Network-blueviolet?style=for-the-badge)
![Expo](https://img.shields.io/badge/Expo-54-000000?style=for-the-badge&logo=expo&logoColor=white)
![React Native](https://img.shields.io/badge/React_Native-0.81-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Firebase](https://img.commerce.io/badge/Firebase-Auth%20%2F%20Firestore-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)

A high-performance, multi-modal messaging application built with Expo and React Native, featuring advanced AI-driven compression and multi-modal CLIP integration.

## 🚀 Key Features

- **Multi-Modal Messaging**: Send text, images, and video with unified AI encoding.
- **AI Compression**: Utilizes CLIP (Contrastive Language-Image Pre-training) models to compress media into 512-float vectors, achieving up to 500x compression for video.
- **Firebase Integration**: Secure authentication and real-time data storage using Firebase Auth and Firestore.
- **Edge AI**: Runs TFLite (TensorFlow Lite) models directly on the device for lightning-fast encoding and decoding.
- **Video Keyframe Strategy**: Innovative video compression that extracts keyframes (1 fps) to minimize bandwidth while maintaining visual quality.

## 🛠 Tech Stack

- **Framework**: [Expo](https://expo.dev/) (SDK 54)
- **UI**: [React Native](https://reactnative.dev/), [NativeWind](https://www.nativewind.dev/) (Tailwind CSS for React Native)
- **State Management**: [React Query](https://tanstack.com/query/latest)
- **Backend**: [Firebase](https://firebase.google.com/) (Auth, Firestore)
- **AI/ML**: [TensorFlow Lite](https://www.tensorflow.org/lite), [react-native-fast-tflite](https://github.com/mrousavy/react-native-fast-tflite)
- **Database (Local)**: [Drizzle ORM](https://orm.drizzle.team/)

## 📂 Project Structure

- `/app`: Expo Router screens and layouts.
- `/components`: Reusable UI components.
- `/lib`: Core logic, including AI model services, Firebase configuration, and performance monitoring.
- `/assets/models`: TFLite models for text and image processing.
- `/scripts`: Utility scripts for environment setup and model management.

## 🚦 Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) (v18+)
- [pnpm](https://pnpm.io/)
- [Expo Go](https://expo.dev/client) or a physical device for testing.

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ethcocoder/paradox-neetwork-application.git
   cd paradox-network-app
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add your Firebase and API configuration.

4. Start the development server:
   ```bash
   pnpm dev
   ```

## 🧠 AI Architecture

The application uses a dual-encoder/decoder strategy:

| Data Type | Encoder Model | Size | Decoder Model | Size |
|-----------|---------------|------|---------------|------|
| **Text**  | CLIP Text Encoder | 102 MB | CLIP Text Decoder | 1.2 MB |
| **Image** | CLIP Image Encoder | 567 KB | CLIP Image Decoder | 2.1 MB |
| **Video** | CLIP Image Encoder | - | CLIP Image Decoder | - |

For more details on the AI implementation, see the [Multi-Modal Guide](./MULTI_MODAL_GUIDE.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

**Developed by Ethco Coder**
