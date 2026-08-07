import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'websocket_service.dart';

class WebRTCCallService {
  static final WebRTCCallService _instance = WebRTCCallService._internal();
  factory WebRTCCallService() => _instance;
  WebRTCCallService._internal();

  RTCPeerConnection? _peerConnection;
  MediaStream? _localStream;
  MediaStream? _remoteStream;
  String? _currentSosId;
  StreamSubscription? _wsSubscription;
  
  Function(MediaStream stream)? onRemoteStreamAdd;
  Function()? onCallEnded;

  final Map<String, dynamic> _configuration = {
    'iceServers': [
      {'urls': 'stun:stun.l.google.com:19302'},
      {'urls': 'stun:stun1.l.google.com:19302'},
    ]
  };

  Future<void> initiateCall(String sosId) async {
    _currentSosId = sosId;
    
    // Listen for WebRTC signals from WS
    _wsSubscription = WebSocketService().messageStream.listen((data) {
      final type = data['type'];
      if (type == 'CALL_ANSWER' && data['sdp'] != null) {
        _handleAnswer(data['sdp']);
      } else if (type == 'ICE_CANDIDATE' && data['candidate'] != null) {
        _handleIceCandidate(data['candidate']);
      } else if (type == 'CALL_REJECT' || type == 'CALL_END') {
        endCall(sendSignal: false);
      }
    });

    try {
      _localStream = await navigator.mediaDevices.getUserMedia({
        'audio': true,
        'video': false,
      });

      _peerConnection = await createPeerConnection(_configuration);
      
      _localStream!.getTracks().forEach((track) {
        _peerConnection!.addTrack(track, _localStream!);
      });

      _peerConnection!.onTrack = (RTCTrackEvent event) {
        if (event.streams.isNotEmpty) {
          _remoteStream = event.streams[0];
          if (onRemoteStreamAdd != null) {
            onRemoteStreamAdd!(_remoteStream!);
          }
        }
      };

      _peerConnection!.onIceCandidate = (RTCIceCandidate candidate) {
        WebSocketService().sendMessage({
          'type': 'ICE_CANDIDATE',
          'sos_id': _currentSosId,
          'candidate': {
            'candidate': candidate.candidate,
            'sdpMid': candidate.sdpMid,
            'sdpMLineIndex': candidate.sdpMLineIndex
          }
        });
      };

      RTCSessionDescription offer = await _peerConnection!.createOffer();
      await _peerConnection!.setLocalDescription(offer);

      WebSocketService().sendMessage({
        'type': 'INITIATE_CALL',
        'sos_id': _currentSosId,
        'sdp': {
          'type': offer.type,
          'sdp': offer.sdp,
        }
      });
    } catch (e) {
      debugPrint('Error initiating call: $e');
      endCall();
    }
  }

  Future<void> _handleAnswer(Map<String, dynamic> sdpMap) async {
    if (_peerConnection != null) {
      try {
        await _peerConnection!.setRemoteDescription(
          RTCSessionDescription(sdpMap['sdp'], sdpMap['type'])
        );
      } catch (e) {
        debugPrint('Error setting remote description: $e');
      }
    }
  }

  Future<void> _handleIceCandidate(Map<String, dynamic> candidateMap) async {
    if (_peerConnection != null) {
      try {
        await _peerConnection!.addCandidate(
          RTCIceCandidate(
            candidateMap['candidate'],
            candidateMap['sdpMid'],
            candidateMap['sdpMLineIndex']
          )
        );
      } catch (e) {
        debugPrint('Error adding ICE candidate: $e');
      }
    }
  }

  bool toggleMute() {
    if (_localStream != null) {
      final audioTracks = _localStream!.getAudioTracks();
      if (audioTracks.isNotEmpty) {
        final isEnabled = audioTracks[0].enabled;
        audioTracks[0].enabled = !isEnabled;
        return !isEnabled; // Return new muted state
      }
    }
    return false;
  }

  bool toggleSpeaker() {
    // Note: flutter_webrtc speaker toggle is platform-specific and often requires helper plugins
    // For this prototype, we'll try to use the built-in media stream track manipulation
    if (_localStream != null) {
      Helper.setSpeakerphoneOn(!_isSpeakerOn);
      _isSpeakerOn = !_isSpeakerOn;
      return _isSpeakerOn;
    }
    return true;
  }
  
  bool _isSpeakerOn = true;

  void endCall({bool sendSignal = true}) {
    if (sendSignal && _currentSosId != null) {
      WebSocketService().sendMessage({
        'type': 'CALL_END',
        'sos_id': _currentSosId
      });
    }

    _peerConnection?.close();
    _peerConnection = null;

    if (_localStream != null) {
      for (var track in _localStream!.getTracks()) {
        track.stop();
      }
      _localStream = null;
    }

    _remoteStream = null;
    _currentSosId = null;
    _isSpeakerOn = true;
    
    _wsSubscription?.cancel();
    _wsSubscription = null;
    
    if (onCallEnded != null) {
      onCallEnded!();
    }
  }
}
