import React from 'react';
import { Volume2, ShieldAlert, FileText, Globe, Stethoscope, AlertTriangle } from 'lucide-react';

export default function TriageResultCard({ triageResult, loading, speakFirstAid }) {
  if (loading) {
    return (
      <div className="loader-card">
        <div className="spinner-ring"></div>
        <h3 style={{ fontFamily: 'Outfit', fontSize: '20px' }}>Analyzing your emergency...</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-sub)', marginTop: '4px' }}>
          Please wait a moment while we process your request.
        </p>
      </div>
    );
  }

  if (!triageResult) {
    return (
      <div className="hud-card" style={{ textAlign: 'center', padding: '40px 20px' }}>
        <ShieldAlert size={48} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
        <h3 style={{ fontSize: '18px', color: 'var(--text-sub)' }}>Ready to Help</h3>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', marginTop: '6px' }}>
          Speak or type your emergency details on the left, and we will get you the right help immediately.
        </p>
      </div>
    );
  }

  const firstAidSteps = (triageResult.first_aid_native && triageResult.first_aid_native.length > 0)
    ? triageResult.first_aid_native
    : triageResult.first_aid_english;

  return (
    <div className="dispatch-hud-card">
      {/* Header Severity Banner */}
      <div className="dispatch-header">
        <div className="triage-pills">
          <span className="pill-red">
            🚨 {triageResult.severity.replace('_', ' ')}
          </span>
          <span className="pill-lang">
            🌐 Language: {triageResult.detected_language || "Auto-Detected"}
          </span>
        </div>
        <h2 className="dispatch-title">{triageResult.category}</h2>
        <p className="dispatch-sub">{triageResult.triage_summary}</p>
      </div>

      {/* Real AI Classification & Extraction Grid */}
      <div className="responders-grid">
        {/* Original Input */}
        <div className="responder-card">
          <div className="responder-icon">🗣️</div>
          <div className="responder-info">
            <h4>WHAT YOU SAID</h4>
            <strong style={{ fontSize: '13px', fontWeight: '600' }}>"{triageResult.input_text}"</strong>
            <p>Detected Language: {triageResult.detected_language}</p>
          </div>
        </div>

        {/* English Translation */}
        <div className="responder-card">
          <div className="responder-icon">🇬🇧</div>
          <div className="responder-info">
            <h4>CLINICAL ENGLISH TRANSLATION</h4>
            <strong style={{ fontSize: '13px', fontWeight: '600' }}>"{triageResult.translated_english}"</strong>
            <p>Prepared for Emergency Responders</p>
          </div>
        </div>

        {/* Chief Complaint & Doctor Specialty */}
        <div className="responder-card">
          <div className="responder-icon">🩺</div>
          <div className="responder-info">
            <h4>RECOMMENDED SPECIALIST</h4>
            <strong>{triageResult.recommended_doctor_specialty}</strong>
            <p>Chief Complaint: {triageResult.chief_complaint}</p>
          </div>
        </div>
      </div>

      {/* AI First Aid Steps */}
      <div className="firstaid-hud">
        <div className="firstaid-header-row">
          <h3>🩹 AI-Guided Step-by-Step First Aid ({triageResult.detected_language})</h3>
          <button className="tts-audio-btn" onClick={speakFirstAid}>
            <Volume2 size={16} /> Listen Guidance
          </button>
        </div>

        <div className="step-items-list">
          {firstAidSteps.map((step, idx) => (
            <div className="step-item-card" key={idx}>
              <div className="step-badge">{step.step_number || idx + 1}</div>
              <div>
                {step.icon || '⚠️'} {step.instruction}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
