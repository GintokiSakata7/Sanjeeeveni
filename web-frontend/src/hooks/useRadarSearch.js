import { useState, useRef, useCallback, useEffect } from 'react';
import { fetchWithFallback } from '../services/apiClient';
import { supabase } from '../services/supabaseClient';

// Radius steps in meters (matches Pygame config.py)
const RADIUS_STEPS = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000];

// Expansion interval: how long (ms) to wait at each radius before checking for expansion
const EXPANSION_CHECK_INTERVAL = 4000;

/**
 * Haversine formula — calculates distance in meters between two lat/lon points.
 */
function haversineDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000; // Earth radius in meters
  const toRad = (deg) => (deg * Math.PI) / 180;
  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Calculate bearing (0–360°) from point A to point B.
 * 0° = North, 90° = East, 180° = South, 270° = West.
 */
function calculateBearing(lat1, lon1, lat2, lon2) {
  const toRad = (deg) => (deg * Math.PI) / 180;
  const toDeg = (rad) => (rad * 180) / Math.PI;
  const dLon = toRad(lon2 - lon1);
  const y = Math.sin(dLon) * Math.cos(toRad(lat2));
  const x =
    Math.cos(toRad(lat1)) * Math.sin(toRad(lat2)) -
    Math.sin(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.cos(dLon);
  let bearing = toDeg(Math.atan2(y, x));
  return (bearing + 360) % 360;
}

/**
 * Format meters to human-readable string.
 */
export function formatDistance(meters) {
  if (meters >= 1000) {
    const km = meters / 1000;
    const formatted = km.toFixed(1);
    return formatted.endsWith('.0') ? `${Math.round(km)} km` : `${formatted} km`;
  }
  return `${Math.round(meters)} m`;
}

/**
 * useRadarSearch — Custom hook implementing the full Pygame-style radar search state machine.
 *
 * Flow:
 * 1. Fetch ALL hospitals from koushik table
 * 2. Calculate distance + bearing from user GPS to each
 * 3. Start at radius step 0 (50m), continuously expand
 * 4. Hospitals within current radius get "discovered" when the sweep beam passes their bearing
 * 5. Discovered hospitals show up in the left panel with YES/NO buttons
 * 6. YES → accepted (pick closest winner, stop search)
 * 7. NO → rejected (if all rejected at current radius, auto-expand)
 * 8. Radar never stops until a hospital accepts or max radius reached
 */
export default function useRadarSearch() {
  // All hospitals fetched from DB, enriched with distance/bearing
  const [allHospitals, setAllHospitals] = useState([]);

  // Hospitals that the sweep beam has revealed
  const [discoveredHospitals, setDiscoveredHospitals] = useState([]);

  // Response map: hospitalId → "PENDING" | "ACCEPTED" | "REJECTED"
  const [responses, setResponses] = useState({});

  // Current radius step index
  const [radiusStepIndex, setRadiusStepIndex] = useState(0);

  // Search active flag
  const [isSearchActive, setIsSearchActive] = useState(false);

  // Final winner
  const [finalHospital, setFinalHospital] = useState(null);

  // Notifications log
  const [notifications, setNotifications] = useState([]);

  // Track which hospitals are still pending discovery (not yet swept)
  const pendingDiscoveryRef = useRef(new Set());

  // Expansion timer ref
  const expansionTimerRef = useRef(null);

  // Ref to track latest state for callbacks
  const stateRef = useRef({});
  useEffect(() => {
    stateRef.current = {
      allHospitals,
      discoveredHospitals,
      responses,
      radiusStepIndex,
      isSearchActive,
      finalHospital
    };
  });

  const currentRadius = RADIUS_STEPS[radiusStepIndex] || RADIUS_STEPS[RADIUS_STEPS.length - 1];

  // Add a notification
  const addNotification = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setNotifications(prev => [...prev, { id, message, type, timestamp: Date.now() }]);
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  }, []);

  const sosPayloadRef = useRef(null);

  const updateSosPayload = useCallback((payload) => {
    sosPayloadRef.current = { ...sosPayloadRef.current, ...payload };
  }, []);

  /**
   * Start a new search: fetch all hospitals, calculate distances, begin scanning.
   */
  const startSearch = useCallback(async (userLat, userLon, initialPayload = null) => {
    sosPayloadRef.current = initialPayload;

    // Reset state
    setDiscoveredHospitals([]);
    setResponses({});
    setRadiusStepIndex(0);
    setFinalHospital(null);
    setNotifications([]);
    pendingDiscoveryRef.current = new Set();

    if (expansionTimerRef.current) {
      clearInterval(expansionTimerRef.current);
      expansionTimerRef.current = null;
    }

    addNotification(`SCANNING RADIUS: ${formatDistance(RADIUS_STEPS[0])}...`, 'scan');

    try {
      // Fetch ALL hospitals from the FastAPI backend instead of direct Supabase dummy table
      const res = await fetchWithFallback('/api/v1/hospital/all');
      if (!res.ok) throw new Error("Failed to fetch hospitals");
      const data = await res.json();

      if (!data || data.length === 0) {
        addNotification('NO HOSPITALS FOUND IN DATABASE', 'error');
        return;
      }

      // Enrich each hospital with distance and bearing
      const enriched = data.map(h => {
        const hLat = h.latitude || 0;
        const hLon = h.longitude || 0;
        const distance = haversineDistance(userLat, userLon, hLat, hLon);
        const bearing = calculateBearing(userLat, userLon, hLat, hLon);
        return { ...h, distance, bearing, id: String(h.id) };
      });

      // Sort by distance
      enriched.sort((a, b) => a.distance - b.distance);

      setAllHospitals(enriched);
      setIsSearchActive(true);

      addNotification(`LOADED ${enriched.length} HOSPITALS — BEGINNING SCAN`, 'info');

    } catch (err) {
      console.error('Backend fetch error:', err);
      addNotification('DATABASE ERROR — COULD NOT FETCH HOSPITALS', 'error');
    }
  }, [addNotification]);

  /**
   * Get hospitals that fall within the current radius but haven't been discovered yet.
   */
  const getUndiscoveredInRadius = useCallback(() => {
    const { allHospitals: all, radiusStepIndex: rsi } = stateRef.current;
    const radius = RADIUS_STEPS[rsi] || RADIUS_STEPS[RADIUS_STEPS.length - 1];
    return (all || []).filter(h => {
      return h.distance <= radius && !pendingDiscoveryRef.current.has(h.id);
    });
  }, []);

  /**
   * Called by RadarCanvas when the sweep beam passes a hospital's bearing.
   * Transitions a hospital from "undiscovered" to "discovered + PENDING".
   */
  const discoverHospital = useCallback(async (hospitalId) => {
    if (stateRef.current.finalHospital) return; // Search already resolved

    const hospital = (stateRef.current.allHospitals || []).find(h => h.id === hospitalId);
    if (!hospital) return;

    // Mark as discovered
    pendingDiscoveryRef.current.add(hospitalId);

    setDiscoveredHospitals(prev => {
      if (prev.find(h => h.id === hospitalId)) return prev;
      return [...prev, hospital];
    });

    setResponses(prev => {
      if (prev[hospitalId]) return prev;
      return { ...prev, [hospitalId]: 'PENDING' };
    });

    addNotification(`FOUND: ${hospital.name} — ${formatDistance(hospital.distance)}`, 'discover');

    // Send SOS Routing request to the backend for this specific hospital
    try {
      const payload = sosPayloadRef.current || {};
      const res = await fetchWithFallback('/api/v1/routing/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hospital_id: hospitalId,
          citizen_lat: payload.latitude || 0,
          citizen_lng: payload.longitude || 0,
          transcript: payload.text || 'Emergency distress signal',
          triage_urgency: payload.urgency || 'HIGH',
          image_url: null
        })
      });
      
      if (!res.ok) throw new Error("Routing failed");
      const data = await res.json();
      
      // We could store the returned sos_id if we wanted to track it exactly, 
      // but for polling we can just poll the status using the hospital_id + citizen data
      // For now, we'll store sos_id in a mapping so the polling system knows which SOS to check.
      setResponses(prev => ({ ...prev, [`${hospitalId}_sos_id`]: data.sos_id }));
      
    } catch (err) {
      console.error("Failed to send SOS to hospital:", err);
    }

  }, [addNotification]);

  /**
   * Accept a hospital.
   */
  const acceptHospital = useCallback((hospitalId) => {
    setResponses(prev => {
      const updated = { ...prev, [hospitalId]: 'ACCEPTED' };

      // Find winner among all accepted (shortest distance)
      const accepted = (stateRef.current.allHospitals || []).filter(h => updated[h.id] === 'ACCEPTED');
      if (accepted.length > 0) {
        const winner = accepted.reduce((best, h) => h.distance < best.distance ? h : best);
        setFinalHospital(winner);
        setIsSearchActive(false);

        if (expansionTimerRef.current) {
          clearInterval(expansionTimerRef.current);
          expansionTimerRef.current = null;
        }

        addNotification(`✅ HOSPITAL ACCEPTED: ${winner.name} (${formatDistance(winner.distance)})`, 'accept');
      }

      return updated;
    });
  }, [addNotification]);

  /**
   * Reject a hospital.
   */
  const rejectHospital = useCallback((hospitalId) => {
    const hospital = (stateRef.current.allHospitals || []).find(h => h.id === hospitalId);
    const name = hospital ? hospital.name : 'Hospital';

    setResponses(prev => ({ ...prev, [hospitalId]: 'REJECTED' }));
    addNotification(`❌ ${name} REJECTED`, 'reject');
  }, [addNotification]);

  /**
   * Auto-expansion effect:
   * Periodically checks if all discovered hospitals at current radius have responded.
   * If all rejected → expand radius. If no hospitals at radius → expand.
   */
  useEffect(() => {
    // Poll backend for PENDING SOS statuses every 3 seconds
    let statusTimer = null;
    if (isSearchActive && !finalHospital) {
      statusTimer = setInterval(async () => {
        const state = stateRef.current;
        const currentResponses = state.responses || {};
        
        for (const [hospitalId, status] of Object.entries(currentResponses)) {
          if (status === 'PENDING') {
            const sosId = currentResponses[`${hospitalId}_sos_id`];
            if (sosId) {
              try {
                const res = await fetchWithFallback(`/api/v1/routing/status/${sosId}`);
                if (res.ok) {
                  const data = await res.json();
                  if (data.status === 'ACCEPTED') {
                    acceptHospital(hospitalId);
                  } else if (data.status === 'REJECTED') {
                    rejectHospital(hospitalId);
                  }
                }
              } catch (e) {
                // Silently ignore poll errors
              }
            }
          }
        }
      }, 3000);
    }

    if (!isSearchActive || finalHospital || allHospitals.length === 0) return;

    expansionTimerRef.current = setInterval(() => {
      const state = stateRef.current;
      if (state.finalHospital || !state.isSearchActive) return;


      const rsi = state.radiusStepIndex;
      const radius = RADIUS_STEPS[rsi] || RADIUS_STEPS[RADIUS_STEPS.length - 1];
      const hospitalsInRadius = (state.allHospitals || []).filter(h => h.distance <= radius);
      const resp = state.responses || {};

      // Check if all hospitals in this radius have been discovered and responded to
      const allDiscovered = hospitalsInRadius.every(h => pendingDiscoveryRef.current.has(h.id));
      const allResponded = hospitalsInRadius.every(h => resp[h.id] && resp[h.id] !== 'PENDING');
      const anyAccepted = hospitalsInRadius.some(h => resp[h.id] === 'ACCEPTED');

      if (anyAccepted) return; // Don't expand if someone accepted

      const shouldExpand = hospitalsInRadius.length === 0 || (allDiscovered && allResponded);

      if (shouldExpand) {
        if (rsi < RADIUS_STEPS.length - 1) {
          const newIndex = rsi + 1;
          const oldStr = formatDistance(RADIUS_STEPS[rsi]);
          const newStr = formatDistance(RADIUS_STEPS[newIndex]);

          setRadiusStepIndex(newIndex);

          if (hospitalsInRadius.length === 0) {
            addNotification(`NO HOSPITALS AT ${oldStr} → EXPANDING TO ${newStr}`, 'expand');
          } else {
            addNotification(`ALL REJECTED AT ${oldStr} → EXPANDING TO ${newStr}`, 'expand');
          }
        } else {
          // Max radius reached
          addNotification('MAX RADIUS (50 km) REACHED — NO HOSPITAL ACCEPTED', 'error');
          setIsSearchActive(false);
        }
      }
    }, EXPANSION_CHECK_INTERVAL);

    return () => {
      if (expansionTimerRef.current) {
        clearInterval(expansionTimerRef.current);
        expansionTimerRef.current = null;
      }
      if (statusTimer) {
        clearInterval(statusTimer);
      }
    };
  }, [isSearchActive, finalHospital, allHospitals.length, addNotification]);

  // Compute stats
  const totalCount = Object.keys(responses).length;
  const pendingCount = Object.values(responses).filter(s => s === 'PENDING').length;
  const acceptedCount = Object.values(responses).filter(s => s === 'ACCEPTED').length;
  const rejectedCount = Object.values(responses).filter(s => s === 'REJECTED').length;

  return {
    // State
    allHospitals,
    discoveredHospitals,
    responses,
    currentRadius,
    radiusStepIndex,
    isSearchActive,
    finalHospital,
    notifications,

    // Stats
    totalCount,
    pendingCount,
    acceptedCount,
    rejectedCount,

    // Actions
    startSearch,
    discoverHospital,
    acceptHospital,
    rejectHospital,
    getUndiscoveredInRadius,
    updateSosPayload,

    // Helpers
    formatDistance,
    RADIUS_STEPS,
  };
}
