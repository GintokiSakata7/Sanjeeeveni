// Gesture and AI Fallback Doctor Media Assets Exporter
import cprVideo from './CPR demoin.mp4';
import cprImg from './Cpr.jpeg';
import pulseImg from './check pulse.jpeg';
import oxygenImg from './give the oxygen.jpeg';
import bleedingImg from './to stop the bleeding of injure.jpeg';

export const GESTURE_MEDIA_MAP = {
  cpr_video: {
    id: 'cpr_video',
    title: 'AI CPR Video Demonstration',
    type: 'video',
    src: cprVideo,
    badge: 'ANIMATED VIDEO DEMO',
    desc: 'Continuous high-quality chest compressions (100–120 BPM) and airway rescue breath cycles.'
  },
  cpr_technique: {
    id: 'cpr_technique',
    title: 'CPR Hand Position & Compression Form',
    type: 'image',
    src: cprImg,
    badge: 'HAND PLACEMENT',
    desc: 'Lock elbows straight. Interlock fingers on the lower half of the breastbone and compress 2 inches.'
  },
  check_pulse: {
    id: 'check_pulse',
    title: 'Carotid & Radial Pulse Verification',
    type: 'image',
    src: pulseImg,
    badge: 'VITAL SIGNS',
    desc: 'Check carotid pulse on neck groove for 5–10 seconds. Check radial pulse on wrist.'
  },
  airway_oxygen: {
    id: 'airway_oxygen',
    title: 'Airway Clearance & Oxygen Administration',
    type: 'image',
    src: oxygenImg,
    badge: 'AIRWAY & O2',
    desc: 'Perform head-tilt chin-lift maneuver. Place mask securely and deliver high-flow oxygen.'
  },
  stop_bleeding: {
    id: 'stop_bleeding',
    title: 'Arterial Bleeding & Wound Pressure',
    type: 'image',
    src: bleedingImg,
    badge: 'HEMOSTASIS',
    desc: 'Apply firm direct pressure with clean cloth. Elevate limb and apply emergency tourniquet if bleeding persists.'
  }
};
