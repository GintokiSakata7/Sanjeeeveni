import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // Use 10.0.2.2 for Android emulator, localhost for Windows/Web, or your local IP for physical devices.
  static const String baseUrl = 'http://localhost:8000/api/v1';

  static Future<Map<String, dynamic>> registerHelper({
    required String name,
    required String phone,
    required String password,
    required String roleType,
    required String location,
    required String certificateId,
    required List<String> skills,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/helpers/register'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'name': name,
          'phone': phone,
          'password': password,
          'role_type': roleType,
          'location': location,
          'certificate_id': certificateId,
          'skills': skills,
          'latitude': 17.3850,
          'longitude': 78.4867,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Failed to register helper');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }

  static Future<Map<String, dynamic>> loginHelper({
    required String phone,
    required String password,
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/auth/helpers/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone': phone,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['detail'] ?? 'Invalid phone number or password');
      }
    } catch (e) {
      throw Exception('Network error: $e');
    }
  }
}
