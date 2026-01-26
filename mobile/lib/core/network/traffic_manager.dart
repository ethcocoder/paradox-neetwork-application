/// Traffic Manager - Dual-Lane Routing 
/// Enforces strict separation between zero-rated and normal internet traffic
/// Based on internet.md specification

import 'package:dio/dio.dart';
import '../../config/app_config.dart';

enum TrafficLane { zeroRated, normal }

class TrafficManager {
  late final Dio _zeroRatedClient; // Lane A - FREE
  late final Dio _normalClient;    // Lane B - Uses data
  
  TrafficManager() {
    _initializeClients();
  }
  
  void _initializeClients() {
    // Lane A Client (Zero-Rated Domain)
    _zeroRatedClient = Dio(BaseOptions(
      baseUrl: AppConfig.zeroRatedDomain,
      connectTimeout: AppConfig.connectionTimeout,
      receiveTimeout: AppConfig.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'X-Traffic-Lane': 'zero-rated',
        'X-Telecom-Partner': AppConfig.telecomPartner,
      },
    ));
    
    // Lane B Client (Normal Internet)
    _normalClient = Dio(BaseOptions(
      baseUrl: AppConfig.normalDomain,
      connectTimeout: AppConfig.connectionTimeout,
      receiveTimeout: AppConfig.receiveTimeout,
      headers: {
        'Content-Type': 'application/json',
        'X-Traffic-Lane': 'normal',
      },
    ));
    
    // Add interceptors for logging and error handling
    _zeroRatedClient.interceptors.add(_createInterceptor(TrafficLane.zeroRated));
    _normalClient.interceptors.add(_createInterceptor(TrafficLane.normal));
  }
  
  InterceptorsWrapper _createInterceptor(TrafficLane lane) {
    return InterceptorsWrapper(
      onRequest: (options, handler) {
        print('📡 [${lane.name.toUpperCase()}] ${options.method} ${options.path}');
        return handler.next(options);
      },
      onResponse: (response, handler) {
        print('✅ [${lane.name.toUpperCase()}] ${response.statusCode} ${response.requestOptions.path}');
        return handler.next(response);
      },
      onError: (error, handler) {
        print('❌ [${lane.name.toUpperCase()}] ${error.response?.statusCode} ${error.requestOptions.path}');
        return handler.next(error);
      },
    );
  }
  
  /// Get appropriate client for operation
  Dio getClient(String operation) {
    if (AppConfig.isZeroRated(operation)) {
      return _zeroRatedClient;
    } else {
      return _normalClient;
    }
  }
  
  /// Send request with automatic lane routing
  Future<Response> request(
    String operation,
    String path, {
    String method = 'GET',
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
  }) async {
    final client = getClient(operation);
    
    try {
      switch (method.toUpperCase()) {
        case 'GET':
          return await client.get(path, queryParameters: queryParameters, options: options);
        case 'POST':
          return await client.post(path, data: data, queryParameters: queryParameters, options: options);
        case 'PUT':
          return await client.put(path, data: data, queryParameters: queryParameters, options: options);
        case 'DELETE':
          return await client.delete(path, data: data, queryParameters: queryParameters, options: options);
        default:
          throw Exception('Unsupported HTTP method: $method');
      }
    } catch (e) {
      // If Lane B (normal internet) fails, degrade gracefully
      if (!AppConfig.isZeroRated(operation)) {
        print('⚠️  Lane B request failed (no data?): $e');
        // Don't crash app, just return error
      }
      rethrow;
    }
  }
  
  /// Add authorization token to requests
  void setAuthToken(String token) {
    final authHeader = {'Authorization': 'Bearer $token'};
    _zeroRatedClient.options.headers.addAll(authHeader);
    _normalClient.options.headers.addAll(authHeader);
  }
  
  /// Remove authorization token
  void clearAuthToken() {
    _zeroRatedClient.options.headers.remove('Authorization');
    _normalClient.options.headers.remove('Authorization');
  }
  
  /// Get traffic statistics
  Map<String, dynamic> getTrafficStats() {
    return {
      'lane_a_active': true,
      'lane_b_active': true,
      'zero_rated_domain': AppConfig.zeroRatedDomain,
      'normal_domain': AppConfig.normalDomain,
    };
  }
}
