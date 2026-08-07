import React from 'react';
import { Mic, Radio, RotateCcw, Languages } from 'lucide-react';

const INDIAN_LANGUAGES = [
  { code: "auto", label: "✨ Auto-Detect (All Indian Languages)" },
  { code: "te-IN", label: "🇮🇳 Telugu (తెలుగు)" },
  { code: "hi-IN", label: "🇮🇳 Hindi (हिंदी / Gangetic Dialects)" },
  { code: "ta-IN", label: "🇮🇳 Tamil (தமிழ்)" },
  { code: "kn-IN", label: "🇮🇳 Kannada (ಕನ್ನಡ)" },
  { code: "ml-IN", label: "🇮🇳 Malayalam (മലയാളം)" },
  { code: "mr-IN", label: "🇮🇳 Marathi (मराठी)" },
  { code: "bn-IN", label: "🇮🇳 Bengali (বাংলা)" },
  { code: "gu-IN", label: "🇮🇳 Gujarati (ગુજરાતી)" },
  { code: "pa-IN", label: "🇮🇳 Punjabi (ਪੰਜਾਬੀ)" },
  { code: "or-IN", label: "🇮🇳 Odia (ଓଡ଼ိଆ)" },
  { code: "ur-IN", label: "🇮🇳 Urdu (اردو)" },
  { code: "en-IN", label: "🇬🇧 English (India)" },
];

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
  handleClear,
  hasAudioBlob
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
          {/* Multilingual Speech Engine Language Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '14px', background: 'var(--bg-subtle)', padding: '8px 14px', borderRadius: '12px', border: '1px solid var(--border-light)', width: '100%' }}>
            <Languages size={16} color="#2563EB" />
            <span style={{ fontSize: '11px', fontWeight: '700', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>WHISPER V3 STT ENGINE:</span>
            <select
              value={selectedLang}
              onChange={(e) => setSelectedLang(e.target.value)}
              style={{
                background: 'var(--bg-card)',
                color: 'var(--text-main)',
                border: '1px solid var(--border-light)',
                borderRadius: '8px',
                padding: '6px 10px',
                fontSize: '12px',
                fontWeight: '600',
                outline: 'none',
                width: '100%',
                cursor: 'pointer'
              }}
            >
              {INDIAN_LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.label}
                </option>
              ))}
            </select>
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
              ? "🎙️ Groq Whisper v3 Recording Active • Speak in any Indian language or dialect..."
              : hasAudioBlob
              ? "✅ Audio Recording Ready • Click Transmit SOS below or speak again"
              : "Tap Microphone Orb to record audio in any language"}
          </p>

          <div style={{ width: '100%', marginTop: '14px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: 'var(--text-muted)', fontWeight: '700' }}>
              <span>{selectedLang === "auto" ? "Live transcription disabled in Auto-Detect" : "What you said:"}</span>
              {transcript && selectedLang !== "auto" && (
                <button className="clear-link" onClick={handleClear}>
                  <RotateCcw size={12} style={{ display: 'inline' }} /> Clear
                </button>
              )}
            </div>
            
            {selectedLang === "auto" ? (
              <div className="transcript-box" style={{ minHeight: '60px', opacity: 0.7, padding: '10px', background: 'var(--bg-subtle)', borderRadius: '8px', border: '1px solid var(--border-light)' }}>
                <span className="placeholder" style={{ fontSize: '12px', lineHeight: '1.5' }}>
                  Voice is being securely recorded. The AI will automatically detect your language and transcribe it upon transmitting the SOS.
                  <br/><br/>
                  <i>(Select a specific language from the dropdown above if you want to see a live text preview here).</i>
                </span>
              </div>
            ) : (
              <textarea
                className="hud-textarea"
                value={transcript}
                onChange={(e) => setTranscript(e.target.value)}
                placeholder="Your words will appear here as you speak..."
                style={{ marginTop: '8px' }}
              />
            )}
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
