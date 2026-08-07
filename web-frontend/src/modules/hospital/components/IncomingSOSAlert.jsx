import React, { useState } from 'react';
import { AlertTriangle, MapPin, Activity, Stethoscope, User, Image as ImageIcon, Check, X, Car, Loader } from 'lucide-react';

export default function IncomingSOSAlert({ sosRequest, availableDrivers, availableDoctors, onAccept, onReject, isSubmitting }) {
  const [selectedDriverId, setSelectedDriverId] = useState('');
  const [selectedDoctorId, setSelectedDoctorId] = useState('');

  if (!sosRequest) return null;

  const canSubmit = selectedDriverId && selectedDoctorId && !isSubmitting;

  return (
    <div className="hms-modal-overlay" style={{ zIndex: 9999, backgroundColor: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(4px)' }}>
      <div className="hms-modal-card" style={{ border: '2px solid #ef4444', boxShadow: '0 0 60px rgba(239, 68, 68, 0.4)', maxWidth: '600px', animation: 'pulse-border 2s infinite' }}>
        
        <div className="modal-head" style={{ borderBottom: '1px solid rgba(239, 68, 68, 0.3)', backgroundColor: 'rgba(239, 68, 68, 0.1)' }}>
          <h3 style={{ color: '#ef4444', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertTriangle className="animate-pulse" size={24} /> INCOMING EMERGENCY (SOS)
          </h3>
        </div>

        <div className="modal-form" style={{ padding: '20px' }}>
          <p style={{ color: '#94a3b8', marginBottom: '20px' }}>Radar sweep has routed a distress signal to your facility.</p>
          
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px', marginBottom: '20px' }}>
            <div style={{ backgroundColor: '#0f1523', padding: '15px', borderRadius: '8px', border: '1px solid #1e293b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8', marginBottom: '5px' }}>
                <Activity size={16} color="#fb923c" />
                <span style={{ fontSize: '12px' }}>Triage Urgency</span>
              </div>
              <strong style={{ color: sosRequest.triage_urgency?.includes('RED') ? '#ef4444' : '#facc15', fontSize: '16px' }}>
                {sosRequest.triage_urgency}
              </strong>
            </div>

            <div style={{ backgroundColor: '#0f1523', padding: '15px', borderRadius: '8px', border: '1px solid #1e293b' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8', marginBottom: '5px' }}>
                <MapPin size={16} color="#60a5fa" />
                <span style={{ fontSize: '12px' }}>Location</span>
              </div>
              <strong style={{ color: '#fff', fontSize: '16px' }}>
                {sosRequest.citizen_lat?.toFixed(4)}, {sosRequest.citizen_lng?.toFixed(4)}
              </strong>
            </div>
            
            <div style={{ backgroundColor: '#0f1523', padding: '15px', borderRadius: '8px', border: '1px solid #1e293b', gridColumn: '1 / -1' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8', marginBottom: '5px' }}>
                <User size={16} color="#34d399" />
                <span style={{ fontSize: '12px' }}>Distress Transcript</span>
              </div>
              <p style={{ color: '#cbd5e1', fontStyle: 'italic', margin: 0 }}>"{sosRequest.transcript}"</p>
            </div>

            {sosRequest.image_url && (
               <div style={{ backgroundColor: '#0f1523', padding: '15px', borderRadius: '8px', border: '1px solid #1e293b', gridColumn: '1 / -1' }}>
                 <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8', marginBottom: '10px' }}>
                   <ImageIcon size={16} color="#c084fc" />
                   <span style={{ fontSize: '12px' }}>Attached Image</span>
                 </div>
                 <img src={sosRequest.image_url} alt="Emergency Situation" style={{ width: '100%', borderRadius: '8px', maxHeight: '200px', objectFit: 'cover' }} />
               </div>
            )}
          </div>
          
          {/* ASSIGN DRIVER */}
          <div className="form-field" style={{ marginBottom: '15px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8' }}>
              <Car size={16} color="#2dd4bf" />
              Assign Driver
              {availableDrivers.length === 0 && (
                <span style={{ fontSize: '11px', color: '#ef4444', marginLeft: '8px' }}>⚠ No available drivers</span>
              )}
            </label>
            <select
              value={selectedDriverId}
              onChange={(e) => setSelectedDriverId(e.target.value)}
              disabled={isSubmitting}
              style={{ width: '100%', backgroundColor: '#1a2332', color: 'white', padding: '10px', borderRadius: '8px', border: `1px solid ${selectedDriverId ? '#2dd4bf' : '#334155'}` }}
            >
              <option value="">-- Select available driver --</option>
              {availableDrivers.map(drv => (
                <option key={drv.id} value={drv.id}>
                  🚑 {drv.name} ({drv.contact_number || drv.email})
                </option>
              ))}
            </select>
          </div>

          {/* ASSIGN DOCTOR */}
          <div className="form-field">
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#94a3b8' }}>
              <Stethoscope size={16} color="#fb7185" />
              Assign Doctor
              {availableDoctors.length === 0 && (
                <span style={{ fontSize: '11px', color: '#ef4444', marginLeft: '8px' }}>⚠ No available doctors</span>
              )}
            </label>
            <select
              value={selectedDoctorId}
              onChange={(e) => setSelectedDoctorId(e.target.value)}
              disabled={isSubmitting}
              style={{ width: '100%', backgroundColor: '#1a2332', color: 'white', padding: '10px', borderRadius: '8px', border: `1px solid ${selectedDoctorId ? '#fb7185' : '#334155'}` }}
            >
              <option value="">-- Select available doctor --</option>
              {availableDoctors.map(doc => (
                <option key={doc.id} value={doc.id}>
                  👨‍⚕️ Dr. {doc.name} — {doc.specialization}
                </option>
              ))}
            </select>
          </div>

          {/* Validation hint */}
          {(!selectedDriverId || !selectedDoctorId) && !isSubmitting && (
            <p style={{ fontSize: '12px', color: '#64748b', marginTop: '10px', textAlign: 'center' }}>
              Select both a driver and a doctor to accept the emergency.
            </p>
          )}
        </div>

        <div className="modal-actions" style={{ padding: '0 20px 20px 20px' }}>
          <button
            onClick={() => !isSubmitting && onReject(sosRequest.id)}
            disabled={isSubmitting}
            className="btn-sec"
            style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center', opacity: isSubmitting ? 0.5 : 1 }}
          >
            <X size={18} /> REJECT
          </button>
          <button
            onClick={() => canSubmit && onAccept(sosRequest.id, selectedDriverId, selectedDoctorId)}
            disabled={!canSubmit}
            className="btn-add-primary"
            style={{ 
              display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center', 
              backgroundColor: canSubmit ? '#ef4444' : '#374151', 
              opacity: canSubmit ? 1 : 0.5,
              cursor: canSubmit ? 'pointer' : 'not-allowed'
            }}
          >
            {isSubmitting ? (
              <><Loader size={18} className="animate-spin" /> PROCESSING...</>
            ) : (
              <><Check size={18} /> ACCEPT &amp; DISPATCH</>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
