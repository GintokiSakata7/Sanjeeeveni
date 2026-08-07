import React, { useEffect, useState, useRef } from 'react';
import { wsService } from '../services/websocketService';
import IncomingCallModal from './IncomingCallModal';
import { fetchWithFallback } from '../services/apiClient';

const STATUS_STEPS = [
  { key: 'PENDING',         icon: '📡', label: 'SOS Signal Sent — Awaiting Hospital Response', color: 'amber' },
  { key: 'ACCEPTED',        icon: '✅', label: 'Hospital Accepted Emergency Case',             color: 'emerald' },
  { key: 'DOCTOR_ASSIGNED', icon: '👨‍⚕️', label: 'Doctor Assigned to Your Case',              color: 'blue' },
  { key: 'DOCTOR_ACCEPTED', icon: '🩺', label: 'Doctor Confirmed — Ready to Contact You',     color: 'cyan' },
  { key: 'DISPATCHED',      icon: '🚑', label: 'Ambulance Dispatched En Route',               color: 'indigo' },
  { key: 'ARRIVED',         icon: '🏥', label: 'Ambulance Has Arrived',                       color: 'green' },
];

const STATUS_ORDER = STATUS_STEPS.map(s => s.key);

const colorMap = {
  amber:   { bg: 'rgba(245,158,11,0.15)',  border: 'rgba(245,158,11,0.5)',  text: '#fde68a' },
  emerald: { bg: 'rgba(52,211,153,0.15)',  border: 'rgba(52,211,153,0.5)',  text: '#a7f3d0' },
  blue:    { bg: 'rgba(59,130,246,0.15)',  border: 'rgba(59,130,246,0.5)',  text: '#bfdbfe' },
  cyan:    { bg: 'rgba(34,211,238,0.15)',  border: 'rgba(34,211,238,0.5)',  text: '#a5f3fc' },
  indigo:  { bg: 'rgba(99,102,241,0.15)', border: 'rgba(99,102,241,0.5)',  text: '#c7d2fe' },
  green:   { bg: 'rgba(74,222,128,0.15)', border: 'rgba(74,222,128,0.5)',  text: '#bbf7d0' },
};

