import 'dart:async';
import 'package:flutter/material.dart';
import '../services/preferences_service.dart';
import 'auth/unified_login_screen.dart';
import 'doctor/doctor_dashboard_screen.dart';
import 'driver/driver_dashboard_screen.dart';
import 'helper/helper_dashboard_screen.dart';
import 'onboarding_instructions_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _fadeAnimation;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );

    _fadeAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeIn),
    );

    _scaleAnimation = Tween<double>(begin: 0.85, end: 1.0).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeOutCubic),
    );

    _animController.forward();

    Timer(const Duration(milliseconds: 2400), () {
      if (mounted) {
        final prefs = PreferencesService();

        // 1. If already logged in, navigate straight to their role dashboard
        if (prefs.isLoggedIn) {
          Widget dashboard;
          switch (prefs.loggedInRole) {
            case 'doctor':
              dashboard = DoctorDashboardScreen(
                doctorName: prefs.loggedInUserName.isNotEmpty
                    ? prefs.loggedInUserName
                    : 'Dr. Rajesh Sharma, MD',
              );
              break;
            case 'driver':
              dashboard = DriverDashboardScreen(
                driverName: prefs.loggedInUserName.isNotEmpty
                    ? prefs.loggedInUserName
                    : 'Suresh Kumar',
              );
              break;
            case 'helper':
            default:
              dashboard = HelperDashboardScreen(
                helperName: prefs.loggedInUserName.isNotEmpty
                    ? prefs.loggedInUserName
                    : 'Anjali Devi (ASHA Worker)',
              );
              break;
          }

          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => dashboard),
          );
          return;
        }

        // 2. If not logged in, check onboarding status
        if (prefs.isOnboardingCompleted) {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const UnifiedLoginScreen()),
          );
        } else {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(
              builder: (_) => const OnboardingInstructionsScreen(),
            ),
          );
        }
      }
    });
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      body: Stack(
        children: [
          // Subtle background glow
          Center(
            child: Container(
              width: 320,
              height: 320,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: const Color(0xFF0284C7).withValues(alpha: 0.08),
              ),
            ),
          ),
          Center(
            child: FadeTransition(
              opacity: _fadeAnimation,
              child: ScaleTransition(
                scale: _scaleAnimation,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 28),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // Medical Emblem Icon
                      Container(
                        width: 96,
                        height: 96,
                        decoration: BoxDecoration(
                          color: const Color(0xFFDC2626),
                          borderRadius: BorderRadius.circular(28),
                          boxShadow: [
                            BoxShadow(
                              color:
                                  const Color(0xFFDC2626).withValues(alpha: 0.4),
                              blurRadius: 24,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.local_hospital,
                          color: Colors.white,
                          size: 52,
                        ),
                      ),
                      const SizedBox(height: 28),

                      // Title
                      const Text(
                        'SANJEEVANI',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 32,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 2.5,
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Tagline — clean, professional, no quotes
                      const Text(
                        'The right help.\nAt the right place. At the right time.',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 14,
                          fontWeight: FontWeight.w500,
                          height: 1.5,
                          letterSpacing: 0.2,
                        ),
                      ),
                      const SizedBox(height: 24),

                      const Text(
                        'Emergency Medical Response System',
                        textAlign: TextAlign.center,
                        style: TextStyle(
                          color: Color(0xFF64748B),
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Bottom Loading Indicator
          Positioned(
            bottom: 40,
            left: 0,
            right: 0,
            child: Center(
              child: Column(
                children: [
                  SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2.5,
                      color: const Color(0xFF38BDF8).withValues(alpha: 0.8),
                    ),
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    'Loading...',
                    style: TextStyle(
                      color: Color(0xFF64748B),
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
