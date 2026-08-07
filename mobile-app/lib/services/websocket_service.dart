import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/status.dart' as status;
import 'api_service.dart';

class WebSocketService {
  static final WebSocketService _instance = WebSocketService._internal();
  factory WebSocketService() => _instance;
  WebSocketService._internal();

  WebSocketChannel? _channel;
  StreamController<Map<String, dynamic>> _messageController = StreamController<Map<String, dynamic>>.broadcast();
  String? _doctorId;
  Timer? _reconnectTimer;
  int _reconnectAttempts = 0;
  bool _isConnecting = false;

  Stream<Map<String, dynamic>> get messageStream => _messageController.stream;

  void connect(String doctorId) {
    if (_isConnecting) return;
    
    if (_channel != null && _doctorId == doctorId) {
      return; // Already connected
    }
    
    _doctorId = doctorId;
    _isConnecting = true;
    _disconnectInternal();

    // Use deployed server for WebSockets per user request
    String wsUrl = 'wss://sanjeeeveni.onrender.com/api/v1/ws/doctor/$doctorId';

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
          debugPrint('WebSocket closed');
          _scheduleReconnect();
        },
        onError: (error) {
          debugPrint('WebSocket error: $error');
          _scheduleReconnect();
        },
      );
      _isConnecting = false;
    } catch (e) {
      _isConnecting = false;
      debugPrint('WebSocket connect error: $e');
      _scheduleReconnect();
    }
  }

  void _disconnectInternal() {
    _reconnectTimer?.cancel();
    _channel?.sink.close(status.goingAway);
    _channel = null;
  }

  void disconnect() {
    _disconnectInternal();
    _doctorId = null;
  }

  void sendMessage(Map<String, dynamic> data) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode(data));
    }
  }

  void initiateCall(String sosId) {
    sendMessage({
      'type': 'INITIATE_CALL',
      'sos_id': sosId,
    });
  }

  void _scheduleReconnect() {
    if (_doctorId == null || _isConnecting) return;
    
    if (_reconnectAttempts >= 5) {
      debugPrint('Max reconnect attempts reached');
      return;
    }

    _reconnectTimer?.cancel();
    final delay = Duration(seconds: (1 << _reconnectAttempts)); // Exponential backoff
    _reconnectAttempts++;
    
    _reconnectTimer = Timer(delay, () {
      if (_doctorId != null) {
        debugPrint('Attempting to reconnect...');
        connect(_doctorId!);
      }
    });
  }
}
