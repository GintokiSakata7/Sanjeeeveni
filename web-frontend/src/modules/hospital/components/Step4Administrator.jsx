import React, { useState } from 'react';
import { UserCheck, Key, Mail, Phone, Lock, ShieldAlert, CheckCircle2 } from 'lucide-react';

export default function Step4Administrator({ formData, updateField }) {
  const [showPassword, setShowPassword] = useState(false);

  const getPasswordStrength = (pass) => {
    if (!pass) return { score: 0, text: 'Empty', color: 'bg-slate-700' };
    let score = 0;
    if (pass.length >= 6) score += 1;
    if (pass.length >= 10) score += 1;
    if (/[A-Z]/.test(pass)) score += 1;
    if (/[0-9]/.test(pass)) score += 1;
    if (/[^A-Za-z0-9]/.test(pass)) score += 1;

    if (score <= 2) return { score: 33, text: 'Weak', color: 'bg-red-500' };
    if (score <= 4) return { score: 66, text: 'Medium', color: 'bg-amber-500' };
    return { score: 100, text: 'Strong', color: 'bg-emerald-500' };
  };

  const strength = getPasswordStrength(formData.admin_password);
  const isMatch = formData.admin_password && formData.admin_password === formData.admin_confirm_password;

  return (
    <div className="step-card">
      <div className="step-card-header">
        <UserCheck className="step-icon text-emerald-400" size={24} />
        <div>
          <h3>Step 4: Primary Administrator Account</h3>
          <p>Create login credentials for the hospital authority administering this portal</p>
        </div>
      </div>

      <div className="form-grid">
        {/* Administrator Name */}
        <div className="form-group">
          <label>Administrator Full Name *</label>
          <input
            type="text"
            placeholder="e.g. Dr. Rajesh Sharma"
            value={formData.admin_name}
            onChange={(e) => updateField('admin_name', e.target.value)}
            required
          />
        </div>

        {/* Designation */}
        <div className="form-group">
          <label>Designation *</label>
          <input
            type="text"
            placeholder="e.g. Medical Director / Chief Administrator"
            value={formData.admin_designation}
            onChange={(e) => updateField('admin_designation', e.target.value)}
            required
          />
        </div>

        {/* Email */}
        <div className="form-group">
          <label>Official Email Address (Login ID) *</label>
          <input
            type="email"
            placeholder="admin@yashodahospitals.org"
            value={formData.admin_email}
            onChange={(e) => updateField('admin_email', e.target.value)}
            required
          />
        </div>

        {/* Mobile */}
        <div className="form-group">
          <label>Mobile Number *</label>
          <input
            type="tel"
            placeholder="+91 98765 43210"
            value={formData.admin_mobile}
            onChange={(e) => updateField('admin_mobile', e.target.value)}
            required
          />
        </div>

        {/* Password */}
        <div className="form-group">
          <label>Portal Password *</label>
          <div className="input-with-icon">
            <input
              type={showPassword ? 'text' : 'password'}
              placeholder="Minimum 6 characters"
              value={formData.admin_password}
              onChange={(e) => updateField('admin_password', e.target.value)}
              required
            />
            <button
              type="button"
              className="toggle-pass-btn"
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? 'Hide' : 'Show'}
            </button>
          </div>

          {/* Password Strength Meter */}
          {formData.admin_password && (
            <div className="pass-strength-bar mt-2 font-sans text-xs">
              <div className="flex justify-between mb-1">
                <span>Strength: <strong>{strength.text}</strong></span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                <div
                  className={`h-full ${strength.color} transition-all duration-300`}
                  style={{ width: `${strength.score}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* Confirm Password */}
        <div className="form-group">
          <label>Confirm Password *</label>
          <input
            type={showPassword ? 'text' : 'password'}
            placeholder="Re-enter password"
            value={formData.admin_confirm_password}
            onChange={(e) => updateField('admin_confirm_password', e.target.value)}
            required
          />
          {formData.admin_confirm_password && (
            <div className="mt-1 flex items-center text-xs gap-1 font-sans">
              {isMatch ? (
                <span className="text-emerald-400 flex items-center gap-1">
                  <CheckCircle2 size={13} /> Passwords match
                </span>
              ) : (
                <span className="text-red-400 flex items-center gap-1">
                  <ShieldAlert size={13} /> Passwords do not match
                </span>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
