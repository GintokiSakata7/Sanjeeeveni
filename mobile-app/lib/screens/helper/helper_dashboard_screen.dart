import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import '../../models/emergency_case.dart';
import '../../services/location_service.dart';
import '../../services/notification_service.dart';
import '../../services/preferences_service.dart';
import '../../widgets/app_toast.dart';
import '../auth/unified_login_screen.dart';

class HelperDashboardScreen extends StatefulWidget {
  final String helperName;
  final String helperLocation;

  const HelperDashboardScreen({
    super.key,
    this.helperName = 'Anjali Devi (ASHA Worker)',
    this.helperLocation = 'Banjara Hills Sector 4, Hyderabad',
  });

  @override
  State<HelperDashboardScreen> createState() => _HelperDashboardScreenState();
}

class _HelperDashboardScreenState extends State<HelperDashboardScreen> {
  final PreferencesService _prefs = PreferencesService();
  late List<EmergencyCase> _nearbyCases;
  EmergencyCase? _acceptedCase;
  Position? _currentGpsPosition;
  String _calculatedDistanceText = '';
  String _calculatedEtaText = '';
  DateTime? _lastBackPressTime;

  @override
  void initState() {
    super.initState();
    _nearbyCases = EmergencyCase.getMockCases();
    _fetchHelperGps();
  }

  Future<void> _fetchHelperGps() async {
    final pos = await LocationService.getCurrentPosition();
    if (pos != null && mounted) {
      setState(() {
        _currentGpsPosition = pos;
      });
      _updateDistancesWithRealGps(pos);
    }
  }

  void _updateDistancesWithRealGps(Position pos) {
    if (_acceptedCase != null) {
      final meters = LocationService.distanceInMeters(
        fromLat: pos.latitude,
        fromLng: pos.longitude,
        toLat: _acceptedCase!.latitude,
        toLng: _acceptedCase!.longitude,
      );
      setState(() {
        _calculatedDistanceText = LocationService.formatDistance(meters);
        _calculatedEtaText = LocationService.estimateWalkingTime(meters);
      });
    }
  }

  void _acceptCase(EmergencyCase ec) {
    setState(() {
      _acceptedCase = ec;
      _nearbyCases.removeWhere((item) => item.id == ec.id);
      _calculatedDistanceText = '${ec.distanceKm} km';
      _calculatedEtaText = '${ec.etaMinutes} min walk';
    });

    if (_currentGpsPosition != null) {
      _updateDistancesWithRealGps(_currentGpsPosition!);
    }

    NotificationService.showInAppAlert(
      context,
      title: 'Emergency Case Accepted',
      message: 'Routing to ${ec.patientName}. Directions ready.',
      icon: Icons.check_circle,
      backgroundColor: const Color(0xFF059669),
    );
  }

  void _rejectCase(EmergencyCase ec) {
    setState(() {
      _nearbyCases.removeWhere((item) => item.id == ec.id);
    });

    NotificationService.showInAppAlert(
      context,
      title: 'Incident Passed',
      message: 'Alert transferred to the next nearest community responder.',
      icon: Icons.redo,
      backgroundColor: const Color(0xFF334155),
    );
  }

