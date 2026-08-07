import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:aero_mobile/screens/role_gateway_screen.dart';
import 'package:aero_mobile/screens/doctor/doctor_dashboard_screen.dart';
import 'package:aero_mobile/screens/driver/driver_dashboard_screen.dart';
import 'package:aero_mobile/screens/helper/helper_dashboard_screen.dart';
import 'package:aero_mobile/screens/auth/unified_login_screen.dart';
import 'package:aero_mobile/screens/auth/helper_register_screen.dart';
import 'package:aero_mobile/screens/permissions_screen.dart';
import 'package:aero_mobile/services/preferences_service.dart';
import 'package:aero_mobile/services/location_service.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('Sanjeevani Multi-Role Suite Tests', () {
    testWidgets('RoleGatewayScreen renders portals without SOS', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: RoleGatewayScreen()),
      );

      expect(find.text('SANJEEVANI'), findsOneWidget);
      expect(find.text('Staff & Responder Portal'), findsOneWidget);
      expect(find.text('Join as Community Helper'), findsOneWidget);
      expect(find.text('SYSTEM CAPABILITIES'), findsOneWidget);
      // Verify SOS is completely removed
      expect(find.text('Citizen SOS Emergency'), findsNothing);
    });

    testWidgets('UnifiedLoginScreen renders role tabs and login credentials', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: UnifiedLoginScreen()),
      );

      expect(find.text('Staff Portal Sign In'), findsOneWidget);
      expect(find.byIcon(Icons.arrow_back), findsNothing);
      expect(find.text('Doctor'), findsOneWidget);
      expect(find.text('Driver'), findsOneWidget);
      expect(find.text('Helper'), findsOneWidget);
      expect(find.text('REGISTERED MOBILE NUMBER'), findsOneWidget);
      expect(find.text('SECURITY PASSWORD'), findsOneWidget);
      expect(find.text('Register Here'), findsOneWidget);
    });

    testWidgets('DoctorDashboardScreen displays patient emergency and telemetry with logout', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: DoctorDashboardScreen()),
      );

      expect(find.byIcon(Icons.arrow_back), findsNothing);
      expect(find.byIcon(Icons.logout), findsOneWidget);
    });

    testWidgets('DriverDashboardScreen displays dispatch, milestones and Google Maps button', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: DriverDashboardScreen()),
      );

      expect(find.byIcon(Icons.arrow_back), findsNothing);
      expect(find.text('ACTIVE EMERGENCY DISPATCH'), findsOneWidget);
      expect(find.text('LIVE DISPATCH TRIP MILESTONES'), findsOneWidget);
      expect(find.text('OPEN IN GOOGLE MAPS (DRIVING DIRECTIONS)'), findsOneWidget);
      expect(find.text('Call ER Doctor'), findsOneWidget);
      expect(find.byIcon(Icons.logout), findsOneWidget);
    });

    testWidgets('HelperRegisterScreen requires live location and proof upload', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: HelperRegisterScreen()),
      );

      expect(find.text('Helper / Responder Registration'), findsOneWidget);
      expect(find.text('LIVE LOCATION TRACKING REQUIRED'), findsOneWidget);
      expect(find.text('PROOF OF MEDICAL KNOWLEDGE / CERTIFICATION'), findsOneWidget);
    });

    testWidgets('HelperDashboardScreen shows live location status and radar', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: HelperDashboardScreen()),
      );

      expect(find.byIcon(Icons.arrow_back), findsNothing);
      expect(find.text('LIVE GPS BROADCASTING TO ER: ACTIVE'), findsOneWidget);
      expect(find.text('NEARBY EMERGENCY RADAR (WITHIN 1.5 KM)'), findsOneWidget);
      expect(find.byIcon(Icons.logout), findsOneWidget);
    });

    testWidgets('PermissionsScreen controls hardware and notification access', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: PermissionsScreen()),
      );

      expect(find.text('Device Permissions Access'), findsOneWidget);
      expect(find.text('Live Location & GPS Access'), findsOneWidget);
      expect(find.text('Microphone & Voice Input'), findsOneWidget);
      expect(find.text('Speaker & Emergency Calling'), findsOneWidget);
      expect(find.text('High-Priority Alert Notifications'), findsOneWidget);
    });

    test('PreferencesService state persistence & login/logout test', () async {
      final prefs = PreferencesService();
      await prefs.loadFromDisk();

      expect(prefs.isLoggedIn, false);
      await prefs.login(role: 'helper', userId: '+919849012345', userName: 'Anjali Devi');
      expect(prefs.isLoggedIn, true);
      expect(prefs.loggedInRole, 'helper');
      expect(prefs.loggedInUserName, 'Anjali Devi');

      await prefs.logout();
      expect(prefs.isLoggedIn, false);
      expect(prefs.loggedInRole, '');

      prefs.completeOnboarding();
      expect(prefs.isOnboardingCompleted, true);
      expect(prefs.isHelperLiveLocationBroadcasting, true);
    });

    test('LocationService distance calculation and formatting', () {
      final formatted1 = LocationService.formatDistance(450);
      expect(formatted1, '450 m');

      final formatted2 = LocationService.formatDistance(2400);
      expect(formatted2, '2.4 km');

      final walking = LocationService.estimateWalkingTime(1000);
      expect(walking, '12 min walk');

      final driving = LocationService.estimateDrivingTime(5000);
      expect(driving, '10 min drive');
    });
  });
}
