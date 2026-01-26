/// Authentication Service

import 'package:flutter_secure_storage.dart';
import '../core/network/traffic_manager.dart';
import '../models/user_model.dart';

class AuthService {
  final TrafficManager _trafficManager;
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();
  
  User? _currentUser;
  String? _authToken;
  
  AuthService(this._trafficManager);
  
  User? get currentUser => _currentUser;
  bool get isAuthenticated => _authToken != null && _currentUser != null;
  
  /// Register new user
  Future<User> register({
    required String phoneNumber,
    required String password,
    String? username,
  }) async {
    final response = await _trafficManager.request(
      'auth_register',
      '/auth/register',
      method: 'POST',
      data: {
        'phone_number': phoneNumber,
        'password': password,
        'username': username,
      },
    );
    
    final data = response.data;
    _authToken = data['access_token'];
    _currentUser = User.fromJson(data);
    
    // Save token securely
    await _saveAuthToken(_authToken!);
    await _saveUser(_currentUser!);
    
    // Set token in traffic manager
    _trafficManager.setAuthToken(_authToken!);
    
    return _currentUser!;
  }
  
  /// Login existing user
  Future<User> login({
    required String phoneNumber,
    required String password,
  }) async {
    final response = await _trafficManager.request(
      'auth_login',
      '/auth/login',
      method: 'POST',
      data: {
        'phone_number': phoneNumber,
        'password': password,
      },
    );
    
    final data = response.data;
    _authToken = data['access_token'];
    _currentUser = User.fromJson(data);
    
    // Save token securely
    await _saveAuthToken(_authToken!);
    await _saveUser(_currentUser!);
    
    // Set token in traffic manager
    _trafficManager.setAuthToken(_authToken!);
    
    return _currentUser!;
  }
  
  /// Logout user
  Future<void> logout() async {
    _currentUser = null;
    _authToken = null;
    
    await _secureStorage.delete(key: 'auth_token');
    await _secureStorage.delete(key: 'user_data');
    
    _trafficManager.clearAuthToken();
  }
  
  /// Try to restore session from storage
  Future<bool> tryRestoreSession() async {
    try {
      final token = await _secureStorage.read(key: 'auth_token');
      final userData = await _secureStorage.read(key: 'user_data');
      
      if (token != null && userData != null) {
        _authToken = token;
        _currentUser = User.fromJson(
          Map<String, dynamic>.from(
            // Would need to parse JSON here
            {} // Simplified for now
          ),
        );
        
        _trafficManager.setAuthToken(token);
        return true;
      }
    } catch (e) {
      print('Failed to restore session: $e');
    }
    
    return false;
  }
  
  Future<void> _saveAuthToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
  }
  
  Future<void> _saveUser(User user) async {
    // Would serialize user to JSON here
    await _secureStorage.write(key: 'user_data', value: user.userId);
  }
}
