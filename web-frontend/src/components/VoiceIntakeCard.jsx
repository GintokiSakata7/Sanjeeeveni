import React from 'react';
import { Mic, Radio, RotateCcw, Languages } from 'lucide-react';

export default function VoiceIntakeCard({
  inputMode,
  setInputMode,
  selectedLang,
  setSelectedLang,
  isListening,
  toggleListening,
  transcript,
  setTranscript,
  typedText,
  setTypedText,
  handleClear
}) {
  return (
    <div className="hud-card">
      <div className="card-title-row">
        <h3><Radio size={18} color="#DC2626" /> EMERGENCY VOICE & SPEECH INTAKE</h3>
        <div style={{ display: 'flex', gap: '6px' }}>
          <button
            className={`lang-btn ${inputMode === 'voice' ? 'active' : ''}`}
            onClick={() => setInputMode('voice')}
          >
            Voice
          </button>
          <button
            className={`lang-btn ${inputMode === 'type' ? 'active' : ''}`}
            onClick={() => setInputMode('type')}
          >
            Type
          </button>
        </div>
      </div>

      {inputMode === 'voice' ? (
        <div className="voice-hud">
          {/* Speech Engine Language Selector */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', background: 'var(--bg-subtle)', padding: '6px 12px', borderRadius: '100px', border: '1px solid var(--border-light)' }}>
            <Languages size={14} color="var(--text-muted)" />
            <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)' }}>SPEECH ENGINE:</span>
            <button
              className={`lang-btn ${selectedLang === 'te-IN' ? 'active' : ''}`}
              onClick={() => setSelectedLang('te-IN')}
            >
              🇮🇳 Telugu Voice
            </button>
            <button
              className={`lang-btn ${selectedLang === 'hi-IN' ? 'active' : ''}`}
              onClick={() => setSelectedLang('hi-IN')}
            >
              🇮🇳 Hindi Voice
            </button>
            <button
              className={`lang-btn ${selectedLang === 'en-IN' ? 'active' : ''}`}
              onClick={() => setSelectedLang('en-IN')}
            >
              🇬🇧 English
            </button>
          </div>

          <button
            className={`voice-orb-btn ${isListening ? 'recording' : ''}`}
            onClick={toggleListening}
          >
            <Mic size={42} />
          </button>

          {/* Sound Equalizer Waveform */}
          <div className="wave-bars">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
              <div key={i} className={`wave-bar-unit ${isListening ? 'active' : ''}`}></div>
            ))}
          </div>

          <p style={{ fontSize: '13px', color: 'var(--text-sub)', marginTop: '10px', fontWeight: '600' }}>
            {isListening
              ? `🎙️ Listening in ${selectedLang === 'te-IN' ? 'Telugu (తెలుగు)' : selectedLang === 'hi-IN' ? 'Hindi (हिंदी)' : 'English'}... Speak clearly`
              : "Tap Microphone Orb to start speech intake"}
          </p>

          <div style={{ width: '100%', marginTop: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>
              <span>ACCUMULATED SPEECH TRANSCRIPT:</span>
              {transcript && (
                <button className="clear-link" onClick={handleClear}>
                  <RotateCcw size={12} style={{ display: 'inline' }} /> Clear
                </button>
              )}
            </div>
            <textarea
              className="hud-textarea"
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder={
                selectedLang === 'te-IN'
                  ? "మాట్లాడిన తెలుగు వాక్యాలు ఇక్కడ నమోదు చేయబడతాయి..."
                  : selectedLang === 'hi-IN'
                  ? "बोले गए हिंदी वाक्य यहाँ दर्ज किए जाएँगे..."
                  : "Spoken audio streams here continuously without loss across pauses..."
              }
            />
          </div>
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>
            <span>TYPE EMERGENCY DETAILS:</span>
            {typedText && (
              <button className="clear-link" onClick={handleClear}>
                <RotateCcw size={12} style={{ display: 'inline' }} /> Clear
              </button>
            )}
          </div>
          <textarea
            className="hud-textarea"
            value={typedText}
            onChange={(e) => setTypedText(e.target.value)}
            placeholder="Describe emergency symptoms (e.g., Na peru Bhanu Prakash, car accident jarigindi, heavy bleeding)..."
          />
        </div>
      )}
    </div>
  );
}
