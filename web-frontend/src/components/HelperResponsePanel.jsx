import React from 'react';
import { formatDistance } from '../hooks/useRadarSearch';

/**
 * HelperResponsePanel — Left-side panel showing discovered helpers
 * with YES/NO buttons, status badges, response counters, and winner banner.
 */
export default function HelperResponsePanel({
  discoveredHelpers = [],
  responses = {},
  onAccept,
  onReject,
  isSearchActive,
  finalHelper,
  currentRadius,
  totalCount,
  pendingCount,
  acceptedCount,
  rejectedCount,
  notifications = [],
}) {
  if (!isSearchActive && discoveredHelpers.length === 0 && !finalHelper) {
    return null; // Don't render if no search has started
  }

  return (
    <div className="helper-response-panel">
      {/* Status Bar */}
      <div className="radar-status-bar">
        <div className="radar-status-title">
          <span className="radar-status-icon">📡</span>
          <span>HELPER PROXIMITY SCAN</span>
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
      {finalHelper && (
        <div className="final-selection-banner" style={{ flexDirection: 'column' }}>
          <div style={{ display: 'flex', alignItems: 'center', width: '100%', gap: '15px' }}>
            <div className="final-banner-icon">🤝</div>
            <div className="final-banner-content">
              <div className="final-banner-label">HELPER SELECTED</div>
              <div className="final-banner-name">{finalHelper.name}</div>
              <div className="final-banner-distance">
                📏 {formatDistance(finalHelper.distance)} • {finalHelper.role || 'Volunteer'}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Helper Cards */}
      <div className="helper-cards-scroll">
        {discoveredHelpers.length === 0 && isSearchActive && (
          <div className="radar-searching-msg">
            <div className="searching-pulse"></div>
            <span>Scanning for helpers...</span>
          </div>
        )}

        {discoveredHelpers.map((h, idx) => {
          const status = responses[h.id] || 'PENDING';
          const isWinner = finalHelper && finalHelper.id === h.id;

          return (
            <div
              key={h.id}
              className={`helper-response-card ${status.toLowerCase()} ${isWinner ? 'winner' : ''}`}
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
                <span className="hrc-dept">{h.role || 'Volunteer'}</span>
                <span className="hrc-distance">{formatDistance(h.distance)}</span>
              </div>

              {status === 'PENDING' && !finalHelper && (
                <div className="hrc-actions">
                  <span className="hrc-waiting-text" style={{fontSize: '12px', color: '#94a3b8', fontStyle: 'italic'}}>Waiting for response...</span>
                </div>
              )}
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
