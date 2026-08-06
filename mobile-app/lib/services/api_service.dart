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
      return ['http://localhost:8000', 'http://127.0.0.1:8000'];
    }
    return [
      'http://127.0.0.1:8000',     // ADB reverse (physical device over USB) / Local PC
      'http://10.0.2.2:8000',      // Android Emulator standard loopback
      'http://172.30.187.129:8000', // Wi-Fi LAN IP fallback
      'http://localhost:8000',
    ];
  }

  /// POST helper that tries working base URL first, or discovers the active backend host dynamically.
  Future<Map<String, dynamic>> _post(String path, Map<String, dynamic> body) async {
    final targets = _workingBaseUrl != null
        ? [_workingBaseUrl!, ..._candidateUrls.where((u) => u != _workingBaseUrl)]
        : _candidateUrls;

    Exception? lastException;

    for (final base in targets) {
      final url = Uri.parse('$base$path');
      try {
        final response = await http
            .post(
              url,
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode(body),
            )
            .timeout(const Duration(seconds: 4));

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
      } on ApiException catch (e) {
        // HTTP response received (e.g. 401 Unauthorized), so target URL is valid!
        _workingBaseUrl = base;
        rethrow;
      } on SocketException catch (e) {
        lastException = e;
        continue; // Try next candidate URL
      } on http.ClientException catch (e) {
        lastException = e;
        continue; // Try next candidate URL
      } catch (e) {
        if (e is FormatException) {
          throw ApiException('Invalid response from server.', 0);
        }
        lastException = Exception(e.toString());
      }
    }

    throw ApiException(
      'Cannot connect to backend server at any host (127.0.0.1 / 10.0.2.2).\n'
      'Ensure uvicorn is running on port 8000 and USB debugging / Wi-Fi is active.',
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
}

/// Custom exception for API errors with status code and user-facing message.
class ApiException implements Exception {
  final String message;
  final int statusCode;
  ApiException(this.message, this.statusCode);

  @override
  String toString() => message;
}
