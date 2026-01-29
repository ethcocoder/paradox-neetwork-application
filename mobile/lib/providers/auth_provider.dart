/// Auth Provider - State Management

import 'package:flutter/foundation.dart';
import '../models/user_model.dart';
import '../services/firebase_service.dart';
import 'package:firebase_auth/firebase_auth.dart' as fb_auth;

class AuthProvider with ChangeNotifier {
  final FirebaseService _firebaseService;
  
  User? _currentUser;
  bool _isLoading = false;
  String? _error;
  
  AuthProvider(this._firebaseService);
  
  User? get currentUser => _currentUser;
  User? get user => _currentUser;
  bool get isAuthenticated => _currentUser != null;
  bool get isLoading => _isLoading;
  String? get error => _error;
  
  /// Login
  Future<void> login({
    required String email,
    required String password,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final credential = await _firebaseService.login(email, password);
      if (credential.user != null) {
        _currentUser = await _firebaseService.getUserProfile(credential.user!.uid);
      }
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
    required String email,
    required String password,
    String? username,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    
    try {
      final credential = await _firebaseService.register(email, password, username: username);
      if (credential.user != null) {
        _currentUser = await _firebaseService.getUserProfile(credential.user!.uid);
      }
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
    await _firebaseService.logout();
    _currentUser = null;
    notifyListeners();
  }
  
  /// Try restore session
  Future<void> tryRestoreSession() async {
    _isLoading = true;
    notifyListeners();
    
    try {
      // Firebase handles persistence automatically
      final fb_auth.User? fbUser = fb_auth.FirebaseAuth.instance.currentUser;
      if (fbUser != null) {
        _currentUser = await _firebaseService.getUserProfile(fbUser.uid);
      }
    } catch (e) {
      print('Failed to restore session: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
