import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import '../../models/emergency_case.dart';
import '../../services/api_service.dart';
import '../../services/location_service.dart';
import '../../services/notification_service.dart';
import '../../services/preferences_service.dart';
import '../../widgets/app_toast.dart';
import '../../widgets/live_tracker_card.dart';
import '../auth/unified_login_screen.dart';

class DriverDashboardScreen extends StatefulWidget {
  final String driverName;
  final String badgeId;
  final String ambulanceUnit;

  const DriverDashboardScreen({
    super.key,
    this.driverName = 'Suresh Kumar',
    this.badgeId = 'DRV-108-HYD-44',
    this.ambulanceUnit = 'ALS-108-HYD-04',
  });

  @override
  State<DriverDashboardScreen> createState() => _DriverDashboardScreenState();
}

class _DriverDashboardScreenState extends State<DriverDashboardScreen> {
  final PreferencesService _prefs = PreferencesService();
  late EmergencyCase _activeCase;
  int _currentMilestoneIndex = 0;
  Position? _currentGpsPosition;
  String _calculatedDistanceText = '';
  String _calculatedEtaText = '';
  DateTime? _lastBackPressTime;

  final List<String> _milestones = [
    'Dispatch Acknowledged & Siren Engaged',
    'Navigating Scene (Green Corridor GPS)',
    'Arrived at Scene & Field Triage',
    'Patient Stabilized & Loaded to Ambulance',
    'In Transit to Hospital ER Trauma Bay',
    'Arrived at Hospital & Handoff to ER Physician',
  ];

  EmergencyCase _createDefaultCase() {
    return EmergencyCase(
      id: 'EMG-STANDBY-01',
      patientName: 'Standby Emergency Intake',
      patientAge: 40,
      patientGender: 'Emergency',
      bloodGroup: 'O+',
      emergencyType: 'Green Corridor Dispatch Standby',
      severity: 'MODERATE',
      locationAddress: 'Hyderabad Metropolitan Area',
      latitude: 17.4126,
      longitude: 78.4482,
      distanceKm: 1.5,
      etaMinutes: 5,
      vitals: {'Status': 'Awaiting Active Dispatch'},
      reportedSymptoms: ['Standby for incoming emergency call'],
      assignedAmbulanceUnit: widget.ambulanceUnit,
      assignedHospital: 'Sanjeevani ER Center',
      callerPhone: '+91 98765 43210',
      status: 'STANDBY',
      timestamp: DateTime.now(),
    );
  }

  @override
  void initState() {
    super.initState();
    _activeCase = _createDefaultCase();
    _loadLiveDriverCase();
    _fetchDriverGps();
  }

  Future<void> _loadLiveDriverCase() async {
    try {
      final res = await ApiService().getLiveCases();
      final list = res['cases'] as List? ?? [];
      if (list.isNotEmpty && mounted) {
        setState(() {
          _activeCase = EmergencyCase.fromJson(list.first as Map<String, dynamic>);
        });
        _fetchDriverGps();
      }
    } catch (_) {}
  }

  Future<void> _fetchDriverGps() async {
    final pos = await LocationService.getCurrentPosition();
    if (pos != null && mounted) {
      setState(() {
        _currentGpsPosition = pos;
      });
      final meters = LocationService.distanceInMeters(
        fromLat: pos.latitude,
        fromLng: pos.longitude,
        toLat: _activeCase.latitude,
        toLng: _activeCase.longitude,
      );
      setState(() {
        _calculatedDistanceText = LocationService.formatDistance(meters);
        _calculatedEtaText = LocationService.estimateDrivingTime(meters);
      });
    }
  }

  void _triggerAlarmModal() {
    NotificationService.triggerEmergencySirenAlarm(
      context,
      emergencyCase: _activeCase,
      onAccept: () {
        setState(() {
          _currentMilestoneIndex = 0;
        });
        NotificationService.showInAppAlert(
          context,
          title: 'Dispatch Locked & Siren Activated',
          message: 'Navigation engaged to ${_activeCase.locationAddress}.',
          icon: Icons.navigation,
          backgroundColor: const Color(0xFFDC2626),
        );
      },
    );
  }

