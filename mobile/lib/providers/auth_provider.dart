/// Auth Provider - State Management

import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/auth_service.dart';

class AuthProvider with ChangeNotifier {
  final AuthService _authService;
  
  User? _currentUser;
  bool _isLoading = false;
  String? _error;
  
  AuthProvider(this._authService);
  
  User? get currentUser => _currentUser;
  User? get user => _currentUser;
  bool get isAuthenticated => _currentUser != null;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  /// Login
  Future<void> login({
    required String phoneNumber,
    required String password,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      _currentUser = await _authService.login(
        phoneNumber: phoneNumber,
        password: password,
      );
      _error = null;
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Register
  Future<void> register({
    required String phoneNumber,
    required String password,
    String? username,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      _currentUser = await _authService.register(
        phoneNumber: phoneNumber,
        password: password,
        username: username,
      );
      _error = null;
    } catch (e) {
      _error = e.toString();
      rethrow;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
  
  /// Logout
  Future<void> logout() async {
    await _authService.logout();
    _currentUser = null;
    notifyListeners();
  }
  
  /// Try restore session
  Future<void> tryRestoreSession() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      final restored = await _authService.tryRestoreSession();
      if (restored) {
        _currentUser = _authService.currentUser;
      }
    } catch (e) {
      print('Failed to restore session: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
