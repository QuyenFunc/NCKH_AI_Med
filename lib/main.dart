import 'package:flutter/material.dart';
import 'screens/main_screen.dart';

void main() {
  runApp(const Dia5App());
}

class Dia5App extends StatelessWidget {
  const Dia5App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Dia5 - AI Medical Diagnosis',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        // Medical theme with blue color scheme
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1976D2), // Medical blue
          brightness: Brightness.light,
        ),
        primaryColor: const Color(0xFF1976D2),
        useMaterial3: true,
        
        // AppBar theme
        appBarTheme: const AppBarTheme(
          elevation: 0,
          backgroundColor: Colors.white,
          foregroundColor: Colors.black87,
          titleTextStyle: TextStyle(
            fontSize: 18.0,
            fontWeight: FontWeight.w600,
            color: Colors.black87,
          ),
        ),
        
        // Text theme
        textTheme: const TextTheme(
          bodyLarge: TextStyle(
            fontSize: 16.0,
            height: 1.4,
            color: Colors.black87,
          ),
          bodyMedium: TextStyle(
            fontSize: 14.0,
            height: 1.4,
            color: Colors.black87,
          ),
        ),
        
        // Icon theme
        iconTheme: const IconThemeData(
          color: Color(0xFF1976D2),
        ),
        
        // Input decoration theme
        inputDecorationTheme: InputDecorationTheme(
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24.0),
            borderSide: BorderSide(color: Colors.grey.shade300),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24.0),
            borderSide: BorderSide(color: Colors.grey.shade300),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(24.0),
            borderSide: const BorderSide(color: Color(0xFF1976D2)),
          ),
          filled: true,
          fillColor: Colors.grey.shade50,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: 20.0,
            vertical: 12.0,
          ),
        ),
      ),
      home: const MainScreen(),
    );
  }
}
