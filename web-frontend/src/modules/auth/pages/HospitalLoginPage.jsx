import React, { useState } from 'react';
import {
  Building2,
  Mail,
  Lock,
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  Activity,
  LogIn,
  CheckCircle2,
  Clock,
  ShieldAlert,
  Sparkles
} from 'lucide-react';
import { loginHospital } from '../../hospital/services/hospitalApi';

export default function HospitalLoginPage({
  onBackToCitizen,
  onStartRegistration
}) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [loggedInUser, setLoggedInUser] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg('');
    try {
      const result = await loginHospital(email, password);
      setLoggedInUser(result);
    } catch (err) {
      setErrorMsg(err.message || 'Invalid administrator email or password.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="hospital-login-page-root font-sans">
      {/* Top Header Bar */}
      <div className="login-page-header">
        <button type="button" className="btn-back-link" onClick={onBackToCitizen}>
          <ArrowLeft size={16} /> Back to Citizen SOS Engine
        </button>

        <div className="header-brand-tag">
          <Building2 size={18} className="text-cyan-400" />
          <span>Sanjeevani Hospital Portal</span>
        </div>
      </div>

      {/* Main Split Layout Container */}
      <div className="hospital-login-split-container">
        {/* Left Side: Professional Medical Brand Feature Showcase */}
        <div className="login-showcase-panel">
          <div className="showcase-content">
            <div className="brand-pill font-sans">
              <Sparkles size={14} className="text-cyan-400" /> NHA & ABDM Compliant Portal
            </div>

            <h1 className="showcase-title">
              Next-Gen Emergency Medical Command & Control
            </h1>

            <p className="showcase-desc">
              Seamless emergency dispatch telemetry, live bed capacity tracking, and direct ambulance orchestration for verified hospitals.
            </p>

            {/* Feature Highlights Grid */}
            <div className="showcase-features-grid font-sans">
              <div className="feature-item">
                <div className="feature-icon-box bg-cyan-950/80 border-cyan-800">
                  <Activity className="text-cyan-400" size={20} />
                </div>
                <div>
                  <h5>Live Bed Availability</h5>
                  <p>Real-time ICU and casualty bed tracking</p>
                </div>
              </div>

              <div className="feature-item">
                <div className="feature-icon-box bg-emerald-950/80 border-emerald-800">
                  <ShieldCheck className="text-emerald-400" size={20} />
                </div>
                <div>
                  <h5>Verified Multi-Tenancy</h5>
                  <p>Encrypted healthcare identity & verification</p>
                </div>
              </div>

              <div className="feature-item">
                <div className="feature-icon-box bg-purple-950/80 border-purple-800">
                  <Building2 className="text-purple-400" size={20} />
                </div>
                <div>
                  <h5>HL7 FHIR & REST API</h5>
                  <p>Direct connectivity with HIS & EHR systems</p>
                </div>
              </div>
            </div>

            {/* Stat Badges */}
            <div className="showcase-stats font-sans">
              <div className="stat-badge font-mono">
                <strong>99.9%</strong>
                <span>Uptime SLA</span>
              </div>
              <div className="stat-badge font-mono">
                <strong>&lt; 30s</strong>
                <span>Dispatch Triage</span>
              </div>
              <div className="stat-badge font-mono">
                <strong>256-bit</strong>
                <span>AES Encryption</span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Side: Professional Dedicated Login Form Card */}
        <div className="login-form-panel">
          <div className="login-card font-sans">
            {loggedInUser ? (
              /* Authenticated Account Status View */
              <div className="login-success-state">
                {loggedInUser.status === 'PENDING_VERIFICATION' ? (
                  <div className="status-box pending-box">
                    <Clock size={40} className="text-amber-400 mb-3" />
                    <h3>Registration Pending Verification</h3>
                    <p className="status-msg">
                      Account registered for <strong>{loggedInUser.hospital_name}</strong>.
                      Our clinical team is auditing your verification documents. Once approved, complete portal access will be granted.
                    </p>
                    <div className="hospital-ref-pill font-mono">
                      Ref ID: {loggedInUser.hospital_id}
                    </div>
                  </div>
                ) : (
                  <div className="status-box approved-box">
                    <CheckCircle2 size={40} className="text-emerald-400 mb-3" />
                    <h3>Welcome Back to Hospital Command</h3>
                    <p className="status-msg">
                      Authenticated as <strong>{loggedInUser.admin_name}</strong> ({loggedInUser.hospital_name}).
                    </p>
                  </div>
                )}

                <button
                  type="button"
                  className="btn-full-primary mt-6"
                  onClick={onBackToCitizen}
                >
                  Return to Main Application
                </button>
              </div>
            ) : (
              /* Professional Sign-In Form */
              <div className="login-form-wrapper">
                <div className="form-header">
                  <h2>Hospital Sign In</h2>
                  <p>Enter your administrator credentials to access your hospital portal</p>
                </div>

                {errorMsg && (
                  <div className="login-error-alert">
                    <ShieldAlert size={18} className="shrink-0 text-red-400" />
                    <span>{errorMsg}</span>
                  </div>
                )}

                <form onSubmit={handleSubmit} className="dedicated-form">
                  <div className="form-field">
                    <label>Official Administrator Email *</label>
                    <div className="field-input-box">
                      <Mail size={18} className="field-icon" />
                      <input
                        type="email"
                        placeholder="admin@hospital.org"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <div className="form-field">
                    <div className="flex justify-between items-center mb-1">
                      <label>Portal Password *</label>
                      <button
                        type="button"
                        className="toggle-pass-link"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? 'Hide' : 'Show'}
                      </button>
                    </div>
                    <div className="field-input-box">
                      <Lock size={18} className="field-icon" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                      />
                    </div>
                  </div>

                  <button
                    type="submit"
                    className="btn-dedicated-login"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="flex items-center justify-center gap-2">
                        <span className="spinner"></span> Authenticating Credentials...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-2">
                        <LogIn size={18} /> Sign In to Hospital Portal
                      </span>
                    )}
                  </button>
                </form>

                {/* Prominent Hospital Registration Action Card */}
                <div className="registration-callout-card">
                  <div className="callout-content">
                    <h4>Unregistered Hospital Facility?</h4>
                    <p>Register your hospital with Sanjeevani to join our emergency response network.</p>
                  </div>
                  <button
                    type="button"
                    className="btn-start-reg"
                    onClick={onStartRegistration}
                  >
                    Register Your Hospital <ArrowRight size={16} />

                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
