import React from 'react';
import { Network, Monitor, Code2, Server, CheckCircle2, UserCheck } from 'lucide-react';
import { HOSPITAL_TYPES, INTEGRATION_MODES } from '../types/hospitalTypes';

export default function Step6Integration({ formData, updateField }) {
  const isDashboardMode = formData.hospital_type === HOSPITAL_TYPES.SMALL;

  return (
    <div className="step-card">
      <div className="step-card-header">
        <Network className="step-icon text-teal-400" size={24} />
        <div>
          <h3>Step 6: System Integration & Gateway Setup</h3>
          <p>Configure operational mode and technical API endpoints for live emergency telemetry</p>
        </div>
      </div>

      {isDashboardMode ? (
        /* Native Sanjeevani Management System Banner */
        <div className="small-hospital-integration-banner font-sans">
          <div className="banner-icon-badge">
            <Monitor size={36} className="text-cyan-400" />
          </div>
          <h4>Sanjeevani Integrated Hospital Management Dashboard</h4>
          <p className="banner-desc">
            No external API configuration required! Your facility will manage live bed availability, casualty intake, and emergency dispatch directly through Sanjeevani's intuitive web command portal.
          </p>

          <div className="perks-grid">
            <div className="perk-box">
              <CheckCircle2 size={18} className="text-emerald-400" />
              <div>
                <strong>Zero Setup Overhead</strong>
                <p>Instant dashboard activation upon administrative verification</p>
              </div>
            </div>

            <div className="perk-box">
              <UserCheck size={18} className="text-cyan-400" />
              <div>
                <strong>Staff Credential Creation</strong>
                <p>Create dedicated login access for duty doctors and ambulance personnel</p>
              </div>
            </div>
          </div>
        </div>
      ) : (
        /* Custom HIS / EHR Integration Setup Form */
        <div className="large-hospital-integration-form font-sans">
          <label className="field-label-main">Select Preferred External Integration Protocol *</label>

          <div className="integration-mode-grid">
            {/* REST API Option */}
            <div
              className={`integ-card ${formData.integration_mode === INTEGRATION_MODES.REST_API ? 'selected' : ''}`}
              onClick={() => updateField('integration_mode', INTEGRATION_MODES.REST_API)}
            >
              <Code2 size={24} className="text-cyan-400 mb-2" />
              <h5>REST API Interface</h5>
              <p>Standard JSON webhooks and RESTful endpoints for bed sync & triage dispatch.</p>
            </div>

            {/* HL7 FHIR Option */}
            <div
              className={`integ-card ${formData.integration_mode === INTEGRATION_MODES.HL7_FHIR ? 'selected' : ''}`}
              onClick={() => updateField('integration_mode', INTEGRATION_MODES.HL7_FHIR)}
            >
              <Server size={24} className="text-purple-400 mb-2" />
              <h5>HL7 FHIR Protocol</h5>
              <p>Fast Healthcare Interoperability Resources standard format compliance.</p>
            </div>

            {/* Custom API Option */}
            <div
              className={`integ-card ${formData.integration_mode === INTEGRATION_MODES.CUSTOM_API ? 'selected' : ''}`}
              onClick={() => updateField('integration_mode', INTEGRATION_MODES.CUSTOM_API)}
            >
              <Network size={24} className="text-amber-400 mb-2" />
              <h5>Custom HIS / EHR Adapter</h5>
              <p>Proprietary hospital software connector managed via custom middleware.</p>
            </div>

            {/* Dashboard Option */}
            <div
              className={`integ-card ${formData.integration_mode === INTEGRATION_MODES.DASHBOARD ? 'selected' : ''}`}
              onClick={() => updateField('integration_mode', INTEGRATION_MODES.DASHBOARD)}
            >
              <Monitor size={24} className="text-emerald-400 mb-2" />
              <h5>Sanjeevani Web Portal (Interim)</h5>
              <p>Use Sanjeevani Web Portal while custom API integrations are under development.</p>
            </div>
          </div>

          {/* Technical Endpoints Form */}
          {formData.integration_mode !== INTEGRATION_MODES.DASHBOARD && (
            <div className="tech-endpoints-section form-grid mt-6">
              <div className="form-group">
                <label>Hospital Base API URL (Optional)</label>
                <input
                  type="url"
                  placeholder="https://api.yashodahospitals.org/v1"
                  value={formData.base_url}
                  onChange={(e) => updateField('base_url', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Webhook Callback URL (Optional)</label>
                <input
                  type="url"
                  placeholder="https://api.yashodahospitals.org/webhooks/sanjeevani"
                  value={formData.callback_url}
                  onChange={(e) => updateField('callback_url', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>API Documentation URL (Optional)</label>
                <input
                  type="url"
                  placeholder="https://developer.yashodahospitals.org/docs"
                  value={formData.api_doc_url}
                  onChange={(e) => updateField('api_doc_url', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Technical Lead Contact Name</label>
                <input
                  type="text"
                  placeholder="e.g. Anand Kumar (Head of IT)"
                  value={formData.tech_contact_name}
                  onChange={(e) => updateField('tech_contact_name', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>Technical Lead Email</label>
                <input
                  type="email"
                  placeholder="it-dev@yashodahospitals.org"
                  value={formData.tech_contact_email}
                  onChange={(e) => updateField('tech_contact_email', e.target.value)}
                />
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
