import React from 'react';
import { Activity } from 'lucide-react';

export default function CategoryPresets({ addSymptomPreset }) {
  return (
    <div className="hud-card">
      <div className="card-title-row">
        <h3><Activity size={18} color="#38BDF8" /> QUICK EMERGENCY CATEGORIES</h3>
      </div>

      <div className="preset-grid">
        <div className="preset-card" onClick={() => addSymptomPreset('Severe Chest Pain / Heart Attack')}>
          🫀 Chest Pain / Cardiac
        </div>
        <div className="preset-card" onClick={() => addSymptomPreset('Road Accident with severe bleeding')}>
          🚗 Accident / Bleeding
        </div>
        <div className="preset-card" onClick={() => addSymptomPreset('Difficulty breathing / Asthma attack')}>
          🫁 Breathlessness
        </div>
        <div className="preset-card" onClick={() => addSymptomPreset('Unconscious person collapsed')}>
          🧠 Stroke / Unconscious
        </div>
      </div>
    </div>
  );
}
