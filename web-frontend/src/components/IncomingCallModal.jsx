import React, { useEffect, useState, useRef } from 'react';
import { rtcService } from '../services/webrtcService';
import { wsService } from '../services/websocketService';

const IncomingCallModal = ({ callInfo, onAccept, onReject, isActive, onEnd }) => {
  const [duration, setDuration] = useState(0);
  const [isMuted, setIsMuted] = useState(false);
  const remoteAudioRef = useRef(null);

  useEffect(() => {
    if (isActive) {
      if (rtcService.remoteStream && remoteAudioRef.current) {
        remoteAudioRef.current.srcObject = rtcService.remoteStream;
      }
      rtcService.onRemoteStreamAdd = (stream) => {
        if (remoteAudioRef.current) {
          remoteAudioRef.current.srcObject = stream;
        }
      };

      const timer = setInterval(() => setDuration(d => d + 1), 1000);
      return () => clearInterval(timer);
    }
  }, [isActive]);

  const handleAccept = async () => {
    try {
      await rtcService.initialize(callInfo.doctor_id, callInfo.sdp);
      onAccept();
    } catch (e) {
      console.error('Failed to accept call', e);
      alert('Could not access microphone.');
      handleReject();
    }
  };

  const handleReject = () => {
    wsService.send({ type: 'CALL_REJECT', doctor_id: callInfo.doctor_id });
    if (onReject) onReject();
  };

  const handleEnd = () => {
    rtcService.endCall();
    if (onEnd) onEnd();
  };

  const handleMute = () => {
    const muted = rtcService.toggleMute();
    setIsMuted(muted);
  };

  const formatDuration = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 rounded-3xl p-8 w-full max-w-sm flex flex-col items-center text-white shadow-2xl shadow-blue-900/20">
        
        <div className="w-24 h-24 bg-blue-900/50 rounded-full border-2 border-blue-500 flex items-center justify-center mb-6 relative">
          {!isActive && (
            <>
              <div className="absolute inset-0 rounded-full border border-blue-400 animate-ping opacity-75"></div>
              <div className="absolute -inset-4 rounded-full border border-blue-400 animate-ping opacity-30 animation-delay-300"></div>
            </>
          )}
          <span className="text-4xl">👨‍⚕️</span>
        </div>

        <h2 className="text-2xl font-bold mb-1">{isActive ? 'Connected' : 'Incoming Call'}</h2>
        <p className="text-slate-400 mb-8">{callInfo.name || 'Emergency Doctor'}</p>

        {isActive ? (
          <>
            <div className="text-xl font-mono text-emerald-400 mb-8">
              {formatDuration(duration)}
            </div>
            
            <audio ref={remoteAudioRef} autoPlay />

            <div className="flex gap-6">
              <button 
                onClick={handleMute}
                className={`w-14 h-14 rounded-full flex items-center justify-center transition-colors ${isMuted ? 'bg-slate-700 text-slate-300' : 'bg-slate-800 text-white hover:bg-slate-700'}`}
              >
                {isMuted ? '🔇' : '🎤'}
              </button>
              
              <button 
                onClick={handleEnd}
                className="w-14 h-14 rounded-full bg-red-600 hover:bg-red-500 flex items-center justify-center transition-colors text-xl"
              >
                📞
              </button>
            </div>
          </>
        ) : (
          <div className="flex gap-8">
            <button 
              onClick={handleReject}
              className="w-16 h-16 rounded-full bg-red-600/20 border-2 border-red-600 text-red-500 hover:bg-red-600 hover:text-white flex items-center justify-center transition-colors text-2xl"
            >
              ✕
            </button>
            <button 
              onClick={handleAccept}
              className="w-16 h-16 rounded-full bg-emerald-600 border-2 border-emerald-500 hover:bg-emerald-500 flex items-center justify-center transition-colors text-2xl shadow-lg shadow-emerald-900/50"
            >
              📞
            </button>
          </div>
        )}
        
      </div>
    </div>
  );
};

export default IncomingCallModal;