  void _advanceMilestone() {
    if (_currentMilestoneIndex < _milestones.length - 1) {
      setState(() {
        _currentMilestoneIndex++;
      });
      NotificationService.showInAppAlert(
        context,
        title: 'Status Broadcasted to ER Command',
        message: 'Milestone: ${_milestones[_currentMilestoneIndex]}',
        icon: Icons.check_circle,
        backgroundColor: const Color(0xFF059669),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Trip Completed. Patient safely handed over to ER.'),
          backgroundColor: Color(0xFF10B981),
        ),
      );
    }
  }

  void _callDoctor() {
    NotificationService.startDirectCall(
      context,
      contactName: 'Dr. Rajesh Sharma (ER Duty Head)',
      contactRole: 'Hospital Emergency Physician',
      associatedCaseId: _activeCase.id,
      phoneNumber: '+91 108-DOC-ER',
    );
  }

  void _callPatientCaller() {
    NotificationService.startDirectCall(
      context,
      contactName: 'Emergency Bystander / Caller',
      contactRole: 'Field Caller',
      associatedCaseId: _activeCase.id,
      phoneNumber: _activeCase.callerPhone,
    );
  }

  void _launchGoogleMapsDirections() {
    LocationService.openGoogleMapsDirections(
      destinationLat: _activeCase.latitude,
      destinationLng: _activeCase.longitude,
      travelMode: 'driving',
    );
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Confirm Logout', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Are you sure you want to sign out from the Ambulance Driver Portal?',
          style: TextStyle(color: Color(0xFFCBD5E1)),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626)),
            child: const Text('Logout', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await _prefs.logout();
      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const UnifiedLoginScreen()),
          (route) => false,
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: false,
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        final now = DateTime.now();
        if (_lastBackPressTime == null ||
            now.difference(_lastBackPressTime!) > const Duration(seconds: 2)) {
          _lastBackPressTime = now;
          AppToast.show(context);
        } else {
          SystemNavigator.pop();
        }
      },
      child: Scaffold(
        backgroundColor: const Color(0xFF0F172A),
        appBar: AppBar(
          backgroundColor: const Color(0xFF0F172A),
          elevation: 0,
          automaticallyImplyLeading: false,
          title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '${widget.driverName} (${widget.badgeId})',
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              widget.ambulanceUnit,
              style: const TextStyle(
                color: Color(0xFF38BDF8),
                fontSize: 11,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.crisis_alert, color: Color(0xFFEF4444)),
            tooltip: 'Simulate Siren Alarm',
            onPressed: _triggerAlarmModal,
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Color(0xFFF87171)),
            tooltip: 'Logout',
            onPressed: _handleLogout,
          ),
        ],
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Siren Alert Trigger Banner
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFF7F1D1D),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: const Color(0xFFEF4444)),
                ),
                child: Row(
                  children: [
                    const Icon(
                      Icons.crisis_alert,
                      color: Colors.white,
                      size: 24,
                    ),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'ACTIVE EMERGENCY DISPATCH',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                              letterSpacing: 0.5,
                            ),
                          ),
                          SizedBox(height: 2),
                          Text(
                            'Siren & Green Corridor GPS Route Active',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                    ElevatedButton(
                      onPressed: _triggerAlarmModal,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: const Color(0xFFDC2626),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      child: const Text(
                        'Re-Alarm',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              // Live Navigation HUD
              LiveTrackerCard(
                originLabel: _currentGpsPosition != null
                    ? 'Current GPS (${_currentGpsPosition!.latitude.toStringAsFixed(3)}°, ${_currentGpsPosition!.longitude.toStringAsFixed(3)}°)'
                    : 'Current Location: Banjara Hills Base Station',
                destinationLabel: _activeCase.locationAddress,
                responderType: 'Ambulance',
                distanceKm: _calculatedDistanceText.isNotEmpty
                    ? double.tryParse(_calculatedDistanceText.split(' ')[0]) ?? _activeCase.distanceKm
                    : _activeCase.distanceKm,
                etaMinutes: _calculatedEtaText.isNotEmpty
                    ? int.tryParse(_calculatedEtaText.split(' ')[0]) ?? _activeCase.etaMinutes
                    : _activeCase.etaMinutes,
                corridorStatus: 'Priority Siren Route Active',
                onExpandMap: _launchGoogleMapsDirections,
              ),
              const SizedBox(height: 14),

              // Prominent Google Maps Navigation Button
              ElevatedButton.icon(
                onPressed: _launchGoogleMapsDirections,
                icon: const Icon(Icons.directions_car, color: Colors.white, size: 20),
                label: const Text(
                  'OPEN IN GOOGLE MAPS (DRIVING DIRECTIONS)',
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 0.5,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0284C7),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 48),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  elevation: 3,
                ),
              ),
              const SizedBox(height: 20),

              // Assigned Patient Case Info
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          _activeCase.id,
                          style: const TextStyle(
                            color: Color(0xFF94A3B8),
                            fontFamily: 'monospace',
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFDC2626).withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            _activeCase.severity,
                            style: const TextStyle(
                              color: Color(0xFFF87171),
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _activeCase.emergencyType,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Patient: ${_activeCase.patientName} (${_activeCase.patientAge}y, ${_activeCase.patientGender}) • Blood: ${_activeCase.bloodGroup}',
                      style: const TextStyle(
                        color: Color(0xFF38BDF8),
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 12),

                    // Quick Communication Buttons
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _callDoctor,
                            icon: const Icon(Icons.call, size: 16),
                            label: const Text('Call ER Doctor'),
                            style: OutlinedButton.styleFrom(
                              side: const BorderSide(color: Color(0xFF0284C7)),
                              foregroundColor: const Color(0xFF38BDF8),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _callPatientCaller,
                            icon: const Icon(Icons.phone_in_talk, size: 16),
                            label: const Text('Call Caller'),
                            style: OutlinedButton.styleFrom(
                              side: const BorderSide(color: Color(0xFF10B981)),
                              foregroundColor: const Color(0xFF34D399),
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(10),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Trip Milestones Stepper
              const Text(
                'LIVE DISPATCH TRIP MILESTONES',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 12),

              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFF334155)),
                ),
                child: Column(
                  children: List.generate(_milestones.length, (index) {
                    final isDone = index < _currentMilestoneIndex;
                    final isCurrent = index == _currentMilestoneIndex;

                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: Row(
                        children: [
                          Container(
                            width: 24,
                            height: 24,
                            decoration: BoxDecoration(
                              color: isDone
                                  ? const Color(0xFF10B981)
                                  : isCurrent
                                      ? const Color(0xFF0284C7)
                                      : const Color(0xFF334155),
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              isDone ? Icons.check : Icons.circle,
                              color: Colors.white,
                              size: 14,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: Text(
                              _milestones[index],
                              style: TextStyle(
                                color: isCurrent
                                    ? Colors.white
                                    : isDone
                                        ? const Color(0xFF94A3B8)
                                        : const Color(0xFF64748B),
                                fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                                fontSize: 13,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  }),
                ),
              ),
              const SizedBox(height: 20),

              // Advance Milestone Action Button
              ElevatedButton.icon(
                onPressed: _advanceMilestone,
                icon: const Icon(Icons.arrow_forward_rounded, size: 20),
                label: Text(
                  _currentMilestoneIndex >= _milestones.length - 1
                      ? 'Trip Completed'
                      : 'Next Milestone: ${_milestones[_currentMilestoneIndex + 1]}',
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFDC2626),
                  foregroundColor: Colors.white,
                  minimumSize: const Size(double.infinity, 52),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                  ),
                  elevation: 4,
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    ),
  );
}
}
