import 'package:flutter/material.dart';
import '../models/emergency_case.dart';
import '../widgets/emergency_alarm_dialog.dart';
import '../screens/call/active_call_screen.dart';

class NotificationService {
  static void showInAppAlert(
    BuildContext context, {
    required String title,
    required String message,
    IconData icon = Icons.notifications_active,
    Color backgroundColor = const Color(0xFF1E293B),
    VoidCallback? onTap,
  }) {
    ScaffoldMessenger.of(context).hideCurrentSnackBar();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        duration: const Duration(seconds: 4),
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        backgroundColor: backgroundColor,
        content: InkWell(
          onTap: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
            onTap?.call();
          },
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: Colors.white, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      title,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      message,
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              if (onTap != null)
                const Icon(Icons.arrow_forward_ios, color: Colors.white70, size: 14),
            ],
          ),
        ),
      ),
    );
  }

  static void triggerEmergencySirenAlarm(
    BuildContext context, {
    required EmergencyCase emergencyCase,
    required VoidCallback onAccept,
  }) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => EmergencyAlarmDialog(
        emergencyCase: emergencyCase,
        onAccept: () {
          Navigator.of(ctx).pop();
          onAccept();
        },
        onDismiss: () {
          Navigator.of(ctx).pop();
        },
      ),
    );
  }

  static void startDirectCall(
    BuildContext context, {
    required String contactName,
    required String contactRole,
    required String associatedCaseId,
    String? phoneNumber,
  }) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (ctx) => ActiveCallScreen(
          contactName: contactName,
          contactRole: contactRole,
          associatedCaseId: associatedCaseId,
          phoneNumber: phoneNumber ?? '+91 108-EMG-LINE',
        ),
      ),
    );
  }
}
