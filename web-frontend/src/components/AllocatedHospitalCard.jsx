import React, { useEffect, useState } from 'react';
import { fetchWithFallback } from '../services/apiClient';

const AllocatedHospitalCard = ({ sosId, finalHospital }) => {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (!sosId) return;

    // We can poll the backend for the specific SOS request details to get the assigned team
    const interval = setInterval(async () => {
      try {
        const res = await fetchWithFallback(`/api/v1/routing/status/${sosId}`);
        if (res.ok) {
          const json = await res.json();
          setData(json);
        }
      } catch (err) {
        // silently fail and retry
      }
    }, 3000);
    
    // Initial fetch
    fetchWithFallback(`/api/v1/routing/status/${sosId}`)
      .then(res => res.json())
      .then(setData)
      .catch(() => {});

    return () => clearInterval(interval);
  }, [sosId]);

  if (!data && !finalHospital) return null;

  // Derive hospital name from finalHospital prop or data if we had it
  const hospitalName = finalHospital?.name || 'Allocated Hospital';
  const hospitalDept = finalHospital?.dept || 'General';

  return (
    <div style={{
      background: 'white',
      borderRadius: '16px',
      padding: '24px',
      boxShadow: '0 10px 30px rgba(0,0,0,0.08)',
      marginBottom: '24px',
      border: '1px solid rgba(16, 185, 129, 0.2)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Decorative top border */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '4px',
        background: 'linear-gradient(90deg, #10b981, #34d399)'
      }} />

      <h2 style={{ 
        margin: '0 0 20px 0', 
        fontSize: '1.25rem', 
        color: '#111827', 
        display: 'flex', 
        alignItems: 'center', 
        gap: '8px' 
      }}>
        <span style={{ fontSize: '1.5rem' }}>🚑</span> Rescue Team Allocated
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
        
        {/* Hospital Info */}
        <div style={{ background: '#f9fafb', padding: '16px', borderRadius: '12px', border: '1px solid #e5e7eb' }}>
          <div style={{ fontSize: '0.875rem', color: '#6b7280', marginBottom: '4px', fontWeight: 500 }}>HOSPITAL</div>
          <div style={{ fontSize: '1.125rem', color: '#111827', fontWeight: 600 }}>{hospitalName}</div>
          <div style={{ fontSize: '0.875rem', color: '#4b5563', marginTop: '4px' }}>{hospitalDept} Department</div>
          {finalHospital?.distance && (
            <div style={{ fontSize: '0.875rem', color: '#10b981', marginTop: '4px', fontWeight: 500 }}>
              {(finalHospital.distance).toFixed(1)} km away
            </div>
          )}
        </div>

        {/* Doctor Info */}
        <div style={{ background: '#f0f9ff', padding: '16px', borderRadius: '12px', border: '1px solid #bae6fd' }}>
          <div style={{ fontSize: '0.875rem', color: '#0369a1', marginBottom: '4px', fontWeight: 500 }}>ASSIGNED DOCTOR</div>
          {data?.assigned_doctor_name ? (
            <>
              <div style={{ fontSize: '1.125rem', color: '#0c4a6e', fontWeight: 600 }}>Dr. {data.assigned_doctor_name}</div>
              <div style={{ fontSize: '0.875rem', color: '#0284c7', marginTop: '4px' }}>Emergency Physician</div>
              <div style={{ fontSize: '0.75rem', color: '#0369a1', marginTop: '8px', background: '#e0f2fe', padding: '4px 8px', borderRadius: '4px', display: 'inline-block' }}>
                Preparing for arrival
              </div>
            </>
          ) : (
            <div style={{ color: '#0ea5e9', fontSize: '0.9rem', fontStyle: 'italic', marginTop: '8px' }}>
              Pending assignment...
            </div>
          )}
        </div>

        {/* Driver Info */}
        <div style={{ background: '#fdf4ff', padding: '16px', borderRadius: '12px', border: '1px solid #fbcfe8' }}>
          <div style={{ fontSize: '0.875rem', color: '#86198f', marginBottom: '4px', fontWeight: 500 }}>AMBULANCE & DRIVER</div>
          {data?.assigned_driver_name ? (
            <>
              <div style={{ fontSize: '1.125rem', color: '#4a044e', fontWeight: 600 }}>{data.assigned_driver_name}</div>
              <div style={{ fontSize: '0.875rem', color: '#a21caf', marginTop: '4px' }}>
                Vehicle: {data.assigned_ambulance_reg || 'N/A'}
              </div>
              <div style={{ fontSize: '0.75rem', color: '#86198f', marginTop: '8px', background: '#fae8ff', padding: '4px 8px', borderRadius: '4px', display: 'inline-block' }}>
                Status: {data.driver_status?.replace('_', ' ') || 'DISPATCHED'}
              </div>
            </>
          ) : (
            <div style={{ color: '#d946ef', fontSize: '0.9rem', fontStyle: 'italic', marginTop: '8px' }}>
              Awaiting dispatch...
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default AllocatedHospitalCard;
