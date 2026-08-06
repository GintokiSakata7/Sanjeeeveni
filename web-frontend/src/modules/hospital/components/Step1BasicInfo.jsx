import React from 'react';
import { Building2, ShieldCheck, Check, Monitor, Network } from 'lucide-react';
import { HOSPITAL_TYPES, HOSPITAL_CATEGORIES } from '../types/hospitalTypes';

export default function Step1BasicInfo({ formData, updateField }) {
  return (
    <div className="step-card">
      <div className="step-card-header">
        <Building2 className="step-icon text-cyan-400" size={24} />
        <div>
          <h3>Step 1: Hospital Facility Profile & Operational Setup</h3>
          <p>Select your hospital system architecture, category, and clinical credentials</p>
        </div>
      </div>

      {/* Professional System Operating Mode Selector */}
      <div className="mode-selection-container">
        <label className="field-label-main">Hospital System Operational Mode *</label>

        <div className="mode-grid">
          {/* Mode 1: Sanjeevani Built-In Hospital Management System */}
          <div
            className={`mode-card ${formData.hospital_type === HOSPITAL_TYPES.SMALL ? 'selected' : ''}`}
            onClick={() => updateField('hospital_type', HOSPITAL_TYPES.SMALL)}
          >
            <div className="mode-card-header">
              <span className="mode-badge small-badge">Sanjeevani Management System</span>
              {formData.hospital_type === HOSPITAL_TYPES.SMALL && <Check size={18} className="text-cyan-400" />}
            </div>
            <div className="flex items-center gap-2 mb-1">
              <Monitor size={18} className="text-cyan-400" />
              <h4>Sanjeevani Integrated Hospital Portal</h4>
            </div>
            <p>
              Use Sanjeevani's built-in web portal for complete hospital management, live bed availability tracking, and staff credential administration.
            </p>
            <div className="mode-perks">
              <span>✓ Native Web Command Dashboard</span>
              <span>✓ Doctor & Ambulance Login Management</span>
            </div>
          </div>

          {/* Mode 2: Connect External HIS / Custom API */}
          <div
            className={`mode-card ${formData.hospital_type === HOSPITAL_TYPES.LARGE ? 'selected' : ''}`}
            onClick={() => updateField('hospital_type', HOSPITAL_TYPES.LARGE)}
          >
            <div className="mode-card-header">
              <span className="mode-badge large-badge">External System Connectivity</span>
              {formData.hospital_type === HOSPITAL_TYPES.LARGE && <Check size={18} className="text-purple-400" />}
            </div>
            <div className="flex items-center gap-2 mb-1">
              <Network size={18} className="text-purple-400" />
              <h4>Connect External HIS / EHR System</h4>
            </div>
            <p>
              Connect your hospital's existing Information System (HIS / EHR / EMR) directly with Sanjeevani using REST APIs, HL7 FHIR standards, or webhooks.
            </p>
            <div className="mode-perks">
              <span>✓ REST API & HL7 FHIR Standard Adapters</span>
              <span>✓ Custom EHR Telemetry Webhooks</span>
            </div>
          </div>
        </div>
      </div>

      <div className="form-grid">
        {/* Hospital Name */}
        <div className="form-group col-span-2">
          <label>Hospital Name *</label>
          <input
            type="text"
            placeholder="e.g. Yashoda Hospitals & Research Centre"
            value={formData.hospital_name}
            onChange={(e) => updateField('hospital_name', e.target.value)}
            required
          />
        </div>

        {/* Category */}
        <div className="form-group">
          <label>Hospital Category *</label>
          <select
            value={formData.category}
            onChange={(e) => updateField('category', e.target.value)}
          >
            <option value={HOSPITAL_CATEGORIES.CHC}>CHC (Community Health Centre)</option>
            <option value={HOSPITAL_CATEGORIES.MULTI_SPECIALITY}>Multi-Speciality Hospital</option>
            <option value={HOSPITAL_CATEGORIES.SUPER_SPECIALITY}>Super-Speciality Hospital</option>
          </select>
        </div>

        {/* Registration Number */}
        <div className="form-group">
          <label>Clinical Registration Number *</label>
          <input
            type="text"
            placeholder="e.g. REG-TS-2024-8849"
            value={formData.registration_number}
            onChange={(e) => updateField('registration_number', e.target.value)}
            required
          />
        </div>

        {/* License Number */}
        <div className="form-group">
          <label>Government Medical License Number *</label>
          <input
            type="text"
            placeholder="e.g. GOVT-LIC-992144"
            value={formData.license_number}
            onChange={(e) => updateField('license_number', e.target.value)}
            required
          />
        </div>

        {/* GST Number */}
        <div className="form-group">
          <label>GSTIN (Optional)</label>
          <input
            type="text"
            placeholder="e.g. 36AABCU9603R1ZM"
            value={formData.gst_number}
            onChange={(e) => updateField('gst_number', e.target.value)}
          />
        </div>
      </div>

      {/* NABH Accreditation */}
      <div className="checkbox-section">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.has_nabh_accreditation}
            onChange={(e) => updateField('has_nabh_accreditation', e.target.checked)}
          />
          <ShieldCheck size={18} className="text-emerald-400" />
          <span>Hospital holds NABH (National Accreditation Board for Hospitals) Accreditation</span>
        </label>

        {formData.has_nabh_accreditation && (
          <div className="form-group mt-3">
            <label>NABH Certificate / Accreditation Number *</label>
            <input
              type="text"
              placeholder="e.g. NABH-2023-SPEC-0912"
              value={formData.nabh_number}
              onChange={(e) => updateField('nabh_number', e.target.value)}
            />
          </div>
        )}
      </div>
    </div>
  );
}
