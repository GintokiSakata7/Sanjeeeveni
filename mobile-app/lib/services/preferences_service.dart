import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class PreferencesService extends ChangeNotifier {
  static final PreferencesService _instance = PreferencesService._internal();
  factory PreferencesService() => _instance;
  PreferencesService._internal();

  SharedPreferences? _prefs;

  // --- Onboarding & Permissions (in-memory + disk) ---
  bool _isOnboardingCompleted = false;
  bool _isLocationGranted = true;
  bool _isMicrophoneGranted = true;
  bool _isSpeakerGranted = true;
  bool _isNotificationGranted = true;
  bool _isHelperLiveLocationBroadcasting = true;

  // --- Persistent Login (disk) ---
  bool _isLoggedIn = false;
  String _loggedInRole = '';
  String _loggedInUserId = '';
  String _loggedInUserName = '';
  String _authToken = '';
  String _hospitalId = '';
  String _hospitalName = '';
  String _specialization = '';
  String _contactNumber = '';
  String _email = '';
  String _shiftTiming = '';
  String _badgeId = '';
  String _licenseNumber = '';
  String _location = '';
  String _roleType = '';
  String _assignedAmbulanceId = '';

  // Getters
  bool get isOnboardingCompleted => _isOnboardingCompleted;
  bool get isLocationGranted => _isLocationGranted;
  bool get isMicrophoneGranted => _isMicrophoneGranted;
  bool get isSpeakerGranted => _isSpeakerGranted;
  bool get isNotificationGranted => _isNotificationGranted;
  bool get isHelperLiveLocationBroadcasting => _isHelperLiveLocationBroadcasting;
  bool get isLoggedIn => _isLoggedIn;
  String get loggedInRole => _loggedInRole;
  String get loggedInUserId => _loggedInUserId;
  String get loggedInUserName => _loggedInUserName;
  String get authToken => _authToken;
  String get hospitalId => _hospitalId;
  String get hospitalName => _hospitalName;
  String get specialization => _specialization;
  String get contactNumber => _contactNumber;
  String get email => _email;
  String get shiftTiming => _shiftTiming;
  String get badgeId => _badgeId;
  String get licenseNumber => _licenseNumber;
  String get location => _location;
  String get roleType => _roleType;
  String get assignedAmbulanceId => _assignedAmbulanceId;

  /// Must be called once before app starts (in main.dart)
  Future<void> loadFromDisk() async {
    _prefs = await SharedPreferences.getInstance();
    _isOnboardingCompleted = _prefs!.getBool('onboarding_completed') ?? false;
    _isLoggedIn = _prefs!.getBool('is_logged_in') ?? false;
    _loggedInRole = _prefs!.getString('logged_in_role') ?? '';
    _loggedInUserId = _prefs!.getString('logged_in_user_id') ?? '';
    _loggedInUserName = _prefs!.getString('logged_in_user_name') ?? '';
    _authToken = _prefs!.getString('auth_token') ?? '';
    _hospitalId = _prefs!.getString('hospital_id') ?? '';
    _hospitalName = _prefs!.getString('hospital_name') ?? '';
    _specialization = _prefs!.getString('specialization') ?? '';
    _contactNumber = _prefs!.getString('contact_number') ?? '';
    _email = _prefs!.getString('email') ?? '';
    _shiftTiming = _prefs!.getString('shift_timing') ?? '';
    _badgeId = _prefs!.getString('badge_id') ?? '';
    _licenseNumber = _prefs!.getString('license_number') ?? '';
    _location = _prefs!.getString('location') ?? '';
    _roleType = _prefs!.getString('role_type') ?? '';
    _assignedAmbulanceId = _prefs!.getString('assigned_ambulance_id') ?? '';
    notifyListeners();
  }

  // --- Onboarding ---
  void completeOnboarding() {
    _isOnboardingCompleted = true;
    _prefs?.setBool('onboarding_completed', true);
    notifyListeners();
  }

  // --- Permissions ---
  void setLocationPermission(bool val) {
    _isLocationGranted = val;
    notifyListeners();
  }

  void setMicrophonePermission(bool val) {
    _isMicrophoneGranted = val;
    notifyListeners();
  }

  void setSpeakerPermission(bool val) {
    _isSpeakerGranted = val;
    notifyListeners();
  }

  void setNotificationPermission(bool val) {
    _isNotificationGranted = val;
    notifyListeners();
  }

  void setHelperLiveLocation(bool val) {
    _isHelperLiveLocationBroadcasting = val;
    notifyListeners();
  }

  void grantAllPermissions() {
    _isLocationGranted = true;
    _isMicrophoneGranted = true;
    _isSpeakerGranted = true;
    _isNotificationGranted = true;
    notifyListeners();
  }

  // --- Persistent Login ---
  Future<void> login({
    required String role,
    required String userId,
    required String userName,
    String token = '',
    String hospitalId = '',
    String hospitalName = '',
    String specialization = '',
    String contactNumber = '',
    String email = '',
    String shiftTiming = '',
    String badgeId = '',
    String licenseNumber = '',
    String location = '',
    String roleType = '',
    String assignedAmbulanceId = '',
  }) async {
    _isLoggedIn = true;
    _loggedInRole = role;
    _loggedInUserId = userId;
    _loggedInUserName = userName;
    _authToken = token;
    _hospitalId = hospitalId;
    _hospitalName = hospitalName;
    _specialization = specialization;
    _contactNumber = contactNumber;
    _email = email;
    _shiftTiming = shiftTiming;
    _badgeId = badgeId;
    _licenseNumber = licenseNumber;
    _location = location;
    _roleType = roleType;
    _assignedAmbulanceId = assignedAmbulanceId;

    await _prefs?.setBool('is_logged_in', true);
    await _prefs?.setString('logged_in_role', role);
    await _prefs?.setString('logged_in_user_id', userId);
    await _prefs?.setString('logged_in_user_name', userName);
    await _prefs?.setString('auth_token', token);
    await _prefs?.setString('hospital_id', hospitalId);
    await _prefs?.setString('hospital_name', hospitalName);
    await _prefs?.setString('specialization', specialization);
    await _prefs?.setString('contact_number', contactNumber);
    await _prefs?.setString('email', email);
    await _prefs?.setString('shift_timing', shiftTiming);
    await _prefs?.setString('badge_id', badgeId);
    await _prefs?.setString('license_number', licenseNumber);
    await _prefs?.setString('location', location);
    await _prefs?.setString('role_type', roleType);
    await _prefs?.setString('assigned_ambulance_id', assignedAmbulanceId);
    notifyListeners();
  }

  Future<void> logout() async {
    _isLoggedIn = false;
    _loggedInRole = '';
    _loggedInUserId = '';
    _loggedInUserName = '';
    _authToken = '';
    _hospitalId = '';
    _hospitalName = '';
    _specialization = '';
    _contactNumber = '';
    _email = '';
    _shiftTiming = '';
    _badgeId = '';
    _licenseNumber = '';
    _location = '';
    _roleType = '';

    await _prefs?.setBool('is_logged_in', false);
    await _prefs?.remove('logged_in_role');
    await _prefs?.remove('logged_in_user_id');
    await _prefs?.remove('logged_in_user_name');
    await _prefs?.remove('auth_token');
    await _prefs?.remove('hospital_id');
    await _prefs?.remove('hospital_name');
    await _prefs?.remove('specialization');
    await _prefs?.remove('contact_number');
    await _prefs?.remove('email');
    await _prefs?.remove('shift_timing');
    await _prefs?.remove('badge_id');
    await _prefs?.remove('license_number');
    await _prefs?.remove('location');
    await _prefs?.remove('role_type');
    notifyListeners();
  }
}
