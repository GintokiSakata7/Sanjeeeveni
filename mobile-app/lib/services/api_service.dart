import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

/// Central HTTP API service for communicating with the Sanjeevani FastAPI backend.
/// Handles doctor login, driver login, helper registration, and helper login.
class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  String? _workingBaseUrl;

  /// Candidate URLs to try depending on environment
  List<String> get _candidateUrls {
    if (kIsWeb) {
      return [
        'http://localhost:8000', 
        'http://127.0.0.1:8000',
        'https://sanjeeeveni.onrender.com'
      ];
    }
    return [
      'http://127.0.0.1:8000',     // ADB reverse (physical device over USB) / Local PC
      'http://10.0.2.2:8000',      // Android Emulator standard loopback
      'http://172.30.187.129:8000', // Wi-Fi LAN IP fallback
      'http://localhost:8000',
      'https://sanjeeeveni.onrender.com', // Secondary Remote
    ];
  }

  /// POST helper that tries working base URL first, or discovers the active backend host dynamically.
  Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> body) async {
    final targets = _workingBaseUrl != null
        ? [_workingBaseUrl!, ..._candidateUrls.where((u) => u != _workingBaseUrl)]
        : _candidateUrls;

    Object? lastError;

    for (final base in targets) {
      final url = Uri.parse('$base$path');
      try {
        final response = await http
            .post(
              url,
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode(body),
            )
            .timeout(const Duration(seconds: 10));

        final decoded = jsonDecode(response.body) as Map<String, dynamic>;

        if (response.statusCode >= 200 && response.statusCode < 300) {
          _workingBaseUrl = base; // Cache successful target host
          return decoded;
        }

        // Extract error detail from FastAPI's standard error response
        String errorMsg = 'Request failed';
        if (decoded.containsKey('detail')) {
          final detail = decoded['detail'];
          if (detail is String) {
            errorMsg = detail;
          } else if (detail is List && detail.isNotEmpty) {
            errorMsg = detail.map((e) => e['msg'] ?? e.toString()).join('; ');
          }
        }
        throw ApiException(errorMsg, response.statusCode);
      } on ApiException {
        // HTTP response received from server (e.g. 401 Unauthorized), host is valid!
        _workingBaseUrl = base;
        rethrow;
      } on TimeoutException catch (e) {
        lastError = e;
        continue; // Try next candidate URL
      } on SocketException catch (e) {
        lastError = e;
        continue; // Try next candidate URL
      } on http.ClientException catch (e) {
        lastError = e;
        continue; // Try next candidate URL
      } catch (e) {
        if (e is FormatException) {
          throw ApiException('Invalid JSON response from server.', 0);
        }
        lastError = e;
        continue;
      }
    }

    throw ApiException(
      'Cannot connect to backend server.\n'
      'Ensure uvicorn is running on port 8000 (Details: ${lastError ?? "Host unreachable"})',
      0,
    );
  }

  // ──────────────────────────────────────────
  // 👨‍⚕️ DOCTOR LOGIN
  // ──────────────────────────────────────────
  /// Login doctor using email or doctor ID + password.
  /// Returns the full auth response map on success.
  Future<Map<String, dynamic>> loginDoctor({
    required String identifier,
    required String password,
  }) async {
    return _post('/api/v1/mobile/login/doctor', {
      'identifier': identifier,
      'password': password,
    });
  }

  // ──────────────────────────────────────────
  // 🚘 DRIVER LOGIN
  // ──────────────────────────────────────────
  /// Login driver using contact number, email, or driver ID + password.
  Future<Map<String, dynamic>> loginDriver({
    required String identifier,
    required String password,
  }) async {
    return _post('/api/v1/mobile/login/driver', {
      'identifier': identifier,
      'password': password,
    });
  }

  // ──────────────────────────────────────────
  // 🤝 HELPER REGISTRATION
  // ──────────────────────────────────────────
  /// Self-register a community helper (ASHA worker, volunteer, etc.).
  Future<Map<String, dynamic>> registerHelper({
    required String name,
    required String phone,
    required String password,
    String? location,
    String roleType = 'ASHA Community Health Worker',
    String? certId,
    List<String> skills = const [],
  }) async {
    return _post('/api/v1/mobile/register/helper', {
      'name': name,
      'phone': phone,
      'password': password,
      'location': location,
      'role_type': roleType,
      'cert_id': certId,
      'skills': skills,
    });
  }

  // ──────────────────────────────────────────
  // 🤝 HELPER LOGIN
  // ──────────────────────────────────────────
  /// Login helper using phone + password.
  Future<Map<String, dynamic>> loginHelper({
    required String phone,
    required String password,
  }) async {
    return _post('/api/v1/mobile/login/helper', {
      'phone': phone,
      'password': password,
    });
  }

  // ──────────────────────────────────────────
  // 🚨 GET HELPERS (GET REQUEST)
  // ──────────────────────────────────────────
  Future<Map<String, dynamic>> _get(String path) async {
    final targets = _workingBaseUrl != null
        ? [_workingBaseUrl!, ..._candidateUrls.where((u) => u != _workingBaseUrl)]
        : _candidateUrls;

    for (final base in targets) {
      final url = Uri.parse('$base$path');
      try {
        final response = await http
            .get(url, headers: {'Accept': 'application/json'})
            .timeout(const Duration(seconds: 10));

        if (response.statusCode >= 200 && response.statusCode < 300) {
          _workingBaseUrl = base;
          return jsonDecode(response.body) as Map<String, dynamic>;
        }
      } catch (_) {
        continue;
      }
    }
    return {'total': 0, 'cases': []};
  }

  /// Get real-time emergency cases appointed to a specific doctor by HMS Admin.
  Future<Map<String, dynamic>> getDoctorAssignedCases(String doctorId) async {
    return _get('/api/v1/mobile/doctor/assigned-cases/$doctorId');
  }

  /// Confirm & accept assigned emergency case on doctor mobile app.
  Future<Map<String, dynamic>> acceptDoctorCase(String sosId) async {
    return _post('/api/v1/mobile/doctor/accept-case/$sosId', {});
  }

  /// Get live emergency cases for drivers and community helpers.
  Future<Map<String, dynamic>> getLiveCases() async {
    return _get('/api/v1/mobile/cases/live');
  }
}

/// Custom exception for API errors with status code and user-facing message.
class ApiException implements Exception {
  final String message;
  final int statusCode;
  ApiException(this.message, this.statusCode);

  @override
  String toString() => message;
}
