import React from 'react';
import { BedDouble, Stethoscope, Activity, HeartPulse, Ambulance, Plus, X } from 'lucide-react';
import { MEDICAL_DEPARTMENTS, SPECIALIZATIONS } from '../constants/hospitalConstants';

export default function Step3HospitalDetails({ formData, updateField }) {
  const toggleDepartment = (dept) => {
    const current = formData.departments || [];
    if (current.includes(dept)) {
      updateField('departments', current.filter((d) => d !== dept));
    } else {
      updateField('departments', [...current, dept]);
    }
  };

  const toggleSpecialization = (spec) => {
    const current = formData.specializations || [];
    if (current.includes(spec)) {
      updateField('specializations', current.filter((s) => s !== spec));
    } else {
      updateField('specializations', [...current, spec]);
    }
  };

  return (
    <div className="step-card">
      <div className="step-card-header">
        <BedDouble className="step-icon text-amber-400" size={24} />
        <div>
          <h3>Step 3: Hospital Capacity & Specializations</h3>
          <p>Specify total bed capacity, critical care infrastructure, and medical departments</p>
        </div>
      </div>

      <div className="form-grid">
        {/* Total Beds */}
        <div className="form-group">
          <label>Total Hospital Beds *</label>
          <input
            type="number"
            min="0"
            value={formData.total_beds}
            onChange={(e) => updateField('total_beds', e.target.value)}
          />
        </div>

        {/* ICU Beds */}
        <div className="form-group">
          <label>ICU / Critical Care Beds *</label>
          <input
            type="number"
            min="0"
            value={formData.icu_beds}
            onChange={(e) => updateField('icu_beds', e.target.value)}
          />
        </div>

        {/* Ambulance Count */}
        <div className="form-group">
          <label>Active Ambulances Owned *</label>
          <input
            type="number"
            min="0"
            value={formData.ambulance_count}
            onChange={(e) => updateField('ambulance_count', e.target.value)}
          />
        </div>
      </div>

      {/* Infrastructure Toggles */}
      <div className="infra-toggles-grid">
        <label className={`toggle-card ${formData.has_emergency_dept ? 'active' : ''}`}>
          <input
            type="checkbox"
            checked={formData.has_emergency_dept}
            onChange={(e) => updateField('has_emergency_dept', e.target.checked)}
          />
          <Activity className="toggle-icon text-red-400" size={20} />
          <div>
            <strong>24/7 Emergency Department</strong>
            <p>Dedicated casualty intake unit</p>
          </div>
        </label>

        <label className={`toggle-card ${formData.has_trauma_center ? 'active' : ''}`}>
          <input
            type="checkbox"
            checked={formData.has_trauma_center}
            onChange={(e) => updateField('has_trauma_center', e.target.checked)}
          />
          <HeartPulse className="toggle-icon text-amber-400" size={20} />
          <div>
            <strong>Level 1 / 2 Trauma Center</strong>
            <p>Specialized surgical trauma care</p>
          </div>
        </label>

        <label className={`toggle-card ${formData.has_blood_bank ? 'active' : ''}`}>
          <input
            type="checkbox"
            checked={formData.has_blood_bank}
            onChange={(e) => updateField('has_blood_bank', e.target.checked)}
          />
          <Ambulance className="toggle-icon text-pink-400" size={20} />
          <div>
            <strong>In-House Blood Bank</strong>
            <p>Blood storage and transfusion facility</p>
          </div>
        </label>
      </div>

      {/* Departments Selection */}
      <div className="chips-section">
        <label className="field-label-main">Active Medical Departments *</label>
        <div className="chips-container">
          {MEDICAL_DEPARTMENTS.map((dept) => {
            const isSelected = (formData.departments || []).includes(dept);
            return (
              <button
                key={dept}
                type="button"
                className={`chip-btn ${isSelected ? 'selected' : ''}`}
                onClick={() => toggleDepartment(dept)}
              >
                {isSelected ? <X size={14} /> : <Plus size={14} />}
                {dept}
              </button>
            );
          })}
        </div>
      </div>

      {/* Specializations Selection */}
      <div className="chips-section mt-4">
        <label className="field-label-main">Medical Specializations & Expertise</label>
        <div className="chips-container">
          {SPECIALIZATIONS.map((spec) => {
            const isSelected = (formData.specializations || []).includes(spec);
            return (
              <button
                key={spec}
                type="button"
                className={`chip-btn ${isSelected ? 'selected' : ''}`}
                onClick={() => toggleSpecialization(spec)}
              >
                {isSelected ? <X size={14} /> : <Plus size={14} />}
                {spec}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
