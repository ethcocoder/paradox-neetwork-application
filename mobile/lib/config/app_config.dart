/// App Configuration - Dual-Lane Architecture
/// Separates zero-rated (Lane A) from normal internet (Lane B) traffic

class AppConfig {
  // Dual-Lane Domain Configuration
  static const String zeroRatedDomain = 'http://localhost:8000'; // Will change to: https://core.pna.et
  static const String normalDomain = 'http://localhost:8000'; // Will change to: https://api.pna.et
  
  // Environment
  static const String environment = 'development'; // development, staging, production
  
  // API Versioning
  static const String apiVersion = 'v1';
  
  // Traffic Lanes
  static const String laneA = 'zero_rated'; // FREE for receivers
  static const String laneB = 'normal';     // Uses user's data
  
  // Telecom Partner
  static const String telecomPartner = 'ethio_telecom';
  
  // Offline Configuration
  static const int maxOfflineQueueSize = 1000;
  static const int offlineSyncIntervalSeconds = 30;
  
  // Message Configuration
  static const int maxMessageLength = 5000;
  static const int vectorDimension = 512;
  
  // Network Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
  
  // Get base URL for specific operation
  static String getBaseUrl(String operation) {
    // Lane A operations (zero-rated)
    const laneAOperations = [
      'message_send',
      'message_receive',
      'message_history',
      'subscription_validate',
      'auth_login',
      'auth_register',
    ];
    
    if (laneAOperations.contains(operation)) {
      return zeroRatedDomain;
    } else {
      return normalDomain;
    }
  }
  
  // Build API endpoint URL
  static String buildUrl(String operation, String path) {
    final baseUrl = getBaseUrl(operation);
    return '$baseUrl/$apiVersion$path';
  }
  
  // Check if operation is zero-rated
  static bool isZeroRated(String operation) {
    return getBaseUrl(operation) == zeroRatedDomain;
  }
}
