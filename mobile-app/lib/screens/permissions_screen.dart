import 'package:flutter/material.dart';
import '../services/preferences_service.dart';
import 'auth/unified_login_screen.dart';

class PermissionsScreen extends StatefulWidget {
  const PermissionsScreen({super.key});

  @override
  State<PermissionsScreen> createState() => _PermissionsScreenState();
}

class _PermissionsScreenState extends State<PermissionsScreen> {
  final PreferencesService _prefs = PreferencesService();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: SafeArea(
        child: Column(
          children: [
            // Top Bar
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back, color: Colors.white70),
                    onPressed: () {
                      if (Navigator.of(context).canPop()) {
                        Navigator.of(context).pop();
                      } else {
                        Navigator.of(context).pushReplacement(
                          MaterialPageRoute(
                            builder: (_) => const UnifiedLoginScreen(),
                          ),
                        );
                      }
                    },
                  ),
                  const SizedBox(width: 8),
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'STEP 2 OF 2',
                        style: TextStyle(
                          color: Color(0xFF38BDF8),
                          fontSize: 11,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2,
                        ),
                      ),
                      Text(
                        'Device Permissions Access',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1E293B),
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: const Color(0xFF334155)),
                      ),
                      child: const Row(
                        children: [
                          Icon(
                            Icons.shield_outlined,
                            color: Color(0xFF10B981),
                            size: 24,
                          ),
                          SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              'Sanjeevani requires system permissions strictly to coordinate emergency response and dispatch in real-time.',
                              style: TextStyle(
                                color: Color(0xFFCBD5E1),
                                fontSize: 12,
                                height: 1.3,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 20),

                    const Text(
                      'REQUIRED EMERGENCY PERMISSIONS',
                      style: TextStyle(
                        color: Color(0xFF94A3B8),
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 12),

                    // 1. Location Access
                    _PermissionCard(
                      icon: Icons.location_on,
                      iconColor: const Color(0xFFEF4444),
                      title: 'Live Location & GPS Access',
                      subtitle:
                          'Enables automatic hospital matching, live ambulance dispatch tracking, and helper proximity radar.',
                      isGranted: _prefs.isLocationGranted,
                      onToggle: (val) {
                        setState(() {
                          _prefs.setLocationPermission(val);
                        });
                      },
                    ),
                    const SizedBox(height: 12),

                    // 2. Microphone Access
                    _PermissionCard(
                      icon: Icons.mic,
                      iconColor: const Color(0xFF0EA5E9),
                      title: 'Microphone & Voice Input',
                      subtitle:
                          'Allows voice notes, clear VoIP doctor consultations, and hands-free medical coordination.',
                      isGranted: _prefs.isMicrophoneGranted,
                      onToggle: (val) {
                        setState(() {
                          _prefs.setMicrophonePermission(val);
                        });
                      },
                    ),
                    const SizedBox(height: 12),

                    // 3. Speaker & Call Access
                    _PermissionCard(
                      icon: Icons.volume_up,
                      iconColor: const Color(0xFFF59E0B),
                      title: 'Speaker & Emergency Calling',
                      subtitle:
                          'Required for high-decibel siren alarm playback and direct VoIP calling between ER, drivers, and helpers.',
                      isGranted: _prefs.isSpeakerGranted,
                      onToggle: (val) {
                        setState(() {
                          _prefs.setSpeakerPermission(val);
                        });
                      },
                    ),
                    const SizedBox(height: 12),

                    // 4. Notifications Access
                    _PermissionCard(
                      icon: Icons.notifications_active,
                      iconColor: const Color(0xFF8B5CF6),
                      title: 'High-Priority Alert Notifications',
                      subtitle:
                          'Delivers critical dispatch alarms and inbound patient updates even when the device screen is locked.',
                      isGranted: _prefs.isNotificationGranted,
                      onToggle: (val) {
                        setState(() {
                          _prefs.setNotificationPermission(val);
                        });
                      },
                    ),
                    const SizedBox(height: 20),
                  ],
                ),
              ),
            ),

            // Bottom Action Area
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  ElevatedButton(
                    onPressed: () {
                      _prefs.grantAllPermissions();
                      _prefs.completeOnboarding();
                      Navigator.of(context).pushAndRemoveUntil(
                        MaterialPageRoute(
                          builder: (_) => const UnifiedLoginScreen(),
                        ),
                        (route) => false,
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF10B981),
                      foregroundColor: Colors.white,
                      minimumSize: const Size(double.infinity, 52),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14),
                      ),
                      elevation: 4,
                    ),
                    child: const Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.check_circle_outline, size: 20),
                        SizedBox(width: 8),
                        Text(
                          'Grant All & Launch Sanjeevani',
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PermissionCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  final bool isGranted;
  final ValueChanged<bool> onToggle;

  const _PermissionCard({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    required this.isGranted,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: isGranted ? const Color(0xFF10B981).withValues(alpha: 0.4) : const Color(0xFF334155),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: iconColor, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 11,
                    height: 1.3,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Switch(
            value: isGranted,
            onChanged: onToggle,
            activeTrackColor: const Color(0xFF10B981),
          ),
        ],
      ),
    );
  }
}
