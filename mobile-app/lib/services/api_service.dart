import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/triage_result.dart';

class ApiService {
  // Works with Android emulator (10.0.2.2) and physical USB device (127.0.0.1 with ADB reverse)
  static const String _baseUrl = 'http://127.0.0.1:8000/api/emergency';

  static Future<TriageResult> submitSos({
    required String text,
    required String language,
    double latitude = 17.3850,
    double longitude = 78.4867,
  }) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/sos'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text': text,
        'input_mode': 'type',
        'language': language,
        'latitude': latitude,
        'longitude': longitude,
      }),
    );

    if (response.statusCode == 200) {
      return TriageResult.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Backend error: ${response.statusCode} ${response.body}');
    }
  }
}