  void _launchGoogleMapsNavigation(EmergencyCase ec) {
    LocationService.openGoogleMapsDirections(
      destinationLat: ec.latitude,
      destinationLng: ec.longitude,
      travelMode: 'walking',
    );
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Confirm Logout', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Are you sure you want to sign out from the Helper Portal?',
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
    final isGpsBroadcasting = _prefs.isHelperLiveLocationBroadcasting;

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
              widget.helperName,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              widget.helperLocation,
              style: const TextStyle(
                color: Color(0xFF34D399),
                fontSize: 11,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
        actions: [
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
              // Live Location Status Banner
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: isGpsBroadcasting
                      ? const Color(0xFF064E3B)
                      : const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isGpsBroadcasting
                        ? const Color(0xFF10B981)
                        : const Color(0xFF475569),
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 10,
                      height: 10,
                      decoration: BoxDecoration(
                        color: isGpsBroadcasting
                            ? const Color(0xFF34D399)
                            : const Color(0xFF94A3B8),
                        shape: BoxShape.circle,
                        boxShadow: isGpsBroadcasting
                            ? [
                                const BoxShadow(
                                  color: Color(0xFF34D399),
                                  blurRadius: 8,
                                  spreadRadius: 2,
                                )
                              ]
                            : null,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isGpsBroadcasting
                                ? 'LIVE GPS BROADCASTING TO ER: ACTIVE'
                                : 'LOCATION BROADCASTING PAUSED',
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                              letterSpacing: 0.5,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            _currentGpsPosition != null
                                ? 'Lat: ${_currentGpsPosition!.latitude.toStringAsFixed(4)}°, Lng: ${_currentGpsPosition!.longitude.toStringAsFixed(4)}° (Real GPS)'
                                : 'Hospital management receives real-time proximity alerts for critical calls.',
                            style: const TextStyle(
                              color: Color(0xFF94A3B8),
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),

              // Active Accepted Emergency Card
              if (_acceptedCase != null) ...[
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFF10B981), width: 1.5),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF10B981).withValues(alpha: 0.15),
                        blurRadius: 16,
                        offset: const Offset(0, 4),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.navigation, color: Color(0xFF10B981), size: 18),
                              SizedBox(width: 6),
                              Text(
                                'LIVE PATIENT TRACKING & NAVIGATION',
                                style: TextStyle(
                                  color: Color(0xFF10B981),
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                  letterSpacing: 0.5,
                                ),
                              ),
                            ],
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFF10B981).withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              _acceptedCase!.id,
                              style: const TextStyle(
                                color: Color(0xFF34D399),
                                fontFamily: 'monospace',
                                fontWeight: FontWeight.bold,
                                fontSize: 11,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),

                      // Patient Details
                      Text(
                        _acceptedCase!.emergencyType,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Patient: ${_acceptedCase!.patientName} (${_acceptedCase!.patientAge}y, ${_acceptedCase!.patientGender}) • Blood: ${_acceptedCase!.bloodGroup}',
                        style: const TextStyle(
                          color: Color(0xFF38BDF8),
                          fontSize: 13,
                        ),
                      ),
                      const SizedBox(height: 12),

                      // Location & Distance Box
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: const Color(0xFF0F172A),
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: const Color(0xFF334155)),
                        ),
                        child: Column(
                          children: [
                            Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Icon(Icons.location_on, color: Color(0xFFF87171), size: 20),
                                const SizedBox(width: 8),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        _acceptedCase!.locationAddress,
                                        style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 13,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        'GPS: ${_acceptedCase!.latitude.toStringAsFixed(4)}° N, ${_acceptedCase!.longitude.toStringAsFixed(4)}° E',
                                        style: const TextStyle(
                                          color: Color(0xFF94A3B8),
                                          fontSize: 11,
                                          fontFamily: 'monospace',
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const Divider(color: Color(0xFF334155), height: 16),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                Row(
                                  children: [
                                    const Icon(Icons.straighten, color: Color(0xFF38BDF8), size: 16),
                                    const SizedBox(width: 4),
                                    Text(
                                      'Distance: ${_calculatedDistanceText.isNotEmpty ? _calculatedDistanceText : '${_acceptedCase!.distanceKm} km'}',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                                Container(width: 1, height: 16, color: const Color(0xFF334155)),
                                Row(
                                  children: [
                                    const Icon(Icons.directions_walk, color: Color(0xFF34D399), size: 16),
                                    const SizedBox(width: 4),
                                    Text(
                                      'ETA: ${_calculatedEtaText.isNotEmpty ? _calculatedEtaText : '${_acceptedCase!.etaMinutes} min walk'}',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontWeight: FontWeight.bold,
                                        fontSize: 12,
                                      ),
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      // Prominent Redirect Button to Google Maps
                      ElevatedButton.icon(
                        onPressed: () => _launchGoogleMapsNavigation(_acceptedCase!),
                        icon: const Icon(Icons.directions, color: Colors.white, size: 20),
                        label: const Text(
                          'GET DIRECTIONS (OPEN GOOGLE MAPS)',
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
                      const SizedBox(height: 14),

                      // Handoff Done Button
                      ElevatedButton.icon(
                        onPressed: () {
                          setState(() {
                            _acceptedCase = null;
                          });
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text(
                                'Emergency handoff completed. Thank you for your assistance!',
                              ),
                              backgroundColor: Color(0xFF10B981),
                            ),
                          );
                        },
                        icon: const Icon(Icons.check_circle, size: 20),
                        label: const Text(
                          'HANDOFF TO PARAMEDICS COMPLETED',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF10B981),
                          foregroundColor: Colors.white,
                          minimumSize: const Size(double.infinity, 48),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 3,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
              ],

              // Nearby Emergencies Radar Header
              const Text(
                'NEARBY EMERGENCY RADAR (WITHIN 1.5 KM)',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 10),

              if (_nearbyCases.isEmpty)
                Container(
                  padding: const EdgeInsets.all(24),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Center(
                    child: Column(
                      children: [
                        Icon(Icons.check_circle, color: Color(0xFF10B981), size: 36),
                        SizedBox(height: 8),
                        Text(
                          'No Active Emergencies in Your Immediate Radius',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                        ),
                        SizedBox(height: 4),
                        Text(
                          'Stay active on GPS. We will sound an alert if an emergency occurs.',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                )
              else
                Column(
                  children: _nearbyCases.map((ec) {
                    return Container(
                      margin: const EdgeInsets.only(bottom: 14),
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
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                decoration: BoxDecoration(
                                  color: const Color(0xFFDC2626).withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  ec.severity,
                                  style: const TextStyle(
                                    color: Color(0xFFF87171),
                                    fontWeight: FontWeight.bold,
                                    fontSize: 11,
                                  ),
                                ),
                              ),
                              Row(
                                children: [
                                  const Icon(Icons.location_on, color: Color(0xFF38BDF8), size: 14),
                                  const SizedBox(width: 4),
                                  Text(
                                    '${ec.distanceKm} km away • ${ec.etaMinutes} min',
                                    style: const TextStyle(
                                      color: Color(0xFF94A3B8),
                                      fontSize: 12,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          const SizedBox(height: 10),
                          Text(
                            ec.emergencyType,
                            style: const TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                              fontSize: 15,
                            ),
                          ),
                          const SizedBox(height: 4),
                          Text(
                            ec.locationAddress,
                            style: const TextStyle(
                              color: Color(0xFF94A3B8),
                              fontSize: 12,
                            ),
                          ),
                          const SizedBox(height: 14),
                          Row(
                            children: [
                              Expanded(
                                child: OutlinedButton(
                                  onPressed: () => _rejectCase(ec),
                                  style: OutlinedButton.styleFrom(
                                    side: const BorderSide(color: Color(0xFF475569)),
                                    foregroundColor: const Color(0xFF94A3B8),
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                  ),
                                  child: const Text('PASS'),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                flex: 2,
                                child: ElevatedButton(
                                  onPressed: () => _acceptCase(ec),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF059669),
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 12),
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    elevation: 2,
                                  ),
                                  child: const Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      Icon(Icons.check, size: 18),
                                      SizedBox(width: 6),
                                      Text(
                                        'ACCEPT EMERGENCY',
                                        style: TextStyle(
                                          fontWeight: FontWeight.bold,
                                          fontSize: 12,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    );
                  }).toList(),
                ),
            ],
          ),
        ),
      ),
    ),
  );
}
}
