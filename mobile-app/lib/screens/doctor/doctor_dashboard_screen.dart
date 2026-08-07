import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../models/emergency_case.dart';
import '../../services/api_service.dart';
import '../../services/notification_service.dart';
import '../../services/preferences_service.dart';
import '../../widgets/app_toast.dart';
import '../../widgets/emergency_alarm_dialog.dart';
import '../auth/unified_login_screen.dart';
import '../../services/websocket_service.dart';

class DoctorDashboardScreen extends StatefulWidget {
  final String doctorName;
  final String hospitalName;

  const DoctorDashboardScreen({
    super.key,
    this.doctorName = 'Doctor',
    this.hospitalName = 'Hospital',
  });

  @override
  State<DoctorDashboardScreen> createState() => _DoctorDashboardScreenState();
}

class _DoctorDashboardScreenState extends State<DoctorDashboardScreen> {
  final PreferencesService _prefs = PreferencesService();
  final ApiService _api = ApiService();

  List<EmergencyCase> _cases = [];
  int _selectedIndex = 0;
  final Set<String> _acceptedCaseIds = {};
  final Set<String> _seenCaseIds = {};
  final Map<String, Map<String, String>> _dynamicVitals = {};
  DateTime? _lastBackPressTime;
  Timer? _pollTimer;
  bool _isAlarmShowing = false;
  StreamSubscription? _wsSubscription;

  @override
  void initState() {
    super.initState();
    _fetchDoctorCases();
    // Poll for assigned cases every 3 seconds as a fallback
    _pollTimer = Timer.periodic(const Duration(seconds: 3), (timer) {
      _fetchDoctorCases();
    });
    
    // Connect to WebSocket for instant pushes
    final doctorId = _prefs.loggedInUserId;
    if (doctorId.isNotEmpty) {
      WebSocketService().connect(doctorId);
      _wsSubscription = WebSocketService().messageStream.listen((message) {
        if (message['type'] == 'NEW_CASE_ASSIGNED') {
          // Force an immediate refresh to fetch the new case details
          _fetchDoctorCases();
        }
      });
    }
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _wsSubscription?.cancel();
    WebSocketService().disconnect();
    super.dispose();
  }

  Future<void> _fetchDoctorCases() async {
    final doctorId = _prefs.loggedInUserId;
    if (doctorId.isEmpty) return;

    try {
      final data = await _api.getDoctorAssignedCases(doctorId);
      final rawList = data['cases'] as List? ?? [];
      final loadedCases = rawList.map((e) => EmergencyCase.fromJson(e as Map<String, dynamic>)).toList();

      if (!mounted) return;

      setState(() {
        _cases = loadedCases;
        for (var c in _cases) {
          if (!_dynamicVitals.containsKey(c.id)) {
            _dynamicVitals[c.id] = Map<String, String>.from(c.vitals);
          }
        }
      });

      // Mark already-accepted cases as seen so old historical cases don't re-trigger
      for (var c in loadedCases) {
        if (c.status == 'DOCTOR_ACCEPTED') {
          _seenCaseIds.add(c.id);
        }
      }

      // Check for newly appointed cases needing doctor response to trigger the Alarm Dialog + Sound
      for (var c in loadedCases) {
        if ((!_seenCaseIds.contains(c.id) || c.status == 'ACCEPTED') && !_isAlarmShowing) {
          _seenCaseIds.add(c.id);
          _triggerEmergencyAlarm(c);
          break;
        }
      }
    } catch (_) {}
  }

  void _triggerEmergencyAlarm(EmergencyCase ec) {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted || _isAlarmShowing) return;
      setState(() => _isAlarmShowing = true);

