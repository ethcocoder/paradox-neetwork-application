/// Login Screen - Redesigned for "Simple & Experienced" Feel
/// Minimalist architecture, focus on content and typography

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:paradox_network_app/theme/app_theme.dart';
import 'package:paradox_network_app/providers/auth_provider.dart';
import 'dart:ui'; // For blur effect

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  void _handleLogin() async {
    if (_phoneController.text.isEmpty || _passwordController.text.isEmpty) return;
    
    setState(() => _isLoading = true);
    
    // Simulate slight delay for "experienced" feel
    await Future.delayed(const Duration(milliseconds: 300));
    
    try {
      final authProvider = context.read<AuthProvider>();
      await authProvider.login(
        phoneNumber: _phoneController.text.trim(),
        password: _passwordController.text,
      );
      
      if (mounted) Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(e.toString()),
            backgroundColor: Colors.redAccent,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black, // True black background
      body: Stack(
        children: [
          // Background Gradient Mesh (Subtle)
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AppTheme.primaryColor.withOpacity(0.15),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryColor.withOpacity(0.15),
                    blurRadius: 100,
                    spreadRadius: 50,
                  ),
                ],
              ),
            ),
          ),
          
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Spacer(flex: 2),
                  
                  // Minimalist Logo Area
                  Center(
                    child: Container(
                      width: 80,
                      height: 80,
                      decoration: BoxDecoration(
                        color: AppTheme.surfaceElevated,
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: AppTheme.primaryColor.withOpacity(0.2)),
                        boxShadow: [
                            BoxShadow(
                                color: AppTheme.primaryColor.withOpacity(0.1),
                                blurRadius: 20,
                                offset: const Offset(0, 10),
                            ),
                        ],
                      ),
                      // Using Icon for now, assuming asset image will be loaded in real run
                      child: const Icon(Icons.webhook, color: AppTheme.primaryColor, size: 40), 
                    ),
                  ),
                  
                  const SizedBox(height: 40),
                  
                  // Headlines
                  Text(
                    'Welcome back',
                    style: Theme.of(context).textTheme.headlineLarge,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Enter your credentials to access the node.',
                    style: Theme.of(context).textTheme.bodyMedium,
                    textAlign: TextAlign.center,
                  ),
                  
                  const Spacer(flex: 1),
                  
                  // Input Fields
                  _MinimalInput(
                    controller: _phoneController,
                    hint: 'Phone Number',
                    icon: Icons.phone_outlined,
                  ),
                  
                  const SizedBox(height: 16),
                  
                  _MinimalInput(
                    controller: _passwordController,
                    hint: 'Password',
                    icon: Icons.lock_outline,
                    isPassword: true,
                  ),
                  
                  const SizedBox(height: 32),
                  
                  // Action Button
                  ElevatedButton(
                    onPressed: _isLoading ? null : _handleLogin,
                    child: _isLoading 
                      ? const SizedBox(width: 24, height: 24, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                      : const Text('Connect'),
                  ),
                  
                  const Spacer(flex: 3),
                  
                  // Footer
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text("New node? ", style: Theme.of(context).textTheme.bodyMedium),
                      GestureDetector(
                        onTap: () => Navigator.pushNamed(context, '/register'),
                        child: Text(
                          "Initialize",
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.primaryColor,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MinimalInput extends StatelessWidget {
  final TextEditingController controller;
  final String hint;
  final IconData icon;
  final bool isPassword;

  const _MinimalInput({
    required this.controller,
    required this.hint,
    required this.icon,
    this.isPassword = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppTheme.surfaceElevated,
        borderRadius: BorderRadius.circular(16),
      ),
      child: TextField(
        controller: controller,
        obscureText: isPassword,
        style: const TextStyle(color: Colors.white),
        decoration: InputDecoration(
          hintText: hint,
          prefixIcon: Icon(icon, size: 20),
          border: InputBorder.none,
          enabledBorder: InputBorder.none,
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: AppTheme.primaryColor, width: 1),
          ),
        ),
      ),
    );
  }
}
