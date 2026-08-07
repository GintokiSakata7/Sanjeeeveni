import React, { useEffect, useState } from 'react';
import { wsService } from '../services/websocketService';
import IncomingCallModal from './IncomingCallModal';

const LiveSOSTracker = ({ sosId }) => {
  const [status, setStatus] = useState('PENDING');
  const [messages, setMessages] = useState([]);
  const [doctorInfo, setDoctorInfo] = useState(null);
  const [ambulanceInfo, setAmbulanceInfo] = useState(null);
  
  const [incomingCall, setIncomingCall] = useState(null); // { doctor_id, sdp }
  const [callActive, setCallActive] = useState(false);

  useEffect(() => {
    if (!sosId) return;

    wsService.connect(sosId);

    const handleStatusUpdate = (data) => {
      setStatus(data.status);
      if (data.message) {
        setMessages(prev => [...prev, { time: new Date().toLocaleTimeString(), text: data.message }]);
      }
    };

    const handleDoctorAssigned = (data) => {
      setDoctorInfo({ name: data.doctor_name, specialty: data.doctor_specialty });
      if (data.message) {
        setMessages(prev => [...prev, { time: new Date().toLocaleTimeString(), text: data.message }]);
      }
    };

    const handleDriverDispatched = (data) => {
      setAmbulanceInfo({ driver: data.driver_name, reg: data.ambulance_reg });
      if (data.message) {
        setMessages(prev => [...prev, { time: new Date().toLocaleTimeString(), text: data.message }]);
      }
    };

    const handleIncomingCall = (data) => {
      setIncomingCall({
        doctor_id: data.doctor_id,
        sdp: data.sdp,
        name: doctorInfo?.name || 'Assigned Doctor'
      });
    };

    const handleCallEnded = () => {
      setCallActive(false);
      setIncomingCall(null);
    };

    wsService.on('STATUS_UPDATE', handleStatusUpdate);
    wsService.on('DOCTOR_ASSIGNED', handleDoctorAssigned);
    wsService.on('DRIVER_DISPATCHED', handleDriverDispatched);
    wsService.on('INITIATE_CALL', handleIncomingCall);
    wsService.on('CALL_END', handleCallEnded);

    return () => {
      wsService.off('STATUS_UPDATE', handleStatusUpdate);
      wsService.off('DOCTOR_ASSIGNED', handleDoctorAssigned);
      wsService.off('DRIVER_DISPATCHED', handleDriverDispatched);
      wsService.off('INITIATE_CALL', handleIncomingCall);
      wsService.off('CALL_END', handleCallEnded);
      wsService.disconnect();
    };
  }, [sosId, doctorInfo]);

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl p-6 mt-6 animate-fade-in text-white">
      <h3 className="text-xl font-bold mb-4 flex items-center">
        <span className="relative flex h-3 w-3 mr-3">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
        </span>
        Live SOS Tracking
      </h3>
      
      <div className="mb-6 flex flex-col space-y-3">
        <div className={`p-3 rounded-lg border ${status === 'PENDING' ? 'bg-amber-900/30 border-amber-500/50 text-amber-200' : 'bg-slate-800 border-slate-700 text-slate-400'}`}>
          📡 SOS Signal Sent. Awaiting Hospital Response...
        </div>
        
        <div className={`p-3 rounded-lg border ${status === 'ACCEPTED' ? 'bg-emerald-900/30 border-emerald-500/50 text-emerald-200' : (status !== 'PENDING' ? 'bg-slate-800 border-slate-700 text-slate-400' : 'opacity-40')}`}>
          ✅ Hospital Accepted Emergency Case
        </div>

        {doctorInfo && (
          <div className="p-3 rounded-lg border bg-blue-900/30 border-blue-500/50 text-blue-200 animate-slide-up">
            👨‍⚕️ Dr. {doctorInfo.name} ({doctorInfo.specialty}) assigned to your case.
          </div>
        )}

        {ambulanceInfo && (
          <div className="p-3 rounded-lg border bg-indigo-900/30 border-indigo-500/50 text-indigo-200 animate-slide-up">
            🚑 Ambulance {ambulanceInfo.reg} dispatched (Driver: {ambulanceInfo.driver})
          </div>
        )}
      </div>

      <div className="border-t border-slate-700 pt-4">
        <h4 className="text-sm font-semibold text-slate-400 mb-2">Timeline Updates</h4>
        <div className="max-h-32 overflow-y-auto space-y-2 text-sm text-slate-300">
          {messages.length === 0 && <span className="text-slate-500 italic">Waiting for updates...</span>}
          {messages.map((m, i) => (
            <div key={i} className="flex">
              <span className="text-slate-500 w-20">{m.time}</span>
              <span>{m.text}</span>
            </div>
          ))}
        </div>
      </div>

      {incomingCall && !callActive && (
        <IncomingCallModal 
          callInfo={incomingCall} 
          onAccept={() => {
            setCallActive(true);
            setIncomingCall(null);
          }}
          onReject={() => {
            setIncomingCall(null);
          }}
        />
      )}
      
      {callActive && (
         <IncomingCallModal 
           callInfo={{ doctor_id: doctorInfo?.name || 'Doctor' }}
           isActive={true}
           onEnd={() => setCallActive(false)}
         />
      )}
    </div>
  );
};

export default LiveSOSTracker;