      // Trigger top notification banner as well
      NotificationService.showInAppAlert(
        context,
        title: '🚨 EMERGENCY DISPATCH ALARM',
        message: 'You have been appointed to ${ec.patientName} (${ec.severity}). Triage incoming!',
        icon: Icons.notifications_active,
        backgroundColor: const Color(0xFFDC2626),
      );

      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (ctx) => EmergencyAlarmDialog(
          emergencyCase: ec,
          onAccept: () async {
            Navigator.of(ctx).pop();
            if (mounted) setState(() => _isAlarmShowing = false);
            _acceptPatient(ec);
            try {
              await _api.acceptDoctorCase(ec.id);
            } catch (_) {}
          },
          onDismiss: () {
            Navigator.of(ctx).pop();
            if (mounted) setState(() => _isAlarmShowing = false);
          },
        ),
      );
    });
  }

  void _acceptPatient(EmergencyCase ec) {
    setState(() {
      _acceptedCaseIds.add(ec.id);
    });

    NotificationService.showInAppAlert(
      context,
      title: 'ER Trauma Bay Reserved',
      message:
          'Trauma team alerted for ${ec.patientName}. Bed #ER-04 pre-allocated.',
      icon: Icons.check_circle,
      backgroundColor: const Color(0xFF065F46),
    );
  }

  void _callPatient(EmergencyCase ec) {
    NotificationService.startDirectCall(
      context,
      contactName: '${ec.patientName} (Field Caller / Bystander)',
      contactRole: 'Emergency Contact',
      associatedCaseId: ec.id,
      phoneNumber: ec.callerPhone,
    );
  }

  void _showEditVitalsDialog(EmergencyCase ec) {
    final vitals = _dynamicVitals[ec.id] ?? ec.vitals;
    final pulseCtrl = TextEditingController(text: vitals['Pulse'] ?? '');
    final bpCtrl = TextEditingController(text: vitals['BP'] ?? '');
    final spo2Ctrl = TextEditingController(text: vitals['SpO2'] ?? '');
    final respCtrl = TextEditingController(text: vitals['Resp'] ?? '');
    final tempCtrl = TextEditingController(text: vitals['Temp'] ?? '98.6 °F');

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Row(
          children: [
            const Icon(Icons.monitor_heart, color: Color(0xFF38BDF8), size: 22),
            const SizedBox(width: 10),
            Text(
              'Update Vitals: ${ec.patientName}',
              style: const TextStyle(color: Colors.white, fontSize: 16),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              _buildVitalInput('Heart Rate / Pulse', pulseCtrl, 'e.g. 118 bpm'),
              const SizedBox(height: 10),
              _buildVitalInput('Blood Pressure', bpCtrl, 'e.g. 120/80 mmHg'),
              const SizedBox(height: 10),
              _buildVitalInput('SpO2 Saturation', spo2Ctrl, 'e.g. 96%'),
              const SizedBox(height: 10),
              _buildVitalInput('Respiratory Rate', respCtrl, 'e.g. 22 /min'),
              const SizedBox(height: 10),
              _buildVitalInput('Body Temperature', tempCtrl, 'e.g. 98.4 °F'),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _dynamicVitals[ec.id] = {
                  'Pulse': pulseCtrl.text.trim().isNotEmpty
                      ? pulseCtrl.text.trim()
                      : (vitals['Pulse'] ?? '--'),
                  'BP': bpCtrl.text.trim().isNotEmpty
                      ? bpCtrl.text.trim()
                      : (vitals['BP'] ?? '--'),
                  'SpO2': spo2Ctrl.text.trim().isNotEmpty
                      ? spo2Ctrl.text.trim()
                      : (vitals['SpO2'] ?? '--'),
                  'Resp': respCtrl.text.trim().isNotEmpty
                      ? respCtrl.text.trim()
                      : (vitals['Resp'] ?? '--'),
                  'Temp': tempCtrl.text.trim().isNotEmpty
                      ? tempCtrl.text.trim()
                      : (vitals['Temp'] ?? '--'),
                };
              });
              Navigator.of(ctx).pop();
              NotificationService.showInAppAlert(
                context,
                title: 'Vitals Updated',
                message: 'Live clinical telemetry updated for ${ec.patientName}.',
                icon: Icons.check_circle,
                backgroundColor: const Color(0xFF0284C7),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0284C7),
              foregroundColor: Colors.white,
            ),
            child: const Text('Save Vitals'),
          ),
        ],
      ),
    );
  }

  Widget _buildVitalInput(
      String label, TextEditingController ctrl, String hint) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFF94A3B8),
            fontSize: 11,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 4),
        TextField(
          controller: ctrl,
          style: const TextStyle(color: Colors.white, fontSize: 13),
          decoration: InputDecoration(
            isDense: true,
            hintText: hint,
            hintStyle: const TextStyle(color: Color(0xFF64748B), fontSize: 12),
            filled: true,
            fillColor: const Color(0xFF0F172A),
            contentPadding:
                const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFF334155)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFF334155)),
            ),
          ),
        ),
      ],
    );
  }

  Future<void> _handleLogout() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Confirm Logout', style: TextStyle(color: Colors.white)),
        content: const Text(
          'Are you sure you want to sign out from the Doctor ER Console?',
          style: TextStyle(color: Color(0xFFCBD5E1)),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(false),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(ctx).pop(true),
            style:
                ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626)),
            child: const Text('Logout', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      await PreferencesService().logout();
      if (mounted) {
        Navigator.of(context).pushAndRemoveUntil(
          MaterialPageRoute(builder: (_) => const UnifiedLoginScreen()),
          (route) => false,
        );
      }
    }
  }

  Color _getSeverityColor(String severity) {
    switch (severity) {
      case 'CRITICAL':
        return const Color(0xFFDC2626);
      case 'HIGH':
        return const Color(0xFFEA580C);
      case 'MODERATE':
      default:
        return const Color(0xFFD97706);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_cases.isEmpty) {
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
                  widget.doctorName,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 15,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  widget.hospitalName,
                  style: const TextStyle(
                    color: Color(0xFF94A3B8),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.logout, color: Color(0xFFEF4444)),
                onPressed: _handleLogout,
                tooltip: 'Logout',
              ),
            ],
          ),
          body: const Center(
            child: Padding(
              padding: EdgeInsets.all(24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.medical_services_outlined, size: 64, color: Color(0xFF64748B)),
                  SizedBox(height: 16),
                  Text(
                    'No Active Case Assigned',
                    style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  SizedBox(height: 8),
                  Text(
                    'Standing by on Green Corridor Duty.\nWhen Hospital Admin appoints you to a case, your emergency alarm will ring.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                  ),
                ],
              ),
            ),
          ),
        ),
      );
    }

    final safeIndex = _selectedIndex < _cases.length ? _selectedIndex : 0;
    final currentCase = _cases[safeIndex];
    final isAccepted = _acceptedCaseIds.contains(currentCase.id);
    final vitals = _dynamicVitals[currentCase.id] ?? currentCase.vitals;

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
              widget.doctorName,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 15,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              widget.hospitalName,
              style: const TextStyle(
                color: Color(0xFF94A3B8),
                fontSize: 11,
              ),
            ),
          ],
        ),
        actions: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF10B981).withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFF10B981)),
            ),
            child: const Row(
              children: [
                Icon(Icons.circle, color: Color(0xFF10B981), size: 8),
                SizedBox(width: 6),
                Text(
                  'ON-DUTY ER',
                  style: TextStyle(
                    color: Color(0xFF10B981),
                    fontWeight: FontWeight.bold,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
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
              // Inbound Patients Selector Tabs
              const Text(
                'INBOUND EMERGENCY QUEUE',
                style: TextStyle(
                  color: Color(0xFF94A3B8),
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                ),
              ),
              const SizedBox(height: 10),

              SizedBox(
                height: 84,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _cases.length,
                  itemBuilder: (context, index) {
                    final c = _cases[index];
                    final isSelected = index == _selectedIndex;
                    final isCaseAccepted = _acceptedCaseIds.contains(c.id);

                    return GestureDetector(
                      onTap: () {
                        setState(() {
                          _selectedIndex = index;
                        });
                      },
                      child: Container(
                        width: 200,
                        margin: const EdgeInsets.only(right: 10),
                        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? const Color(0xFF1E3A8A).withValues(alpha: 0.6)
                              : const Color(0xFF1E293B),
                          borderRadius: BorderRadius.circular(14),
                          border: Border.all(
                            color: isSelected
                                ? const Color(0xFF38BDF8)
                                : const Color(0xFF334155),
                            width: isSelected ? 1.5 : 1,
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Row(
                              children: [
                                Container(
                                  width: 8,
                                  height: 8,
                                  decoration: BoxDecoration(
                                    color: _getSeverityColor(c.severity),
                                    shape: BoxShape.circle,
                                  ),
                                ),
                                const SizedBox(width: 6),
                                Expanded(
                                  child: Text(
                                    c.patientName,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 13,
                                    ),
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                ),
                                if (isCaseAccepted)
                                  const Icon(
                                    Icons.check_circle,
                                    color: Color(0xFF10B981),
                                    size: 14,
                                  ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              'ETA: ${c.etaMinutes} mins • ${c.assignedAmbulanceUnit}',
                              style: const TextStyle(
                                color: Color(0xFF94A3B8),
                                fontSize: 11,
                              ),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
              ),
              const SizedBox(height: 20),

              // Active Case Details Card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(18),
                  border: Border.all(
                    color: _getSeverityColor(currentCase.severity)
                        .withValues(alpha: 0.4),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Case Header
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          currentCase.id,
                          style: const TextStyle(
                            color: Color(0xFF94A3B8),
                            fontFamily: 'monospace',
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 10,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: _getSeverityColor(currentCase.severity)
                                .withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: _getSeverityColor(currentCase.severity),
                            ),
                          ),
                          child: Text(
                            currentCase.severity,
                            style: TextStyle(
                              color: _getSeverityColor(currentCase.severity),
                              fontWeight: FontWeight.bold,
                              fontSize: 11,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 14),

                    // Patient Problem Breakdown
                    const Text(
                      'REPORTED MEDICAL EMERGENCY',
                      style: TextStyle(
                        color: Color(0xFF94A3B8),
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      currentCase.emergencyType,
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 14),

                    // Patient Demographics
                    Container(
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: const Color(0xFF0F172A),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _DoctorBioItem(
                            label: 'Patient',
                            value: currentCase.patientName,
                            icon: Icons.person,
                          ),
                          _DoctorBioItem(
                            label: 'Age / Sex',
                            value:
                                '${currentCase.patientAge}y • ${currentCase.patientGender}',
                            icon: Icons.calendar_today,
                          ),
                          _DoctorBioItem(
                            label: 'Blood Group',
                            value: currentCase.bloodGroup,
                            icon: Icons.bloodtype,
                            highlight: true,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Live Telemetry Vitals Header with Edit Button
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text(
                          'LIVE PRE-HOSPITAL VITALS (TELEMETRY)',
                          style: TextStyle(
                            color: Color(0xFF94A3B8),
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.8,
                          ),
                        ),
                        InkWell(
                          onTap: () => _showEditVitalsDialog(currentCase),
                          borderRadius: BorderRadius.circular(6),
                          child: const Padding(
                            padding:
                                EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            child: Row(
                              children: [
                                Icon(Icons.edit,
                                    color: Color(0xFF38BDF8), size: 14),
                                SizedBox(width: 4),
                                Text(
                                  'Update Vitals',
                                  style: TextStyle(
                                    color: Color(0xFF38BDF8),
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    // Vitals values
                    Row(
                      children: vitals.entries.map((e) {
                        return Expanded(
                          child: Container(
                            margin: const EdgeInsets.symmetric(horizontal: 3),
                            padding: const EdgeInsets.symmetric(
                                vertical: 10, horizontal: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFF0F172A),
                              borderRadius: BorderRadius.circular(10),
                              border:
                                  Border.all(color: const Color(0xFF334155)),
                            ),
                            child: Column(
                              children: [
                                Text(
                                  e.value,
                                  style: const TextStyle(
                                    color: Color(0xFF38BDF8),
                                    fontWeight: FontWeight.bold,
                                    fontSize: 11,
                                  ),
                                  textAlign: TextAlign.center,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  e.key,
                                  style: const TextStyle(
                                    color: Color(0xFF64748B),
                                    fontSize: 10,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                    const SizedBox(height: 16),

                    // Reported Symptoms
                    const Text(
                      'CLINICAL ASSESSMENT & FIELD SYMPTOMS',
                      style: TextStyle(
                        color: Color(0xFF94A3B8),
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        letterSpacing: 0.8,
                      ),
                    ),
                    const SizedBox(height: 8),

                    Column(
                      children: currentCase.reportedSymptoms.map((s) {
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 6),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(
                                Icons.check_circle_outline,
                                color: Color(0xFF38BDF8),
                                size: 16,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  s,
                                  style: const TextStyle(
                                    color: Color(0xFFCBD5E1),
                                    fontSize: 12,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),

              // Doctor Action Buttons
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => _callPatient(currentCase),
                      icon: const Icon(Icons.phone_in_talk, size: 18),
                      label: const Text('Call Patient'),
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: Color(0xFF0284C7)),
                        foregroundColor: const Color(0xFF38BDF8),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton.icon(
                      onPressed:
                          isAccepted ? null : () => _acceptPatient(currentCase),
                      icon: Icon(
                        isAccepted ? Icons.check : Icons.local_hospital,
                        size: 20,
                      ),
                      label: Text(
                        isAccepted
                            ? 'ER Bed Allocated'
                            : 'Accept Patient & ER Bed',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: isAccepted
                            ? const Color(0xFF059669)
                            : const Color(0xFFDC2626),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        elevation: 4,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                    ),
                  ),
                ],
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

class _DoctorBioItem extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final bool highlight;

  const _DoctorBioItem({
    required this.label,
    required this.value,
    required this.icon,
    this.highlight = false,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon,
            color: highlight
                ? const Color(0xFFEF4444)
                : const Color(0xFF94A3B8),
            size: 18),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            color: highlight ? const Color(0xFFEF4444) : Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Color(0xFF64748B),
            fontSize: 10,
          ),
        ),
      ],
    );
  }
}
