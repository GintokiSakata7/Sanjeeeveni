import { wsService } from './websocketService';

class WebRTCService {
  constructor() {
    this.peerConnection = null;
    this.localStream = null;
    this.remoteStream = null;
    this.doctorId = null;
    this.onRemoteStreamAdd = null;
    
    this.config = {
      iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' }
      ]
    };
  }

  async initialize(doctorId, remoteOffer) {
    this.doctorId = doctorId;
    
    // Get local microphone access
    try {
      this.localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
    } catch (err) {
      console.error('Error accessing microphone:', err);
      throw new Error('Microphone access denied or unavailable.');
    }

    this.peerConnection = new RTCPeerConnection(this.config);

    // Add local tracks to peer connection
    this.localStream.getTracks().forEach(track => {
      this.peerConnection.addTrack(track, this.localStream);
    });

    // Handle incoming remote stream
    this.peerConnection.ontrack = (event) => {
      this.remoteStream = event.streams[0];
      if (this.onRemoteStreamAdd) {
        this.onRemoteStreamAdd(this.remoteStream);
      }
    };

    // Handle ICE candidates
    this.peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        wsService.send({
          type: 'ICE_CANDIDATE',
          doctor_id: this.doctorId,
          candidate: event.candidate
        });
      }
    };

    // Connection state changes
    this.peerConnection.onconnectionstatechange = () => {
      console.log('WebRTC State:', this.peerConnection.connectionState);
    };

    // Handle the remote offer
    if (remoteOffer) {
      await this.peerConnection.setRemoteDescription(new RTCSessionDescription(remoteOffer));
      
      // Create answer
      const answer = await this.peerConnection.createAnswer();
      await this.peerConnection.setLocalDescription(answer);
      
      // Send answer back to doctor
      wsService.send({
        type: 'CALL_ANSWER',
        doctor_id: this.doctorId,
        sdp: answer
      });
    }

    // Listen for ICE candidates from the doctor
    this._iceCandidateHandler = (data) => {
      if (data.candidate && this.peerConnection) {
        this.peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate))
          .catch(e => console.error('Error adding received ice candidate', e));
      }
    };
    wsService.on('ICE_CANDIDATE', this._iceCandidateHandler);
  }

  toggleMute() {
    if (this.localStream) {
      const audioTracks = this.localStream.getAudioTracks();
      if (audioTracks.length > 0) {
        const isMuted = !audioTracks[0].enabled;
        audioTracks[0].enabled = isMuted; // Toggle
        return !isMuted; // return new muted state
      }
    }
    return false;
  }

  endCall() {
    if (this.peerConnection) {
      this.peerConnection.close();
      this.peerConnection = null;
    }
    
    if (this.localStream) {
      this.localStream.getTracks().forEach(track => track.stop());
      this.localStream = null;
    }
    
    if (this.doctorId) {
      wsService.send({
        type: 'CALL_END',
        doctor_id: this.doctorId
      });
    }
    
    if (this._iceCandidateHandler) {
      wsService.off('ICE_CANDIDATE', this._iceCandidateHandler);
      this._iceCandidateHandler = null;
    }
    
    this.remoteStream = null;
    this.doctorId = null;
  }
}

export const rtcService = new WebRTCService();
