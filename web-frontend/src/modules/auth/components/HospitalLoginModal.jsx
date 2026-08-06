import React, { useState } from 'react';
import { X, LogIn, Mail, Lock, Building2, ShieldAlert, Clock, CheckCircle2 } from 'lucide-react';
import { loginHospital } from '../../hospital/services/hospitalApi';

export default function HospitalLoginModal({ isOpen, onClose, onStartRegistration }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [loggedInUser, setLoggedInUser] = useState(null);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg('');
    try {
      const result = await loginHospital(email, password);
      setLoggedInUser(result);
    } catch (err) {
      setErrorMsg(err.message || 'Login failed. Please check credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="modal-backdrop font-sans">
      <div className="modal-card">
        {/* Modal Header */}
        <div className="modal-header">
          <div className="modal-title-group">
            <Building2 className="text-cyan-400" size={24} />
            <div>
              <h3>Sanjeevani Hospital Portal</h3>
              <p>Administrator & Medical Personnel Login</p>
            </div>
          </div>
          <button type="button" className="close-modal-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        {loggedInUser ? (
          /* Successful Auth / Pending Status View */
          <div className="login-success-view">
            <div className="status-badge-container">
              {loggedInUser.status === 'PENDING_VERIFICATION' ? (
                <div className="pending-verification-box">
                  <Clock size={32} className="text-amber-400 mb-2" />
                  <h4>Registration Status: PENDING_VERIFICATION</h4>
                  <p>
                    Welcome, <strong>{loggedInUser.admin_name}</strong>! Account for <strong>{loggedInUser.hospital_name}</strong> has been registered. Full dashboard & API features will unlock once administrative verification completes.
                  </p>
                </div>
              ) : (
                <div className="approved-verification-box">
                  <CheckCircle2 size={32} className="text-emerald-400 mb-2" />
                  <h4>Hospital Dashboard Access Granted</h4>
                  <p>
                    Welcome back, <strong>{loggedInUser.admin_name}</strong> ({loggedInUser.hospital_name}).
                  </p>
                </div>
              )}
            </div>

            <button
              type="button"
              className="btn-primary-glow w-full mt-4"
              onClick={onClose}
            >
              Continue to Application
            </button>
          </div>
        ) : (
          /* Login Form */
          <form onSubmit={handleSubmit} className="modal-form">
            {errorMsg && (
              <div className="error-banner mb-4">
                <ShieldAlert size={18} className="shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <div className="form-group">
              <label>Administrator Email Address</label>
              <div className="input-icon-wrapper">
                <Mail size={18} className="input-left-icon" />
                <input
                  type="email"
                  placeholder="admin@hospital.org"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label>Password</label>
              <div className="input-icon-wrapper">
                <Lock size={18} className="input-left-icon" />
                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              className="btn-login-submit"
              disabled={isLoading}
            >
              {isLoading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="spinner"></span> Authenticating...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <LogIn size={18} /> Sign In to Hospital Dashboard
                </span>
              )}
            </button>

            <div className="modal-footer-link">
              <span>Don't have a hospital account?</span>
              <button
                type="button"
                className="start-reg-link"
                onClick={() => {
                  onClose();
                  onStartRegistration();
                }}
              >
                Register Your Hospital Now
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
