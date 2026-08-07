import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'api_service.dart';

/// Unified WebSocket service that supports Doctor, Driver, and Helper channels.
/// Each role connects to a different WebSocket endpoint on the backend.
class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>> _messageController = StreamController<Map<String, dynamic>>.broadcast();
  String? _userId;
  String? _role;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  bool _isConnecting = false;

  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;

  /// Connect to the appropriate WebSocket channel based on user role.
  /// [role] must be one of: 'doctor', 'driver', 'helper'
  /// [userId] is the doctor_id, driver_id, or helper_id
  void connect(String userId, {String role = 'doctor'}) {
    if (_isConnecting) return;
    
    if (_channel != null && _userId == userId && _role == role) {
      return; // Already connected to same channel
    }
    
    _userId = userId;
    _role = role;
    _isConnecting = true;
    _disconnectInternal();

    // Build WebSocket URL based on role
    String wsPath;
    switch (role) {
      case 'driver':
        wsPath = '/api/v1/ws/driver/$userId';
        break;
      case 'helper':
        wsPath = '/api/v1/ws/helper/$userId';
        break;
      case 'doctor':
      default:
        wsPath = '/api/v1/ws/doctor/$userId';
        break;
    }

    // Use deployed server for WebSockets
    String wsUrl = 'wss://sanjeeeveni.onrender.com$wsPath';

    try {
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _channel!.stream.listen(
        (message) {
          _reconnectAttempts = 0;
          try {
            final data = jsonDecode(message as String) as Map<String, dynamic>;
            _messageController.add(data);
          } catch (e) {
            debugPrint('Error parsing WS message: $e');
          }
        },
        onDone: () {
          debugPrint('WebSocket closed ($role)');
          _scheduleReconnect();
        },
        onError: (error) {
          debugPrint('WebSocket error ($role): $error');
          _scheduleReconnect();
        },
      );
      _isConnecting = false;
      debugPrint('WebSocket connected: $role/$userId');
    } catch (e) {
      _isConnecting = false;
      debugPrint('WebSocket connect error ($role): $e');
      _scheduleReconnect();
    }
  }

  /// Legacy connect method for backward compatibility (defaults to doctor role).
  void connectDoctor(String doctorId) => connect(doctorId, role: 'doctor');

  /// Connect as a driver to receive task assignments.
  void connectDriver(String driverId) => connect(driverId, role: 'driver');

  /// Connect as a helper to receive SOS alerts.
  void connectHelper(String helperId) => connect(helperId, role: 'helper');

  void _disconnectInternal() {
    _reconnectTimer?.cancel();
    _channel?.sink.close(status.goingAway);
    _channel = null;
  }

  void disconnect() {
    _disconnectInternal();
    _userId = null;
    _role = null;
  }

  void sendMessage(Map<String, dynamic> data) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode(data));
    }
  }

  // ─── Doctor-specific messages ─────────────────────────────

  void initiateCall(String sosId) {
    sendMessage({
      'type': 'INITIATE_CALL',
      'sos_id': sosId,
    });
  }

  // ─── Driver-specific messages ─────────────────────────────

  /// Driver sends current GPS location to the server for patient tracking.
  void sendLocationUpdate(String sosId, double latitude, double longitude) {
    sendMessage({
      'type': 'LOCATION_UPDATE',
      'sos_id': sosId,
      'latitude': latitude,
      'longitude': longitude,
    });
  }

  /// Driver accepts a pending task via WebSocket.
  void sendTaskAccepted(String sosId) {
    sendMessage({
      'type': 'TASK_ACCEPTED',
      'sos_id': sosId,
      'message': 'Driver accepted the task and is en route.',
    });
  }

  /// Driver rejects a pending task via WebSocket.
  void sendTaskRejected(String sosId) {
    sendMessage({
      'type': 'TASK_REJECTED',
      'sos_id': sosId,
      'message': 'Driver rejected the task.',
    });
  }

  /// Driver marks task as completed via WebSocket.
  void sendTaskCompleted(String sosId) {
    sendMessage({
      'type': 'TASK_COMPLETED',
      'sos_id': sosId,
      'message': 'Driver completed the pickup.',
    });
  }

  // ─── Helper-specific messages ─────────────────────────────

  /// Helper accepts an SOS alert via WebSocket.
  void sendAlertAccepted(String sosId) {
    sendMessage({
      'type': 'ALERT_ACCEPTED',
      'sos_id': sosId,
      'message': 'Helper accepted the alert and is en route.',
    });
  }

  /// Helper rejects an SOS alert via WebSocket.
  void sendAlertRejected(String sosId) {
    sendMessage({
      'type': 'ALERT_REJECTED',
      'sos_id': sosId,
      'message': 'Helper rejected the alert.',
    });
  }

  void _scheduleReconnect() {
    if (_userId == null || _isConnecting) return;
    
    if (_reconnectAttempts >= 5) {
      debugPrint('Max reconnect attempts reached');
      return;
    }

    _reconnectTimer?.cancel();
    final delay = Duration(seconds: (1 << _reconnectAttempts)); // Exponential backoff
    _reconnectAttempts++;
    
    _reconnectTimer = Timer(delay, () {
      if (_userId != null && _role != null) {
        debugPrint('Attempting to reconnect ($_role)...');
        connect(_userId!, role: _role!);
      }
    });
  }
}
