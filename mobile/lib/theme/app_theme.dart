/// App Theme - "Simple & Experienced" Design System
/// Focuses on minimalism, deep contrast, and elegant typography

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // Brand Colors - Refined Palette
  static const Color primaryColor = Color(0xFF7C4DFF); // Deep Electric Purple
  static const Color secondaryColor = Color(0xFF00E676); // Vivid Green for Zero-Rating
  
  // Background Colors - Absolute Void
  static const Color backgroundBlack = Color(0xFF000000); // True Black
  static const Color surfaceDark = Color(0xFF0A0A0A); // Almost Black
  static const Color surfaceElevated = Color(0xFF141414); // Slightly Lighter
  
  // Text Colors
  static const Color textHighEmphasis = Color(0xFFFFFFFF);
  static const Color textMediumEmphasis = Color(0xFFA0A0A0);
  static const Color textLowEmphasis = Color(0xFF606060);
  
  // Design Tokens
  static const double borderRadiusL = 24.0;
  static const double borderRadiusM = 16.0;
  static const double borderRadiusS = 12.0;

  // Modern Dark Theme
  static ThemeData get premiumTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      primaryColor: primaryColor,
      scaffoldBackgroundColor: backgroundBlack,
      
      // Color Scheme
      colorScheme: const ColorScheme.dark(
        primary: primaryColor,
        secondary: secondaryColor,
        background: backgroundBlack,
        surface: surfaceDark,
        onBackground: textHighEmphasis,
        onSurface: textHighEmphasis,
        outline: textLowEmphasis,
      ),
      
      // Typography - Inter for clean, experienced technical feel
      textTheme: GoogleFonts.interTextTheme(
        const TextTheme(
          displayLarge: TextStyle(fontSize: 40, fontWeight: FontWeight.w300, color: textHighEmphasis, letterSpacing: -1.0),
          displayMedium: TextStyle(fontSize: 32, fontWeight: FontWeight.w400, color: textHighEmphasis, letterSpacing: -0.5),
          headlineLarge: TextStyle(fontSize: 24, fontWeight: FontWeight.w600, color: textHighEmphasis),
          headlineMedium: TextStyle(fontSize: 20, fontWeight: FontWeight.w600, color: textHighEmphasis),
          titleLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.w500, color: textHighEmphasis),
          bodyLarge: TextStyle(fontSize: 16, fontWeight: FontWeight.w400, color: textHighEmphasis, height: 1.5),
          bodyMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w400, color: textMediumEmphasis, height: 1.5),
          labelLarge: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: textHighEmphasis),
          labelMedium: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: textLowEmphasis),
        ),
      ),
      
      // App Bar
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        scrolledUnderElevation: 0,
        iconTheme: IconThemeData(color: textHighEmphasis),
        titleTextStyle: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: textHighEmphasis),
      ),
      
      // Buttons
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: Colors.white,
          elevation: 0,
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(borderRadiusL),
          ),
          textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
      ),
      
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: textMediumEmphasis,
          textStyle: const TextStyle(fontWeight: FontWeight.w500),
        ),
      ),
      
      // Inputs
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: surfaceElevated,
        contentPadding: const EdgeInsets.all(20),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(borderRadiusM),
          borderSide: BorderSide.none,
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(borderRadiusM),
          borderSide: const BorderSide(color: primaryColor, width: 1.5),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(borderRadiusM),
          borderSide: const BorderSide(color: Colors.redAccent, width: 1.5),
        ),
        hintStyle: const TextStyle(color: textLowEmphasis),
        prefixIconColor: textMediumEmphasis,
      ),
      
      // Bottom Sheet
      bottomSheetTheme: const BottomSheetThemeData(
        backgroundColor: surfaceDark,
        modalBackgroundColor: surfaceDark,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
        ),
      ),
      
      // Divider
      dividerTheme: const DividerThemeData(
        color: surfaceElevated,
        thickness: 1,
      ),
    );
  }
}
