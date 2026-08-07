class EmergencyCase {
  final String id;
  final String? notificationId;
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
    this.notificationId,
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
      id: json['id']?.toString() ?? json['case_id']?.toString() ?? json['sos_id']?.toString() ?? 'EMG-LIVE',
      notificationId: json['notification_id']?.toString(),
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
}
