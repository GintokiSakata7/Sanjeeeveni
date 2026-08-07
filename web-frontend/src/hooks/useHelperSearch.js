import { useState, useRef, useCallback, useEffect } from 'react';
import { supabase } from '../services/supabaseClient';

// Radius steps in meters (matches Pygame config.py)
const RADIUS_STEPS = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000];

// Expansion interval: how long (ms) to wait before auto-expanding radius if no helper accepted
const EXPANSION_CHECK_INTERVAL = 3000;

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
 * Format meters to human-readable string (e.g. "500 m", "2.6 km").
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
 * useHelperSearch — Custom hook implementing the full expanding-radius radar search state machine.
 *
 * Rules:
 * 1. Fetch ALL helpers from DB, calculate distance/bearing relative to user GPS.
 * 2. Starts at radius step 0 (50m), continuously expands search distance.
 * 3. Search DOES NOT STOP when helpers are discovered or rejected.
 * 4. Search STOPS ONLY when an ACCEPT (YES) button is clicked.
 * 5. If multiple helpers accept, picks shortest distance winner.
 * 6. All helper IDs are strictly normalized as String(id) to ensure Accept/Reject buttons function 100% reliably.
 */
export default function useHelperSearch() {
  const [allHelpers, setAllHelpers] = useState([]);
  const [discoveredHelpers, setDiscoveredHelpers] = useState([]);
  const [responses, setResponses] = useState({});
  const [radiusStepIndex, setRadiusStepIndex] = useState(0);
  const [isSearchActive, setIsSearchActive] = useState(false);
  const [finalHelper, setFinalHelper] = useState(null);
  const [notifications, setNotifications] = useState([]);

  const pendingDiscoveryRef = useRef(new Set());
  const expansionTimerRef = useRef(null);

  // Ref to track latest state across async callbacks
  const stateRef = useRef({});
  useEffect(() => {
    stateRef.current = {
      allHelpers,
      discoveredHelpers,
      responses,
      radiusStepIndex,
      isSearchActive,
      finalHelper
    };
  });

  const currentRadius = RADIUS_STEPS[radiusStepIndex] || RADIUS_STEPS[RADIUS_STEPS.length - 1];

  // Add a toast notification
  const addNotification = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setNotifications(prev => [...prev, { id, message, type, timestamp: Date.now() }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 5000);
  }, []);

  /**
   * Start a new emergency helper search.
   */
  const startSearch = useCallback(async (userLat, userLon) => {
    setDiscoveredHelpers([]);
    setResponses({});
    setRadiusStepIndex(0);
    setFinalHelper(null);
    setNotifications([]);
    pendingDiscoveryRef.current = new Set();

    if (expansionTimerRef.current) {
      clearInterval(expansionTimerRef.current);
      expansionTimerRef.current = null;
    }

    addNotification(`SCANNING RADIUS: ${formatDistance(RADIUS_STEPS[0])}...`, 'scan');

    try {
      let data = [];
      try {
        const res = await supabase
          .from('helpers')
          .select('*')
          .eq('is_active', true);
        if (res.data && res.data.length > 0) {
          data = res.data;
        }
      } catch (err) {
        console.warn('Supabase helpers fetch failed, falling back to mock data:', err);
      }

      if (!data || data.length === 0) {
        addNotification('NO HELPERS IN RADIUS OR DB IS EMPTY', 'warning');
      }

      // Enrich each helper with distance, bearing, and normalized string ID
      const enriched = data.map(h => {
        const hLat = Number(h.live_lat || h.address_lat || h.latitude || h.lat || 0);
        const hLon = Number(h.live_lon || h.address_lon || h.longitude || h.lon || 0);
        const distance = haversineDistance(userLat, userLon, hLat, hLon);
        const bearing = calculateBearing(userLat, userLon, hLat, hLon);
        return {
          ...h,
          distance,
          bearing,
          id: String(h.id)
        };
      });

      enriched.sort((a, b) => a.distance - b.distance);

      setAllHelpers(enriched);
      setIsSearchActive(true);

      addNotification(`LOADED ${enriched.length} HELPERS — BEGINNING EXPANDING SCAN`, 'info');

    } catch (err) {
      console.error('Helper search error:', err);
      addNotification('ERROR INITIALIZING HELPER SEARCH', 'error');
    }
  }, [addNotification]);

  /**
   * Returns helpers within current radius not yet discovered.
   */
  const getUndiscoveredInRadius = useCallback(() => {
    const { allHelpers: all, radiusStepIndex: rsi } = stateRef.current;
    const radius = RADIUS_STEPS[rsi] || RADIUS_STEPS[RADIUS_STEPS.length - 1];
    return (all || []).filter(h => {
      return h.distance <= radius && !pendingDiscoveryRef.current.has(String(h.id));
    });
  }, []);

  /**
   * Called when a helper is discovered by radar sweep line or auto-discovery.
   */
  const discoverHelper = useCallback((rawId) => {
    if (!rawId || stateRef.current.finalHelper) return;
    const helperId = String(rawId);

    const helper = (stateRef.current.allHelpers || []).find(h => String(h.id) === helperId);
    if (!helper) return;

    if (pendingDiscoveryRef.current.has(helperId)) return;
    pendingDiscoveryRef.current.add(helperId);

    setDiscoveredHelpers(prev => {
      if (prev.some(h => String(h.id) === helperId)) return prev;
      return [...prev, helper];
    });

    setResponses(prev => {
      if (prev[helperId]) return prev;
      return { ...prev, [helperId]: 'PENDING' };
    });

    addNotification(`FOUND: ${helper.name} — ${formatDistance(helper.distance)}`, 'discover');
  }, [addNotification]);

  /**
   * Accept a helper — STOPS THE SEARCH and selects the shortest-distance helper.
   */
  const acceptHelper = useCallback((rawId) => {
    if (!rawId) return;
    const helperId = String(rawId);

    // Update responses
    let updatedResponses = {};
    setResponses(prev => {
      updatedResponses = { ...prev, [helperId]: 'ACCEPTED' };
      return updatedResponses;
    });

    const all = stateRef.current.allHelpers || [];
    const targetHelper = all.find(h => String(h.id) === helperId);

    // Filter all accepted helpers
    const accepted = all.filter(h => {
      const id = String(h.id);
      return id === helperId || updatedResponses[id] === 'ACCEPTED' || stateRef.current.responses[id] === 'ACCEPTED';
    });

    if (accepted.length > 0) {
      // Pick shortest distance
      const winner = accepted.reduce((best, h) => (h.distance < best.distance ? h : best));
      setFinalHelper(winner);
      setIsSearchActive(false);

      if (expansionTimerRef.current) {
        clearInterval(expansionTimerRef.current);
        expansionTimerRef.current = null;
      }

      addNotification(`✅ HOSPITAL ACCEPTED: ${winner.name} (${formatDistance(winner.distance)})`, 'accept');
    } else if (targetHelper) {
      setFinalHelper(targetHelper);
      setIsSearchActive(false);
      addNotification(`✅ HOSPITAL ACCEPTED: ${targetHelper.name} (${formatDistance(targetHelper.distance)})`, 'accept');
    }
  }, [addNotification]);

  /**
   * Reject a helper — Marks status REJECTED without stopping radius expansion.
   */
  const rejectHelper = useCallback((rawId) => {
    if (!rawId) return;
    const helperId = String(rawId);

    const all = stateRef.current.allHelpers || [];
    const helper = all.find(h => String(h.id) === helperId);
    const name = helper ? helper.name : 'Helper';

    setResponses(prev => ({ ...prev, [helperId]: 'REJECTED' }));
    addNotification(`❌ ${name} REJECTED`, 'reject');
  }, [addNotification]);

  /**
   * Continuous Auto-Expansion Effect:
   * Periodically expands the radius (50m -> 100m -> 200m -> 500m -> 1k -> 2k -> 5k -> 10k -> 20k -> 50k).
   * Search DOES NOT STOP when helpers are found or rejected.
   * Search STOPS ONLY when finalHelper is set (Accept clicked).
   */
  useEffect(() => {
    if (!isSearchActive || finalHelper || allHelpers.length === 0) return;

    expansionTimerRef.current = setInterval(() => {
      const state = stateRef.current;
      if (state.finalHelper || !state.isSearchActive) return;

      const rsi = state.radiusStepIndex;
      const radius = RADIUS_STEPS[rsi] || RADIUS_STEPS[RADIUS_STEPS.length - 1];
      const helpersInRadius = (state.allHelpers || []).filter(h => h.distance <= radius);

      // Auto-discover any helper within current radius so they appear on the panel
      helpersInRadius.forEach(h => {
        const idStr = String(h.id);
        if (!pendingDiscoveryRef.current.has(idStr)) {
          discoverHelper(idStr);
        }
      });

      const resp = state.responses || {};
      const anyAccepted = Object.values(resp).some(s => s === 'ACCEPTED');
      if (anyAccepted) return; // Stop expanding if accepted

      // If there are more radius steps available, expand to next radius step!
      if (rsi < RADIUS_STEPS.length - 1) {
        const newIndex = rsi + 1;
        const oldStr = formatDistance(RADIUS_STEPS[rsi]);
        const newStr = formatDistance(RADIUS_STEPS[newIndex]);

        setRadiusStepIndex(newIndex);
        addNotification(`EXPANDING SEARCH RADIUS: ${oldStr} → ${newStr}`, 'expand');
      } else {
        // Max radius reached
        const allResponded = (state.allHelpers || []).every(h => {
          const s = resp[String(h.id)];
          return s && s !== 'PENDING';
        });

        if (allResponded) {
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
    };
  }, [isSearchActive, finalHelper, allHelpers.length, addNotification, discoverHelper]);

  // Compute stats
  const totalCount = Object.keys(responses).length;
  const pendingCount = Object.values(responses).filter(s => s === 'PENDING').length;
  const acceptedCount = Object.values(responses).filter(s => s === 'ACCEPTED').length;
  const rejectedCount = Object.values(responses).filter(s => s === 'REJECTED').length;

  return {
    // State
    allHelpers,
    discoveredHelpers,
    responses,
    currentRadius,
    radiusStepIndex,
    isSearchActive,
    finalHelper,
    notifications,

    // Stats
    totalCount,
    pendingCount,
    acceptedCount,
    rejectedCount,

    // Actions
    startSearch,
    discoverHelper,
    acceptHelper,
    rejectHelper,
    getUndiscoveredInRadius,

    // Helpers
    formatDistance,
    RADIUS_STEPS,
  };
}
