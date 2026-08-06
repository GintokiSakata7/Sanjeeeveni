import React, { useEffect, useRef, useCallback } from 'react';

/**
 * RadarCanvas — HTML5 Canvas radar with sweep beam, bearing-based blips, 
 * dynamic radius ring, and sweep-discovery callbacks.
 *
 * Props:
 *  - allHospitals: Array of { id, distance, bearing, ... } (all fetched, for rendering within radius)
 *  - discoveredIds: Set or array of hospital IDs that have been discovered
 *  - responses: Object { hospitalId: "PENDING"|"ACCEPTED"|"REJECTED" }
 *  - currentRadius: Current search radius in meters (for the glowing ring)
 *  - maxRadius: The max radius in the current step set (for scaling)
 *  - isScanning: Boolean — whether sweep beam should rotate
 *  - onSweepDiscover: callback(hospitalId) — fired when beam passes an undiscovered hospital
 *  - getUndiscoveredInRadius: function returning hospitals in current radius not yet discovered
 *  - finalHospitalId: string | null — the accepted winner's ID
 */
const RadarCanvas = ({
  allHospitals = [],
  discoveredIds = [],
  responses = {},
  currentRadius = 50,
  maxRadius = 50000,
  isScanning = false,
  onSweepDiscover,
  getUndiscoveredInRadius,
  finalHospitalId = null,
}) => {
  const canvasRef = useRef(null);
  const sweepAngleRef = useRef(0);
  const animationRef = useRef(null);
  const lastDiscoverCheckRef = useRef({});

  // Convert discoveredIds to a Set for O(1) lookup
  const discoveredSetRef = useRef(new Set());
  useEffect(() => {
    discoveredSetRef.current = new Set(
      Array.isArray(discoveredIds) ? discoveredIds : []
    );
  }, [discoveredIds]);

  // Store latest props in refs for the animation loop
  const propsRef = useRef({});
  useEffect(() => {
    propsRef.current = {
      allHospitals,
      responses,
      currentRadius,
      maxRadius,
      isScanning,
      finalHospitalId
    };
  });

  const onSweepDiscoverRef = useRef(onSweepDiscover);
  useEffect(() => { onSweepDiscoverRef.current = onSweepDiscover; }, [onSweepDiscover]);

  const getUndiscoveredRef = useRef(getUndiscoveredInRadius);
  useEffect(() => { getUndiscoveredRef.current = getUndiscoveredInRadius; }, [getUndiscoveredInRadius]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    const size = 340;
    canvas.width = size;
    canvas.height = size;
    
    const cx = size / 2;
    const cy = size / 2;
    const radius = (size / 2) - 14;

    let lastTime = performance.now();
    const SWEEP_SPEED = 120;

    const drawRadar = (time) => {
      const dt = (time - lastTime) / 1000;
      lastTime = time;
      const props = propsRef.current;

      if (props.isScanning) {
        sweepAngleRef.current = (sweepAngleRef.current + SWEEP_SPEED * dt) % 360;
      }

      ctx.clearRect(0, 0, size, size);

      // Base dark circle
      ctx.beginPath();
      ctx.arc(cx, cy, radius, 0, Math.PI * 2);
      ctx.fillStyle = 'rgba(10, 18, 22, 0.85)';
      ctx.fill();
      ctx.lineWidth = 2;
      ctx.strokeStyle = 'rgba(0, 229, 255, 0.5)';
      ctx.stroke();

      // Concentric rings (25%, 50%, 75%)
      [0.25, 0.5, 0.75].forEach(ratio => {
        ctx.beginPath();
        ctx.arc(cx, cy, radius * ratio, 0, Math.PI * 2);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
        ctx.stroke();
      });

      // Crosshairs
      ctx.beginPath();
      ctx.moveTo(cx - radius, cy);
      ctx.lineTo(cx + radius, cy);
      ctx.moveTo(cx, cy - radius);
      ctx.lineTo(cx, cy + radius);
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Diagonal lines
      const diagOffset = radius * 0.7071;
      ctx.beginPath();
      ctx.moveTo(cx - diagOffset, cy - diagOffset);
      ctx.lineTo(cx + diagOffset, cy + diagOffset);
      ctx.moveTo(cx - diagOffset, cy + diagOffset);
      ctx.lineTo(cx + diagOffset, cy - diagOffset);
      ctx.strokeStyle = 'rgba(0, 255, 200, 0.06)';
      ctx.stroke();

      // Dynamic search radius ring (cyan glow)
      if (props.currentRadius && props.maxRadius > 0) {
        const radiusRatio = Math.min(props.currentRadius / props.maxRadius, 1.0);
        const ringPx = radius * radiusRatio;
        if (ringPx > 5) {
          ctx.beginPath();
          ctx.arc(cx, cy, ringPx, 0, Math.PI * 2);
          ctx.lineWidth = 2;
          ctx.strokeStyle = 'rgba(0, 229, 255, 0.7)';
          ctx.setLineDash([4, 4]);
          ctx.stroke();
          ctx.setLineDash([]);
        }
      }

      // Cardinal labels
      ctx.font = '10px "JetBrains Mono", monospace';
      ctx.textAlign = 'center';
      ctx.fillStyle = 'rgba(140, 200, 190, 0.8)';
      ctx.fillText('N', cx, cy - radius - 4);
      ctx.fillText('S', cx, cy + radius + 12);
      ctx.fillText('E', cx + radius + 10, cy + 4);
      ctx.fillText('W', cx - radius - 10, cy + 4);

      // Draw hospital blips (only discovered ones)
      const sweepAngle = sweepAngleRef.current;
      const hospitals = props.allHospitals || [];
      const maxR = props.maxRadius || 50000;
      const resp = props.responses || {};
      const discovered = discoveredSetRef.current;

      hospitals.forEach(h => {
        if (!discovered.has(h.id)) return; // Only render discovered

        // Position blip by bearing and distance
        const distRatio = Math.min(h.distance / maxR, 1.0);
        const blipRadius = distRatio * radius;
        const bearingRad = (h.bearing * Math.PI) / 180;
        const tx = cx + blipRadius * Math.sin(bearingRad);
        const ty = cy - blipRadius * Math.cos(bearingRad);

        // Determine color by status
        const status = resp[h.id] || 'PENDING';
        let blipColor, glowColor;
        if (h.id === props.finalHospitalId) {
          blipColor = 'rgba(0, 255, 140, 1)';
          glowColor = 'rgba(0, 255, 140, 0.8)';
        } else if (status === 'ACCEPTED') {
          blipColor = 'rgba(0, 255, 140, 0.9)';
          glowColor = 'rgba(0, 255, 140, 0.5)';
        } else if (status === 'REJECTED') {
          blipColor = 'rgba(255, 60, 80, 0.7)';
          glowColor = 'rgba(255, 60, 80, 0.3)';
        } else {
          // PENDING — fade based on sweep proximity
          let angleDiff = sweepAngle - h.bearing;
          if (angleDiff < 0) angleDiff += 360;
          let opacity = 0.25;
          if (angleDiff >= 0 && angleDiff < 60) {
            opacity = 1 - (angleDiff / 60);
          }
          blipColor = `rgba(255, 180, 0, ${Math.max(opacity, 0.25)})`;
          glowColor = `rgba(255, 180, 0, ${Math.max(opacity * 0.5, 0.1)})`;
        }

        // Draw glow
        ctx.shadowBlur = 8;
        ctx.shadowColor = glowColor;
        ctx.beginPath();
        ctx.arc(tx, ty, 5, 0, Math.PI * 2);
        ctx.fillStyle = blipColor;
        ctx.fill();
        
        // Inner core
        ctx.beginPath();
        ctx.arc(tx, ty, 2, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      // Sweep beam discovery check
      if (props.isScanning && getUndiscoveredRef.current && onSweepDiscoverRef.current) {
        const undiscovered = getUndiscoveredRef.current();
        undiscovered.forEach(h => {
          // Check if sweep angle is close to this hospital's bearing
          let diff = sweepAngle - h.bearing;
          if (diff < 0) diff += 360;
          if (diff >= 0 && diff < 5) {
            // Beam just passed — discover!
            if (!lastDiscoverCheckRef.current[h.id]) {
              lastDiscoverCheckRef.current[h.id] = true;
              onSweepDiscoverRef.current(h.id);
            }
          } else {
            // Reset so it can be discovered again if sweep comes around
            // (shouldn't happen since we only discover once, but safety)
          }
        });
      }

      // Sweep beam line
      const sweepRad = (sweepAngle * Math.PI) / 180;
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      ctx.lineTo(cx + radius * Math.sin(sweepRad), cy - radius * Math.cos(sweepRad));
      ctx.lineWidth = 2;
      ctx.strokeStyle = '#00e5ff';
      ctx.stroke();

      // Sweep gradient tail
      ctx.beginPath();
      ctx.moveTo(cx, cy);
      const TAIL_DEGREES = 40;
      for (let i = 0; i <= TAIL_DEGREES; i += 2) {
        const r = ((sweepAngle - i) * Math.PI) / 180;
        ctx.lineTo(cx + radius * Math.sin(r), cy - radius * Math.cos(r));
      }
      ctx.closePath();

      const gradient = ctx.createConicGradient(
        ((sweepAngle - 90) * Math.PI) / 180, cx, cy
      );
      gradient.addColorStop(0, 'rgba(0, 229, 255, 0)');
      gradient.addColorStop(1 - TAIL_DEGREES / 360, 'rgba(0, 229, 255, 0)');
      gradient.addColorStop(1, 'rgba(0, 229, 255, 0.35)');
      ctx.fillStyle = gradient;
      ctx.fill();

      // Center dot
      ctx.beginPath();
      ctx.arc(cx, cy, 4, 0, Math.PI * 2);
      ctx.fillStyle = '#00e5ff';
      ctx.fill();

      animationRef.current = requestAnimationFrame(drawRadar);
    };

    animationRef.current = requestAnimationFrame(drawRadar);

    return () => {
      cancelAnimationFrame(animationRef.current);
    };
  }, []); // Single mount — all dynamic data accessed via refs

  return (
    <div style={{
      position: 'relative',
      width: '100%',
      maxWidth: '340px',
      aspectRatio: '1/1',
      margin: '0 auto',
      borderRadius: '50%',
      boxShadow: '0 0 35px rgba(0, 229, 255, 0.12), inset 0 0 35px rgba(0,0,0,0.5)',
      border: '1.5px solid rgba(0, 229, 255, 0.25)',
      overflow: 'hidden',
      background: 'rgba(0,0,0,0.15)'
    }}>
      <div style={{
        position: 'absolute',
        top: 0, left: 0, right: 0, bottom: 0,
        background: 'repeating-linear-gradient(0deg, rgba(0,0,0,0.08), rgba(0,0,0,0.08) 1px, transparent 1px, transparent 2px)',
        pointerEvents: 'none',
        borderRadius: '50%'
      }} />
      <canvas 
        ref={canvasRef} 
        style={{ width: '100%', height: '100%', display: 'block' }} 
      />
    </div>
  );
};

export default RadarCanvas;
