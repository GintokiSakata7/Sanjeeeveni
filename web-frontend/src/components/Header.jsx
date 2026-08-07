import React from 'react';
import { Sparkles, Building2, ShieldAlert } from 'lucide-react';

export default function Header({
  selectedLang,
  setSelectedLang,
  onOpenHospitalLogin,
  onOpenAdminLogin
}) {
  return (
    <header className="top-command-bar font-sans">
      <div className="brand-unit font-sans">
        <div className="brand-symbol">🚨</div>
        <div className="brand-title-group">
          <h1>Sanjeevani</h1>
          <p>Emergency Help System</p>
        </div>
      </div>

      <div className="header-right-actions font-sans">
        {/* Direct Hospital Portal Button */}
        <button
          type="button"
          className="hospital-portal-btn"
          onClick={onOpenHospitalLogin}
        >
          <Building2 size={16} className="text-cyan-400" />
          <span>Hospital Portal</span>
        </button>

        {/* Super Admin Authority Button */}
        <button
          type="button"
          className="hospital-portal-btn border-amber-500/40 text-amber-300 hover:border-amber-400"
          onClick={onOpenAdminLogin}
        >
          <ShieldAlert size={16} className="text-amber-400" />
          <span>Super Admin</span>
        </button>

        {/* Language Toolbar */}
        <div className="lang-toolbar font-sans">
          <button
            className={`lang-btn ${selectedLang === 'auto' ? 'active' : ''}`}
            onClick={() => setSelectedLang('auto')}
          >
            <Sparkles size={12} style={{ display: 'inline', marginRight: '4px' }} /> Auto
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
      </div>
    </header>
  );
}
