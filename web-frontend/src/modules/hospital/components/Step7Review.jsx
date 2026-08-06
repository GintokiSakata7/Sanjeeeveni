import React, { useState } from 'react';
import { CheckCircle2, Edit3, Send, ShieldAlert, Building2, MapPin, BedDouble, UserCheck, UploadCloud, Network, ArrowRight } from 'lucide-react';

export default function Step7Review({
  formData,
  goToStep,
  submitRegistration,
  isSubmitting,
  errorMsg
}) {
  const [agreed, setAgreed] = useState(false);

  return (
    <div className="step-card">
      <div className="step-card-header">
        <CheckCircle2 className="step-icon text-emerald-400" size={24} />
        <div>
          <h3>Step 7: Final Review & Submission Audit</h3>
          <p>Carefully verify all hospital details before submitting for administrative verification</p>
        </div>
      </div>

      {errorMsg && (
        <div className="error-banner">
          <ShieldAlert size={20} className="shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Review Cards Grid */}
      <div className="review-sections-grid">
        {/* Step 1 Review */}
        <div className="review-card">
          <div className="review-card-title">
            <Building2 size={18} className="text-cyan-400" />
            <h4>1. Basic Information</h4>
            <button type="button" className="btn-edit" onClick={() => goToStep(1)}>
              <Edit3 size={14} /> Edit
            </button>
          </div>
          <div className="review-details-list">
            <div><span>Name:</span> <strong>{formData.hospital_name || 'N/A'}</strong></div>
            <div><span>Operating Mode:</span> <strong>{formData.hospital_type === 'SMALL' ? 'Sanjeevani Integrated Portal' : 'External HIS Integration'}</strong></div>

            <div><span>Category:</span> <strong>{formData.category}</strong></div>
            <div><span>Reg Number:</span> <strong>{formData.registration_number || 'N/A'}</strong></div>
            <div><span>Govt License:</span> <strong>{formData.license_number || 'N/A'}</strong></div>
            <div><span>NABH Accredited:</span> <strong>{formData.has_nabh_accreditation ? `Yes (${formData.nabh_number})` : 'No'}</strong></div>
            {formData.gst_number && <div><span>GSTIN:</span> <strong>{formData.gst_number}</strong></div>}
          </div>
        </div>

        {/* Step 2 Review */}
        <div className="review-card">
          <div className="review-card-title">
            <MapPin size={18} className="text-red-400" />
            <h4>2. Location & Address</h4>
            <button type="button" className="btn-edit" onClick={() => goToStep(2)}>
              <Edit3 size={14} /> Edit
            </button>
          </div>
          <div className="review-details-list">
            <div><span>City / State:</span> <strong>{formData.city}, {formData.state} ({formData.pincode})</strong></div>
            <div><span>Area:</span> <strong>{formData.area}</strong></div>
            <div><span>Complete Address:</span> <strong>{formData.complete_address || 'N/A'}</strong></div>
            <div><span>Coordinates:</span> <strong>{formData.latitude}, {formData.longitude}</strong></div>
          </div>
        </div>

        {/* Step 3 Review */}
        <div className="review-card">
          <div className="review-card-title">
            <BedDouble size={18} className="text-amber-400" />
            <h4>3. Capacity & Infrastructure</h4>
            <button type="button" className="btn-edit" onClick={() => goToStep(3)}>
              <Edit3 size={14} /> Edit
            </button>
          </div>
          <div className="review-details-list">
            <div><span>Total Beds:</span> <strong>{formData.total_beds}</strong></div>
            <div><span>ICU Beds:</span> <strong>{formData.icu_beds}</strong></div>
            <div><span>Ambulances:</span> <strong>{formData.ambulance_count}</strong></div>
            <div><span>Emergency Dept:</span> <strong>{formData.has_emergency_dept ? 'Active (24/7)' : 'No'}</strong></div>
            <div><span>Trauma Center:</span> <strong>{formData.has_trauma_center ? 'Yes' : 'No'}</strong></div>
            <div><span>Departments:</span> <strong>{(formData.departments || []).join(', ') || 'None selected'}</strong></div>
          </div>
        </div>

        {/* Step 4 Review */}
        <div className="review-card">
          <div className="review-card-title">
            <UserCheck size={18} className="text-emerald-400" />
            <h4>4. Administrator Credentials</h4>
            <button type="button" className="btn-edit" onClick={() => goToStep(4)}>
              <Edit3 size={14} /> Edit
            </button>
          </div>
          <div className="review-details-list">
            <div><span>Name:</span> <strong>{formData.admin_name || 'N/A'}</strong></div>
            <div><span>Designation:</span> <strong>{formData.admin_designation || 'N/A'}</strong></div>
            <div><span>Email (Login ID):</span> <strong>{formData.admin_email || 'N/A'}</strong></div>
            <div><span>Mobile:</span> <strong>{formData.admin_mobile || 'N/A'}</strong></div>
          </div>
        </div>

        {/* Step 5 Review */}
        <div className="review-card">
          <div className="review-card-title">
            <UploadCloud size={18} className="text-indigo-400" />
            <h4>5. Verification Documents</h4>
            <button type="button" className="btn-edit" onClick={() => goToStep(5)}>
              <Edit3 size={14} /> Edit
            </button>
          </div>
          <div className="review-details-list">
            <div><span>Reg Cert:</span> <strong>{formData.registration_cert_url ? 'Uploaded ✓' : 'Pending'}</strong></div>
            <div><span>Govt License:</span> <strong>{formData.govt_license_url ? 'Uploaded ✓' : 'Pending'}</strong></div>
            <div><span>PAN Document:</span> <strong>{formData.pan_url ? 'Uploaded ✓' : 'Pending'}</strong></div>
            <div><span>Exterior Photo:</span> <strong>{formData.exterior_image_url ? 'Uploaded ✓' : 'Pending'}</strong></div>
            <div><span>Hospital Logo:</span> <strong>{formData.logo_url ? 'Uploaded ✓' : 'Pending'}</strong></div>
          </div>
        </div>

        {/* Step 6 Review */}
        <div className="review-card">
          <div className="review-card-title">
            <Network size={18} className="text-teal-400" />
            <h4>6. Integration Mode</h4>
            <button type="button" className="btn-edit" onClick={() => goToStep(6)}>
              <Edit3 size={14} /> Edit
            </button>
          </div>
          <div className="review-details-list">
            <div><span>Mode:</span> <strong>{formData.hospital_type === 'SMALL' ? 'Sanjeevani Dashboard' : formData.integration_mode}</strong></div>
            {formData.base_url && <div><span>Base URL:</span> <strong>{formData.base_url}</strong></div>}
            {formData.tech_contact_name && <div><span>Tech Contact:</span> <strong>{formData.tech_contact_name}</strong></div>}
          </div>
        </div>
      </div>

      {/* Registration Workflow Sequence Visualizer */}
      <div className="workflow-sequence-card mt-6">
        <h5>Registration Verification Workflow</h5>
        <div className="workflow-steps-flex">
          <div className="wf-node active">
            <span>Submit Registration</span>
          </div>
          <ArrowRight size={16} className="text-slate-500" />
          <div className="wf-node">
            <span>Pending Verification</span>
          </div>
          <ArrowRight size={16} className="text-slate-500" />
          <div className="wf-node">
            <span>Admin Review</span>
          </div>
          <ArrowRight size={16} className="text-slate-500" />
          <div className="wf-node">
            <span>Approved / Rejected</span>
          </div>
          <ArrowRight size={16} className="text-slate-500" />
          <div className="wf-node">
            <span>Login Enabled</span>
          </div>
        </div>
      </div>

      {/* Terms Checkbox & Final Submit Button */}
      <div className="submit-section-card mt-6">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={agreed}
            onChange={(e) => setAgreed(e.target.checked)}
          />
          <span>
            I hereby certify that all uploaded documents and medical infrastructure details are accurate and compliant with National Health Authority regulations.
          </span>
        </label>

        <button
          type="button"
          className="btn-submit-final"
          disabled={!agreed || isSubmitting}
          onClick={submitRegistration}
        >
          {isSubmitting ? (
            <span className="flex items-center gap-2">
              <span className="spinner"></span> Processing Registration...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <Send size={18} /> Submit Hospital Registration
            </span>
          )}
        </button>
      </div>
    </div>
  );
}
