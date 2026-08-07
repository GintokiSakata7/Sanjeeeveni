import React from 'react';
import { formatDistance } from '../hooks/useRadarSearch';
import SOSStatusTimeline from './SOSStatusTimeline';

/**
 * HospitalResponsePanel — Left-side panel showing discovered hospitals
 * with YES/NO buttons, status badges, response counters, and winner banner.
 */
export default function HospitalResponsePanel({
  discoveredHospitals = [],
  responses = {},
  onAccept,
  onReject,
  isSearchActive,
  finalHospital,
  currentRadius,
  totalCount,
  pendingCount,
  acceptedCount,
  rejectedCount,
  notifications = [],
}) {
  if (!isSearchActive && discoveredHospitals.length === 0 && !finalHospital) {
    return null; // Don't render if no search has started
  }

  return (
    <div className="hospital-response-panel">
      {/* Status Bar */}
      <div className="radar-status-bar">
        <div className="radar-status-title">
          <span className="radar-status-icon">📡</span>
          <span>HOSPITAL PROXIMITY SCAN</span>
        </div>
        <div className="radar-status-info">
          <span className="radar-radius-badge">
            RADIUS: {formatDistance(currentRadius)}
          </span>
          {isSearchActive && (
            <span className="radar-scanning-badge">SCANNING...</span>
          )}
        </div>
      </div>

      {/* Response Counters */}
      {totalCount > 0 && (
        <div className="response-counters">
          <span className="counter-item">
            <span className="counter-label">TOTAL</span>
            <span className="counter-value">{totalCount}</span>
          </span>
          <span className="counter-divider">|</span>
          <span className="counter-item pending">
            <span className="counter-label">PENDING</span>
            <span className="counter-value">{pendingCount}</span>
          </span>
          <span className="counter-divider">|</span>
          <span className="counter-item accepted">
            <span className="counter-label">ACCEPTED</span>
            <span className="counter-value">{acceptedCount}</span>
          </span>
          <span className="counter-divider">|</span>
          <span className="counter-item rejected">
            <span className="counter-label">REJECTED</span>
            <span className="counter-value">{rejectedCount}</span>
          </span>
        </div>
      )}

      {/* Final Selection Banner */}
      {finalHospital && (
        <div className="final-selection-banner" style={{ flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', width: '100%', gap: '15px' }}>
            <div className="final-banner-icon">🏥</div>
            <div className="final-banner-content">
              <div className="final-banner-label">HOSPITAL SELECTED</div>
              <div className="final-banner-name">{finalHospital.name}</div>
              <div className="final-banner-distance">
                📏 {formatDistance(finalHospital.distance)} • {finalHospital.dept || 'General'}
              </div>
            </div>
          </div>
          
          <div style={{ width: '100%', marginTop: '10px' }}>
             {/* Read SOS ID from responses mapping */}
             <SOSStatusTimeline sosId={responses[`${finalHospital.id}_sos_id`]} />
          </div>
        </div>
      )}

      {/* Hospital Cards */}
      <div className="hospital-cards-scroll">
        {discoveredHospitals.length === 0 && isSearchActive && (
          <div className="radar-searching-msg">
            <div className="searching-pulse"></div>
            <span>Scanning for hospitals...</span>
          </div>
        )}

        {discoveredHospitals.map((h, idx) => {
          const status = responses[h.id] || 'PENDING';
          const isWinner = finalHospital && finalHospital.id === h.id;

          return (
            <div
              key={h.id}
              className={`hospital-response-card ${status.toLowerCase()} ${isWinner ? 'winner' : ''}`}
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              <div className="hrc-header">
                <span className="hrc-rank">#{idx + 1}</span>
                <span className="hrc-name">{h.name}</span>
                <span className={`hrc-status-badge ${status.toLowerCase()}`}>
                  {status === 'PENDING' && '⏳ PENDING'}
                  {status === 'ACCEPTED' && '✅ ACCEPTED'}
                  {status === 'REJECTED' && '❌ REJECTED'}
                </span>
              </div>

              <div className="hrc-details">
                <span className="hrc-dept">{h.dept || 'General'}</span>
                <span className="hrc-distance">{formatDistance(h.distance)}</span>
                {h.available_beds !== undefined && (
                  <span className="hrc-beds">
                    🛏 {h.available_beds}/{h.total_beds}
                  </span>
                )}
              </div>

              {/* Removed manual YES/NO buttons as the system handles it automatically */}
            </div>
          );
        })}
      </div>

      {/* Notifications */}
      {notifications.length > 0 && (
        <div className="radar-notifications">
          {notifications.slice(-3).map(n => (
            <div key={n.id} className={`radar-notification ${n.type}`}>
              {n.message}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
