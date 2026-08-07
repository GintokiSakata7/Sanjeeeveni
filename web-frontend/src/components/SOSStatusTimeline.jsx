import React, { useEffect, useState } from 'react';
import { Clock, CheckCircle2, Truck, Activity, User, ShieldAlert } from 'lucide-react';
import { getApiUrl } from '../config';

export default function SOSStatusTimeline({ sosId }) {
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sosId) return;
    
    const fetchTimeline = async () => {
      try {
        const res = await fetch(getApiUrl(`/api/v1/routing/timeline/${sosId}`));
        if (res.ok) {
          const data = await res.json();
          setTimeline(data);
        }
      } catch (err) {
        console.error("Error fetching timeline:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchTimeline();
    const interval = setInterval(fetchTimeline, 3000);
    return () => clearInterval(interval);
  }, [sosId]);

  if (!sosId) return null;

  const getIcon = (type) => {
    switch (type) {
      case 'CREATED': return <ShieldAlert size={16} color="#fb923c" />;
      case 'HOSPITAL_ACCEPTED': return <Activity size={16} color="#34d399" />;
      case 'DRIVER_ASSIGNED': return <User size={16} color="#60a5fa" />;
      case 'DRIVER_ACCEPTED': return <CheckCircle2 size={16} color="#a78bfa" />;
      case 'EN_ROUTE': return <Truck size={16} color="#f472b6" />;
      case 'DOCTOR_ASSIGNED': return <User size={16} color="#2dd4bf" />;
      default: return <Clock size={16} color="#94a3b8" />;
    }
  };

  return (
    <div style={{
      backgroundColor: '#0f1523',
      border: '1px solid #1e293b',
      borderRadius: '8px',
      padding: '15px',
      marginTop: '15px'
    }}>
      <h4 style={{ color: '#fff', marginBottom: '15px', fontSize: '14px', borderBottom: '1px solid #1e293b', paddingBottom: '10px' }}>
        Live Status Timeline
      </h4>
      
      {loading && timeline.length === 0 ? (
        <p style={{ color: '#94a3b8', fontSize: '12px' }}>Loading timeline...</p>
      ) : timeline.length === 0 ? (
        <p style={{ color: '#94a3b8', fontSize: '12px' }}>No events recorded yet.</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {timeline.map((event, idx) => (
            <div key={event.id} style={{ display: 'flex', gap: '12px' }}>
              <div style={{
                width: '32px', height: '32px', borderRadius: '50%',
                backgroundColor: '#1a2332', display: 'flex', alignItems: 'center', justifyContent: 'center',
                flexShrink: 0,
                border: '1px solid #334155'
              }}>
                {getIcon(event.event_type)}
              </div>
              <div>
                <p style={{ color: '#e2e8f0', margin: '0 0 4px 0', fontSize: '13px' }}>
                  {event.message}
                </p>
                <div style={{ display: 'flex', gap: '10px', fontSize: '11px', color: '#64748b' }}>
                  <span>{new Date(event.created_at).toLocaleTimeString()}</span>
                  <span style={{ textTransform: 'capitalize' }}>by {event.actor_role}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
