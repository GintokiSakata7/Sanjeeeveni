import React from 'react';
import {
  ArrowLeft,
  ArrowRight,
  Save,
  Clock,
  CheckCircle2,
  RotateCcw,
  Building2,
  LogIn,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { useHospitalRegistration } from '../hooks/useHospitalRegistration';
import { STEPPER_STEPS } from '../constants/hospitalConstants';

import Step1BasicInfo from '../components/Step1BasicInfo';
import Step2Address from '../components/Step2Address';
import Step3HospitalDetails from '../components/Step3HospitalDetails';
import Step4Administrator from '../components/Step4Administrator';
import Step5Documents from '../components/Step5Documents';
import Step6Integration from '../components/Step6Integration';
import Step7Review from '../components/Step7Review';

export default function HospitalRegistrationPage({ onBackToCitizen, onOpenLoginModal }) {
  const {
    currentStep,
    formData,
    lastSaved,
    isSubmitting,
    submissionResult,
    errorMsg,
    uploadingField,
    updateField,
    updateMultipleFields,
    handleFileUpload,
    goToStep,
    nextStep,
    prevStep,
    submitRegistration,
    clearDraft
  } = useHospitalRegistration();

  const progressPercent = Math.round((currentStep / 7) * 100);

  // Success View
  if (submissionResult && submissionResult.success) {
    return (
      <div className="hospital-login-page-root font-sans">
        <div className="login-page-header">
          <button type="button" className="btn-back-link" onClick={onBackToCitizen}>
            <ArrowLeft size={16} /> Return to Citizen SOS Engine
          </button>
          <div className="header-brand-tag">
            <Building2 size={18} className="text-cyan-400" />
            <span>Sanjeevani Hospital Network</span>
          </div>
        </div>

        <div className="registration-success-container">
          <div className="success-card">
            <div className="success-icon-badge">
              <CheckCircle2 size={54} className="text-emerald-400" />
            </div>
            <h2>Hospital Registration Submitted!</h2>
            <p className="success-subtitle">
              Your registration application has been filed under reference ID:
            </p>
            <div className="ref-id-box font-mono">{submissionResult.hospital_id}</div>

            <div className="status-timeline-card">
              <div className="status-pill pending">
                <Clock size={16} /> Verification Status: PENDING_VERIFICATION
              </div>
              <p className="status-explanation">
                Our clinical compliance team is reviewing your registration credentials and medical infrastructure details. You will receive an official notification once approved.
              </p>
            </div>

            <div className="success-actions mt-6">
              <button
                type="button"
                className="btn-primary-glow flex items-center justify-center gap-2"
                onClick={onOpenLoginModal}
              >
                <LogIn size={18} /> Proceed to Hospital Sign In
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="hospital-login-page-root font-sans">
      {/* Top Header Bar */}
      <div className="login-page-header">
        <button type="button" className="btn-back-link" onClick={onOpenLoginModal}>
          <ArrowLeft size={16} /> Back to Hospital Sign In
        </button>

        <div className="header-brand-tag">
          <Building2 size={18} className="text-cyan-400" />
          <span>Sanjeevani Hospital Registration</span>
        </div>

        {/* Draft Auto-Save Badge */}
        <div className="draft-save-indicator">
          {lastSaved ? (
            <span className="saved-badge">
              <Save size={13} /> Draft Saved ({lastSaved.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })})
            </span>
          ) : (
            <span className="unsaved-badge">Draft Ready</span>
          )}
          <button
            type="button"
            className="clear-draft-btn"
            title="Reset form draft"
            onClick={() => {
              if (window.confirm('Clear all draft fields and start over?')) {
                clearDraft();
              }
            }}
          >
            <RotateCcw size={12} /> Reset
          </button>
        </div>
      </div>

      {/* Main Split Layout: Sidebar Navigation + Form Container */}
      <div className="hospital-registration-split-layout">
        {/* Left Sidebar: Step Navigation & Progress */}
        <div className="reg-sidebar-panel">
          <div className="sidebar-header font-sans">
            <div className="brand-pill">
              <Sparkles size={14} className="text-cyan-400" /> Healthcare Provider Network
            </div>
            <h3>Hospital Onboarding</h3>
            <p>Complete facility registration to join Sanjeevani's emergency telemetry network</p>

            {/* Overall Progress Bar */}
            <div className="sidebar-progress-box mt-4">
              <div className="flex justify-between text-xs font-bold mb-1 text-slate-300">
                <span>Registration Progress</span>
                <span className="text-cyan-400 font-mono">{progressPercent}%</span>
              </div>
              <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                <div
                  className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-full transition-all duration-300"
                  style={{ width: `${progressPercent}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Vertical Stepper Steps Index */}
          <div className="vertical-stepper-list mt-6">
            {STEPPER_STEPS.map((step) => {
              const isCompleted = step.id < currentStep;
              const isActive = step.id === currentStep;

              return (
                <div
                  key={step.id}
                  className={`vertical-step-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
                  onClick={() => goToStep(step.id)}
                >
                  <div className="step-circle font-mono">
                    {isCompleted ? <CheckCircle2 size={16} /> : step.id}
                  </div>
                  <div className="step-label-group">
                    <span className="step-title">{step.label}</span>
                    <span className="step-sub">{step.desc}</span>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Bottom Security Compliance Badge */}
          <div className="sidebar-compliance-card mt-6">
            <ShieldCheck size={20} className="text-emerald-400 shrink-0" />
            <div>
              <h6>Verified Security Standard</h6>
              <p>256-bit SSL Data Encryption for HIPAA & NHA Trust Compliance</p>
            </div>
          </div>
        </div>

        {/* Right Content Area: Active Step Form */}
        <div className="reg-main-content">
          {errorMsg && (
            <div className="step-error-alert mb-4">
              <span>⚠️ {errorMsg}</span>
            </div>
          )}

          {/* Active Step Component */}
          <div className="step-content-wrapper">
            {currentStep === 1 && (
              <Step1BasicInfo formData={formData} updateField={updateField} />
            )}
            {currentStep === 2 && (
              <Step2Address
                formData={formData}
                updateField={updateField}
                updateMultipleFields={updateMultipleFields}
              />
            )}
            {currentStep === 3 && (
              <Step3HospitalDetails formData={formData} updateField={updateField} />
            )}
            {currentStep === 4 && (
              <Step4Administrator formData={formData} updateField={updateField} />
            )}
            {currentStep === 5 && (
              <Step5Documents
                formData={formData}
                handleFileUpload={handleFileUpload}
                uploadingField={uploadingField}
              />
            )}
            {currentStep === 6 && (
              <Step6Integration formData={formData} updateField={updateField} />
            )}
            {currentStep === 7 && (
              <Step7Review
                formData={formData}
                goToStep={goToStep}
                submitRegistration={submitRegistration}
                isSubmitting={isSubmitting}
                errorMsg={errorMsg}
              />
            )}
          </div>

          {/* Sleek Step Footer Controls */}
          {currentStep < 7 && (
            <div className="reg-footer-nav font-sans">
              <button
                type="button"
                className="btn-step-prev"
                disabled={currentStep === 1}
                onClick={prevStep}
              >
                <ArrowLeft size={16} /> Back
              </button>

              <div className="footer-step-counter font-mono">
                Step {currentStep} of 7
              </div>

              <button type="button" className="btn-step-next" onClick={nextStep}>
                Next Step <ArrowRight size={16} />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
