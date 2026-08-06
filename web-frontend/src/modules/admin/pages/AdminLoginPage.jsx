import React, { useState } from 'react';
import { ShieldAlert, Lock, Mail, ArrowLeft, LogIn, Sparkles, Building2, CheckCircle2 } from 'lucide-react';

export default function AdminLoginPage({ onAdminLoginSuccess, onBackToCitizen }) {
  const [email, setEmail] = useState('admin@sanjeevani.com');
  const [password, setPassword] = useState('SanjeevaniAdmin2026!');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Authentication failed. Please check credentials.');
      }

      // Save admin session
      localStorage.setItem('sanjeevani_admin_token', data.access_token);
      localStorage.setItem('sanjeevani_admin_user', JSON.stringify(data));

      onAdminLoginSuccess(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="hospital-login-page-root font-sans">
      {/* Top Header Bar */}
      <div className="login-page-header">
        <button type="button" className="btn-back-link" onClick={onBackToCitizen}>
          <ArrowLeft size={16} /> Return to Citizen SOS Engine
        </button>

        <div className="header-brand-tag">
          <ShieldAlert size={18} className="text-amber-400" />
          <span>Sanjeevani Central Authority</span>
        </div>
      </div>

      {/* Split Screen Container */}
      <div className="hospital-login-split-container">
        {/* Left Side: Authority Branding Showcase */}
        <div className="login-showcase-panel">
          <div className="showcase-badge font-sans">
            <Sparkles size={14} className="text-amber-400" /> Super Admin Portal
          </div>
          <h1 className="showcase-title">
            State Emergency & <br />
            <span>Hospital Command Center</span>
          </h1>
          <p className="showcase-desc">
            Central administrative oversight for reviewing healthcare provider credentials, verifying NABH/GST compliance, and orchestrating emergency hospital telemetry.
          </p>

          <div className="showcase-features-list font-sans mt-6">
            <div className="feature-item">
              <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
              <span>Real-time Hospital Verification & Compliance Audit</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
              <span>Statewide Bed & ICU Capacity Monitoring</span>
            </div>
            <div className="feature-item">
              <CheckCircle2 size={16} className="text-emerald-400 shrink-0" />
              <span>Custom HIS API Integration Management</span>
            </div>
          </div>
        </div>

        {/* Right Side: Super Admin Auth Form */}
        <div className="login-form-panel">
          <div className="dedicated-login-card font-sans">
            <div className="card-top-head">
              <div className="lock-icon-badge bg-amber-500/10 border-amber-500/30">
                <ShieldAlert size={28} className="text-amber-400" />
              </div>
              <h3>Super Admin Sign In</h3>
              <p>Enter your authorization credentials to access the command dashboard</p>
            </div>

            {error && (
              <div className="login-error-banner mb-4">
                <span>⚠️ {error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="dedicated-form">
              <div className="form-field">
                <label>Admin Access Email *</label>
                <div className="field-input-box">
                  <Mail size={18} className="field-icon" />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="admin@sanjeevani.com"
                    required
                  />
                </div>
              </div>

              <div className="form-field">
                <label>Security Key / Password *</label>
                <div className="field-input-box">
                  <Lock size={18} className="field-icon" />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    required
                  />
                </div>
              </div>

              <div className="demo-credentials-box mb-4">
                <span>🔑 Default Super Admin Login:</span>
                <code>admin@sanjeevani.com</code> / <code>SanjeevaniAdmin2026!</code>
              </div>

              <button
                type="submit"
                className="btn-dedicated-login bg-amber-600 hover:bg-amber-700 border-amber-500"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="spinner"></span> Authenticating Command Token...
                  </span>
                ) : (
                  <span className="flex items-center justify-center gap-2">
                    <LogIn size={18} /> Enter Sanjeevani Command Portal
                  </span>
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
