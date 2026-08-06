import React from 'react';
import { Sparkles } from 'lucide-react';

export default function Header({ selectedLang, setSelectedLang }) {
  return (
    <header className="top-command-bar">
      <div className="brand-unit">
        <div className="brand-symbol">🚨</div>
        <div className="brand-title-group">
          <h1>AERO</h1>
          <p>AI EMERGENCY TRIAGE & CLASSIFICATION ENGINE</p>
        </div>
      </div>

      {/* Live System Stats Ticker */}
      <div className="header-ticker">
        <div className="ticker-item">
          <div className="ticker-dot"></div>
          <span>AI ENGINE ACTIVE</span>
        </div>
        <div className="ticker-item">
          <span>SOTA WHISPER & GEMINI 1.5</span>
        </div>
      </div>

      {/* Language Toolbar */}
      <div className="lang-toolbar">
        <button
          className={`lang-btn ${selectedLang === 'auto' ? 'active' : ''}`}
          onClick={() => setSelectedLang('auto')}
        >
          <Sparkles size={12} style={{ display: 'inline', marginRight: '4px' }} /> Auto Detect
        </button>
        <button
          className={`lang-btn ${selectedLang === 'en-US' ? 'active' : ''}`}
          onClick={() => setSelectedLang('en-US')}
        >
          EN
        </button>
        <button
          className={`lang-btn ${selectedLang === 'te-IN' ? 'active' : ''}`}
          onClick={() => setSelectedLang('te-IN')}
        >
          తెలుగు
        </button>
        <button
          className={`lang-btn ${selectedLang === 'hi-IN' ? 'active' : ''}`}
          onClick={() => setSelectedLang('hi-IN')}
        >
          हिंदी
        </button>
      </div>
    </header>
  );
}
