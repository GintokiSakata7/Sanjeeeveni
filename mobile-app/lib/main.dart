import 'package:flutter/material.dart';
import 'screens/citizen_sos_screen.dart';

void main() {
  runApp(const AeroApp());
}

class AeroApp extends StatelessWidget {
  const AeroApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AERO Emergency',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFFDC2626),
          brightness: Brightness.light,
        ),
        fontFamily: 'Roboto',
        useMaterial3: true,
        scaffoldBackgroundColor: const Color(0xFFF1F5F9),
      ),
      home: const CitizenSosScreen(),
    );
  }
}