const LiveSOSTracker = ({ sosId }) => {
  const [currentStatus, setCurrentStatus] = useState('PENDING');
  const [messages, setMessages]           = useState([]);
  const [doctorInfo, setDoctorInfo]       = useState(null);
  const [ambulanceInfo, setAmbulanceInfo] = useState(null);
  const [incomingCall, setIncomingCall]   = useState(null);
  const [callActive, setCallActive]       = useState(false);
  const doctorInfoRef = useRef(null);

  // ── Hydrate state from DB on mount ──────────────────────────────
  useEffect(() => {
    if (!sosId) return;

    const loadInitialState = async () => {
      try {
        const res = await fetchWithFallback(`/api/v1/routing/status/${sosId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.status) setCurrentStatus(data.status);
          if (data.assigned_doctor_name) {
            const info = { name: data.assigned_doctor_name, specialty: 'Emergency Physician' };
            setDoctorInfo(info);
            doctorInfoRef.current = info;
          }
          if (data.assigned_driver_name || data.assigned_ambulance_reg) {
            setAmbulanceInfo({
              driver: data.assigned_driver_name || 'Driver',
              reg:    data.assigned_ambulance_reg || 'N/A',
            });
          }
        }
      } catch (_) {
        // silently fail
      }
    };

    loadInitialState();
  }, [sosId]);

  // ── WebSocket real-time updates ──────────────────────────────────
  useEffect(() => {
    if (!sosId) return;

    wsService.connect(sosId);

    const addMsg = (text) =>
      setMessages(prev => [...prev, { time: new Date().toLocaleTimeString(), text }]);

    const handleStatusUpdate = (data) => {
      if (data.status) setCurrentStatus(data.status);
      if (data.message) addMsg(data.message);
    };

    const handleDoctorAssigned = (data) => {
      const info = { name: data.doctor_name, specialty: data.doctor_specialty || 'Emergency Physician' };
      setDoctorInfo(info);
      doctorInfoRef.current = info;
      setCurrentStatus(prev =>
        STATUS_ORDER.indexOf('DOCTOR_ASSIGNED') > STATUS_ORDER.indexOf(prev) ? 'DOCTOR_ASSIGNED' : prev
      );
      if (data.message) addMsg(data.message);
    };

    const handleDriverDispatched = (data) => {
      setAmbulanceInfo({ driver: data.driver_name, reg: data.ambulance_reg });
      setCurrentStatus(prev =>
        STATUS_ORDER.indexOf('DISPATCHED') > STATUS_ORDER.indexOf(prev) ? 'DISPATCHED' : prev
      );
      if (data.message) addMsg(data.message);
    };

    const handleDriverEnRoute = (data) => {
      if (data.message) addMsg(data.message);
    };

    const handleIncomingCall = (data) => {
      setIncomingCall({
        doctor_id: data.doctor_id,
        sdp:       data.sdp,
        name:      data.name || doctorInfoRef.current?.name || 'Assigned Doctor',
      });
    };

    const handleCallEnded = () => {
      setCallActive(false);
      setIncomingCall(null);
    };

    wsService.on('STATUS_UPDATE',      handleStatusUpdate);
    wsService.on('DOCTOR_ASSIGNED',    handleDoctorAssigned);
    wsService.on('DRIVER_DISPATCHED',  handleDriverDispatched);
    wsService.on('DRIVER_EN_ROUTE',    handleDriverEnRoute);
    wsService.on('INITIATE_CALL',      handleIncomingCall);
    wsService.on('CALL_END',           handleCallEnded);

    return () => {
      wsService.off('STATUS_UPDATE',     handleStatusUpdate);
      wsService.off('DOCTOR_ASSIGNED',   handleDoctorAssigned);
      wsService.off('DRIVER_DISPATCHED', handleDriverDispatched);
      wsService.off('DRIVER_EN_ROUTE',   handleDriverEnRoute);
      wsService.off('INITIATE_CALL',     handleIncomingCall);
      wsService.off('CALL_END',          handleCallEnded);
      wsService.disconnect();
    };
  }, [sosId]);

  const currentIdx = STATUS_ORDER.indexOf(currentStatus);

  return (
    <div style={{
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      border: '1px solid #334155',
      borderRadius: '16px',
      padding: '24px',
      marginTop: '24px',
      color: '#e2e8f0',
      fontFamily: "'Inter', sans-serif",
    }}>
      {/* Header */}
      <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
        <span style={{ position: 'relative', display: 'inline-flex' }}>
          <span style={{
            position: 'absolute', display: 'inline-flex', height: '12px', width: '12px',
            borderRadius: '50%', background: '#ef4444', opacity: 0.75,
            animation: 'ping 1s cubic-bezier(0,0,0.2,1) infinite'
          }} />
          <span style={{ position: 'relative', display: 'inline-flex', height: '12px', width: '12px', borderRadius: '50%', background: '#ef4444' }} />
        </span>
        Live Emergency Tracking
      </h3>

      {/* Status Steps */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '20px' }}>
        {STATUS_STEPS.map((step, idx) => {
          const isActive  = idx === currentIdx;
          const isPast    = idx < currentIdx;
          const isFuture  = idx > currentIdx;
          const colors    = colorMap[step.color];

          return (
            <div key={step.key} style={{
              padding: '12px 16px',
              borderRadius: '10px',
              border: `1px solid ${(isActive || isPast) ? colors.border : '#334155'}`,
              background: isActive ? colors.bg : (isPast ? 'rgba(30,41,59,0.6)' : 'transparent'),
              color: (isActive || isPast) ? colors.text : '#475569',
              opacity: isFuture ? 0.5 : 1,
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              transition: 'all 0.4s ease',
            }}>
              <span style={{ fontSize: '18px', minWidth: '24px' }}>{step.icon}</span>
              <span style={{ fontSize: '14px', fontWeight: isActive ? 600 : 400 }}>{step.label}</span>
              {isPast && <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#34d399' }}>✓</span>}
              {isActive && <span style={{ marginLeft: 'auto', fontSize: '12px', color: '#facc15', animation: 'pulse 2s infinite' }}>● Live</span>}
            </div>
          );
        })}
      </div>

      {/* Doctor & Ambulance info cards */}
      {doctorInfo && (
        <div style={{ display: 'flex', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, padding: '12px', background: 'rgba(59,130,246,0.1)', border: '1px solid rgba(59,130,246,0.3)', borderRadius: '10px' }}>
            <p style={{ margin: 0, fontSize: '12px', color: '#93c5fd' }}>Assigned Doctor</p>
            <p style={{ margin: '4px 0 0', fontWeight: 700, color: '#fff' }}>Dr. {doctorInfo.name}</p>
            <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#93c5fd' }}>{doctorInfo.specialty}</p>
          </div>
        </div>
      )}

      {ambulanceInfo && (
        <div style={{ display: 'flex', gap: '10px', marginBottom: '16px', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, padding: '12px', background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.3)', borderRadius: '10px' }}>
            <p style={{ margin: 0, fontSize: '12px', color: '#a5b4fc' }}>Ambulance Dispatched</p>
            <p style={{ margin: '4px 0 0', fontWeight: 700, color: '#fff' }}>{ambulanceInfo.reg}</p>
            <p style={{ margin: '2px 0 0', fontSize: '12px', color: '#a5b4fc' }}>Driver: {ambulanceInfo.driver}</p>
          </div>
        </div>
      )}

      {/* Timeline messages */}
      {messages.length > 0 && (
        <div style={{ borderTop: '1px solid #1e293b', paddingTop: '16px' }}>
          <h4 style={{ fontSize: '12px', fontWeight: 600, color: '#64748b', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Timeline Updates
          </h4>
          <div style={{ maxHeight: '120px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {messages.map((m, i) => (
              <div key={i} style={{ display: 'flex', gap: '12px', fontSize: '13px' }}>
                <span style={{ color: '#475569', minWidth: '72px' }}>{m.time}</span>
                <span style={{ color: '#cbd5e1' }}>{m.text}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Incoming Call Modal */}
      {incomingCall && !callActive && (
        <IncomingCallModal
          callInfo={incomingCall}
          onAccept={() => { setCallActive(true); setIncomingCall(null); }}
          onReject={() => setIncomingCall(null)}
        />
      )}

      {callActive && (
        <IncomingCallModal
          callInfo={{ doctor_id: doctorInfo?.name || 'Doctor', name: doctorInfo?.name || 'Your Doctor' }}
          isActive={true}
          onEnd={() => setCallActive(false)}
        />
      )}
    </div>
  );
};

export default LiveSOSTracker;
