import React from 'react';

export default function GpsRadarMap({ gps }) {
  return (
    <div className="map-hud-card">
      <div className="map-sweep"></div>
      
      <div style={{ display: 'flex', justifyContent: 'space-between', zIndex: 2 }}>
        <div style={{ fontSize: '12px', fontWeight: '700', color: 'var(--green-success)' }}>
          ● {gps.status}
        </div>
        <div style={{ fontSize: '11px', fontFamily: 'JetBrains Mono', color: 'var(--text-sub)' }}>
          LAT: {gps.lat.toFixed(4)} • LNG: {gps.lng.toFixed(4)}
        </div>
      </div>

      {/* Real Patient GPS Location Marker */}
      <div className="map-node patient" style={{ top: '48%', left: '42%' }}>
        <span>📍 PATIENT GPS: {gps.lat.toFixed(4)}, {gps.lng.toFixed(4)}</span>
      </div>

      <div style={{ fontSize: '11px', color: 'var(--text-muted)', zIndex: 2, display: 'flex', gap: '16px' }}>
        <span>GEOSPATIAL AI MONITOR</span>
        <span>GPS ACCURACY: HIGH</span>
      </div>
    </div>
  );
}
