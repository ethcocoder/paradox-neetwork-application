/// Updated Main App - Includes Local Encoder/Decoder

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/app_config.dart';
import 'theme/app_theme.dart';
import 'core/network/traffic_manager.dart';
import 'services/auth_service.dart';
import 'services/messaging_service.dart';
import 'services/offline_queue_service.dart';
import 'services/local_latent_encoder.dart';
import 'services/local_latent_decoder.dart';
import 'providers/auth_provider.dart';
import 'features/auth/screens/login_screen.dart';
import 'features/chat/screens/chat_list_screen.dart';
import 'features/subscription/screens/subscription_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  final trafficManager = TrafficManager();
  final authService = AuthService(trafficManager);
  
  // CRITICAL: Initialize local encoder/decoder
  // This ensures encoding happens ON DEVICE before sending
  final localEncoder = LocalLatentEncoder();
  final localDecoder = LocalLatentDecoder();
  await localEncoder.initialize();
  await localDecoder.initialize();
  
  final messagingService = MessagingService(trafficManager, localEncoder);
  final offlineQueueService = OfflineQueueService();
  
  print('🔐 Local encoding/decoding initialized');
  print('📊 Vector dimension: ${LocalLatentEncoder.vectorDimension}');
  print('✅ Raw data will NEVER leave device unencrypted');
  
  runApp(
    MultiProvider(
      providers: [
        Provider.value(value: trafficManager),
        Provider.value(value: localEncoder),
        Provider.value(value: localDecoder),
        Provider.value(value: messagingService),
        Provider.value(value: offlineQueueService),
        ChangeNotifierProvider(
          create: (_) => AuthProvider(authService),
        ),
      ],
      child: const ParadoxNetworkApp(),
    ),
  );
}

class ParadoxNetworkApp extends StatelessWidget {
  const ParadoxNetworkApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Paradox Network',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const SplashScreen(),
      routes: {
        '/login': (context) => const LoginScreen(),
        '/register': (context) => const LoginScreen(),
        '/home': (context) => const ChatListScreen(),
        '/subscription': (context) => const SubscriptionScreen(),
      },
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({Key? key}) : super(key: key);

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _initialize();
  }
  
  Future<void> _initialize() async {
    // Try to restore session
    final authProvider = context.read<AuthProvider>();
    await authProvider.tryRestoreSession();
    
    // Show splash for visual effect
    await Future.delayed(const Duration(seconds: 2));
    
    if (mounted) {
      if (authProvider.isAuthenticated) {
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        Navigator.pushReplacementNamed(context, '/login');
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppTheme.primaryGradient,
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Logo
              Container(
                height: 120,
                width: 120,
                decoration: BoxDecoration(
                  color: Colors.white,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.2),
                      blurRadius: 30,
                      offset: const Offset(0, 10),
                    ),
                  ],
                ),
                child: const Icon(
                  Icons.lock_outline,
                  size: 60,
                  color: AppTheme.primaryColor,
                ),
              ),
              
              const SizedBox(height: 24),
              
              Text(
                'Paradox Network',
                style: Theme.of(context).textTheme.displayMedium?.copyWith(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
              
              const SizedBox(height: 8),
              
              Text(
                'Local Encoding. Zero Trust.',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                  color: Colors.white.withOpacity(0.9),
                ),
              ),
              
              const SizedBox(height: 4),
              
              Text(
                '99% Less Data. 100% Private.',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: Colors.white.withOpacity(0.7),
                ),
              ),
              
              const SizedBox(height: 40),
              
              const CircularProgressIndicator(
                color: Colors.white,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
