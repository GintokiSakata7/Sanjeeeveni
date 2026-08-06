import 'package:flutter/material.dart';

class AppToast {
  /// Displays a sleek, Instagram-style floating capsule/pill toast.
  static void show(
    BuildContext context, {
    String message = 'Press back again to exit',
    Duration duration = const Duration(milliseconds: 2000),
  }) {
    final messenger = ScaffoldMessenger.of(context);
    messenger.clearSnackBars();
    messenger.showSnackBar(
      SnackBar(
        content: Text(
          message,
          textAlign: TextAlign.center,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 13,
            fontWeight: FontWeight.w500,
            letterSpacing: 0.1,
          ),
        ),
        duration: duration,
        backgroundColor: const Color(0xE6262626), // Instagram dark pill tone
        behavior: SnackBarBehavior.floating,
        elevation: 4,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(24),
          side: const BorderSide(
            color: Color(0x33FFFFFF),
            width: 0.8,
          ),
        ),
        margin: const EdgeInsets.only(bottom: 38, left: 60, right: 60),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      ),
    );
  }
}
