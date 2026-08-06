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

  /// Must be called once before app starts (in main.dart)
  Future<void> loadFromDisk() async {
    _prefs = await SharedPreferences.getInstance();
    _isOnboardingCompleted = _prefs!.getBool('onboarding_completed') ?? false;
    _isLoggedIn = _prefs!.getBool('is_logged_in') ?? false;
    _loggedInRole = _prefs!.getString('logged_in_role') ?? '';
    _loggedInUserId = _prefs!.getString('logged_in_user_id') ?? '';
    _loggedInUserName = _prefs!.getString('logged_in_user_name') ?? '';
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
  }) async {
    _isLoggedIn = true;
    _loggedInRole = role;
    _loggedInUserId = userId;
    _loggedInUserName = userName;

    await _prefs?.setBool('is_logged_in', true);
    await _prefs?.setString('logged_in_role', role);
    await _prefs?.setString('logged_in_user_id', userId);
    await _prefs?.setString('logged_in_user_name', userName);
    notifyListeners();
  }

  Future<void> logout() async {
    _isLoggedIn = false;
    _loggedInRole = '';
    _loggedInUserId = '';
    _loggedInUserName = '';

    await _prefs?.setBool('is_logged_in', false);
    await _prefs?.remove('logged_in_role');
    await _prefs?.remove('logged_in_user_id');
    await _prefs?.remove('logged_in_user_name');
    notifyListeners();
  }
}
