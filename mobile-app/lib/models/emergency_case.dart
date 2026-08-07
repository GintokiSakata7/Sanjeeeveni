class EmergencyCase {
  final String id;
  final String patientName;
  final int patientAge;
  final String patientGender;
  final String bloodGroup;
  final String emergencyType;
  final String severity; // CRITICAL, HIGH, MODERATE
  final String locationAddress;
  final double latitude;
  final double longitude;
  final double distanceKm;
  final int etaMinutes;
  final Map<String, String> vitals;
  final List<String> reportedSymptoms;
  final String assignedAmbulanceUnit;
  final String assignedHospital;
  final String callerPhone;
  final String status;
  final bool helperAccepted;
  final String? helperName;
  final DateTime timestamp;

  const EmergencyCase({
    required this.id,
    required this.patientName,
    required this.patientAge,
    required this.patientGender,
    required this.bloodGroup,
    required this.emergencyType,
    required this.severity,
    required this.locationAddress,
    required this.latitude,
    required this.longitude,
    required this.distanceKm,
    required this.etaMinutes,
    required this.vitals,
    required this.reportedSymptoms,
    required this.assignedAmbulanceUnit,
    required this.assignedHospital,
    required this.callerPhone,
    required this.status,
    this.helperAccepted = false,
    this.helperName,
    required this.timestamp,
  });

  factory EmergencyCase.fromJson(Map<String, dynamic> json) {
    Map<String, String> parsedVitals = {};
    if (json['vitals'] is Map) {
      (json['vitals'] as Map).forEach((k, v) {
        parsedVitals[k.toString()] = v.toString();
      });
    } else {
      parsedVitals = {
        'Pulse': '112 bpm',
        'BP': '98/62 mmHg',
        'SpO2': '94%',
        'Resp Rate': '22 /min'
      };
    }

    List<String> symptoms = [];
    if (json['reported_symptoms'] is List) {
      symptoms = (json['reported_symptoms'] as List).map((e) => e.toString()).toList();
    } else if (json['symptoms'] is List) {
      symptoms = (json['symptoms'] as List).map((e) => e.toString()).toList();
    } else {
      symptoms = [json['emergency_type']?.toString() ?? 'Emergency Intake'];
    }

    DateTime parsedTime = DateTime.now();
    if (json['timestamp'] != null) {
      try {
        parsedTime = DateTime.parse(json['timestamp'].toString());
      } catch (_) {}
    }

    return EmergencyCase(
      id: json['id']?.toString() ?? json['case_id']?.toString() ?? 'EMG-LIVE',
      patientName: json['patient_name']?.toString() ?? 'Emergency Victim',
      patientAge: json['patient_age'] is int ? json['patient_age'] : 45,
      patientGender: json['patient_gender']?.toString() ?? 'Emergency Intake',
      bloodGroup: json['blood_group']?.toString() ?? 'O+',
      emergencyType: json['emergency_type']?.toString() ?? 'Severe Emergency',
      severity: json['severity']?.toString() ?? json['triage_urgency']?.toString() ?? 'CRITICAL',
      locationAddress: json['location_address']?.toString() ?? 'Emergency Scene Coordinates',
      latitude: (json['latitude'] ?? json['patient_lat'] ?? 17.4156).toDouble(),
      longitude: (json['longitude'] ?? json['patient_lng'] ?? 78.4357).toDouble(),
      distanceKm: (json['distance_km'] ?? 1.5).toDouble(),
      etaMinutes: json['eta_minutes'] is int ? json['eta_minutes'] : 5,
      vitals: parsedVitals,
      reportedSymptoms: symptoms,
      assignedAmbulanceUnit: json['assigned_ambulance_unit']?.toString() ?? 'ALS-108-HYD-04',
      assignedHospital: json['assigned_hospital']?.toString() ?? 'Apollo Emergency Center',
      callerPhone: json['caller_phone']?.toString() ?? '+91 98765 43210',
      status: json['status']?.toString() ?? 'PENDING',
      timestamp: parsedTime,
    );
  }

  EmergencyCase copyWith({
    String? status,
    bool? helperAccepted,
    String? helperName,
    int? etaMinutes,
    double? distanceKm,
  }) {
    return EmergencyCase(
      id: id,
      patientName: patientName,
      patientAge: patientAge,
      patientGender: patientGender,
      bloodGroup: bloodGroup,
      emergencyType: emergencyType,
      severity: severity,
      locationAddress: locationAddress,
      latitude: latitude,
      longitude: longitude,
      distanceKm: distanceKm ?? this.distanceKm,
      etaMinutes: etaMinutes ?? this.etaMinutes,
      vitals: vitals,
      reportedSymptoms: reportedSymptoms,
      assignedAmbulanceUnit: assignedAmbulanceUnit,
      assignedHospital: assignedHospital,
      callerPhone: callerPhone,
      status: status ?? this.status,
      helperAccepted: helperAccepted ?? this.helperAccepted,
      helperName: helperName ?? this.helperName,
      timestamp: timestamp,
    );
  }

  static List<EmergencyCase> getMockCases() {
    return [
      EmergencyCase(
        id: 'EMG-2026-8901',
        patientName: 'Ramesh Verma',
        patientAge: 54,
        patientGender: 'Male',
        bloodGroup: 'O+',
        emergencyType: 'Road Traffic Accident - Severe Trauma',
        severity: 'CRITICAL',
        locationAddress: 'Near Metro Pillar 142, Banjara Hills, Hyderabad',
        latitude: 17.4156,
        longitude: 78.4357,
        distanceKm: 1.2,
        etaMinutes: 4,
        vitals: {
          'Pulse': '118 bpm',
          'BP': '95/60 mmHg',
          'SpO2': '93%',
          'Resp Rate': '24 /min',
        },
        reportedSymptoms: [
          'High impact vehicle collision with severe blunt trauma',
          'Active limb bleeding & cranial laceration',
          'Rapid response dispatched under green corridor',
        ],
        assignedAmbulanceUnit: 'ALS-108-HYD-04',
        assignedHospital: 'Apollo Emergency Trauma Center',
        callerPhone: '+91 98765 43210',
        status: 'PENDING',
        timestamp: DateTime.now().subtract(const Duration(minutes: 3)),
      ),
      EmergencyCase(
        id: 'EMG-2026-8902',
        patientName: 'Priya Sharma',
        patientAge: 29,
        patientGender: 'Female',
        bloodGroup: 'B+',
        emergencyType: 'Road Traffic Accident - Severe Trauma',
        severity: 'CRITICAL',
        locationAddress: 'Outer Ring Road, Junction 7, Gachibowli',
        latitude: 17.4401,
        longitude: 78.3489,
        distanceKm: 2.8,
        etaMinutes: 7,
        vitals: {
          'Pulse': '112 bpm',
          'BP': '90/60 mmHg',
          'SpO2': '94%',
          'Resp Rate': '22 /min',
        },
        reportedSymptoms: [
          'Two-wheeler collision with median',
          'Right femoral open fracture with active bleeding',
          'Conscious but disoriented',
        ],
        assignedAmbulanceUnit: 'ALS-108-HYD-11',
        assignedHospital: 'Care Hospitals Emergency ER',
        callerPhone: '+91 91234 56789',
        status: 'DISPATCHED',
        timestamp: DateTime.now().subtract(const Duration(minutes: 8)),
      ),
      EmergencyCase(
        id: 'EMG-2026-8903',
        patientName: 'Sunita Reddy',
        patientAge: 62,
        patientGender: 'Female',
        bloodGroup: 'A+',
        emergencyType: 'Suspected Acute Stroke / Hemiparesis',
        severity: 'HIGH',
        locationAddress: 'Plot 45, Jubilee Hills Checkpost',
        latitude: 17.4319,
        longitude: 78.4073,
        distanceKm: 0.9,
        etaMinutes: 3,
        vitals: {
          'Pulse': '88 bpm',
          'BP': '195/115 mmHg',
          'SpO2': '96%',
          'Resp Rate': '18 /min',
        },
        reportedSymptoms: [
          'Sudden facial droop on left side',
          'Inability to raise left arm',
          'Slurred speech noticed at 18:30',
        ],
        assignedAmbulanceUnit: 'BLS-108-HYD-02',
        assignedHospital: 'KIMS Medical Emergency ER',
        callerPhone: '+91 99887 76655',
        status: 'PENDING',
        timestamp: DateTime.now().subtract(const Duration(minutes: 12)),
      ),
    ];
  }
}
