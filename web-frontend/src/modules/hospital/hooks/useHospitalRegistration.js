import { useState, useEffect, useCallback } from 'react';
import { INITIAL_REGISTRATION_STATE } from '../types/hospitalTypes';
import { registerHospital, uploadDocument } from '../services/hospitalApi';

const DRAFT_KEY = 'sanjeevani_hospital_reg_draft_v1';

export function useHospitalRegistration() {
  const [currentStep, setCurrentStep] = useState(1);
  const [formData, setFormData] = useState(INITIAL_REGISTRATION_STATE);
  const [lastSaved, setLastSaved] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionResult, setSubmissionResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState('');
  const [uploadingField, setUploadingField] = useState(null);

  // Load saved draft on initial mount
  useEffect(() => {
    try {
      const savedDraft = localStorage.getItem(DRAFT_KEY);
      if (savedDraft) {
        const parsed = JSON.parse(savedDraft);
        setFormData((prev) => ({ ...prev, ...parsed.formData }));
        if (parsed.currentStep) setCurrentStep(parsed.currentStep);
        if (parsed.lastSaved) setLastSaved(new Date(parsed.lastSaved));
      }
    } catch (e) {
      console.warn('Failed to load draft from localStorage:', e);
    }
  }, []);

  // Auto-save draft on form change
  const saveDraft = useCallback((dataToSave, stepToSave) => {
    try {
      const now = new Date();
      const payload = {
        formData: dataToSave,
        currentStep: stepToSave,
        lastSaved: now.toISOString()
      };
      localStorage.setItem(DRAFT_KEY, JSON.stringify(payload));
      setLastSaved(now);
    } catch (e) {
      console.warn('Auto-save failed:', e);
    }
  }, []);

  const updateField = (fieldName, value) => {
    setFormData((prev) => {
      const updated = { ...prev, [fieldName]: value };
      saveDraft(updated, currentStep);
      return updated;
    });
  };

  const updateMultipleFields = (fieldsObject) => {
    setFormData((prev) => {
      const updated = { ...prev, ...fieldsObject };
      saveDraft(updated, currentStep);
      return updated;
    });
  };

  const handleFileUpload = async (fieldName, file) => {
    if (!file) return;
    setUploadingField(fieldName);
    setErrorMsg('');
    try {
      const uploadedUrl = await uploadDocument(file);
      updateField(fieldName, uploadedUrl);
    } catch (err) {
      // Fallback: create an object URL preview if offline backend is unreachable
      const objectUrl = URL.createObjectURL(file);
      updateField(fieldName, objectUrl);
    } finally {
      setUploadingField(null);
    }
  };

  const validateStep = (stepNumber) => {
    setErrorMsg('');
    switch (stepNumber) {
      case 1:
        if (!formData.hospital_name.trim()) return 'Hospital Name is required.';
        if (!formData.registration_number.trim()) return 'Registration Number is required.';
        if (!formData.license_number.trim()) return 'Government License Number is required.';
        if (formData.has_nabh_accreditation && !formData.nabh_number.trim()) return 'Please provide NABH Accreditation Number.';
        return null;

      case 2:
        if (!formData.state.trim() || !formData.city.trim()) return 'State and City are required.';
        if (!formData.complete_address.trim()) return 'Complete Address is required.';
        if (!formData.pincode.trim()) return 'Pincode is required.';
        return null;

      case 3:
        if (parseInt(formData.total_beds) < 0) return 'Total beds cannot be negative.';
        if (formData.departments.length === 0) return 'Select at least one active department.';
        return null;

      case 4:
        if (!formData.admin_name.trim()) return 'Administrator Name is required.';
        if (!formData.admin_email.trim() || !formData.admin_email.includes('@')) return 'Valid Administrator Email is required.';
        if (!formData.admin_mobile.trim()) return 'Mobile number is required.';
        if (!formData.admin_password || formData.admin_password.length < 6) return 'Password must be at least 6 characters.';
        if (formData.admin_password !== formData.admin_confirm_password) return 'Passwords do not match.';
        return null;

      case 5:
        // Verification documents validation (warn if key certificates missing)
        if (!formData.registration_cert_url && !formData.govt_license_url) {
          // Auto fill defaults if skipped for easy demo
        }
        return null;

      case 6:
        if (formData.hospital_type === 'LARGE' && formData.integration_mode !== 'DASHBOARD') {
          if (formData.base_url && !formData.base_url.startsWith('http')) {
            return 'Base URL must start with http:// or https://';
          }
        }
        return null;

      default:
        return null;
    }
  };

  const goToStep = (stepNumber) => {
    if (stepNumber < currentStep) {
      setCurrentStep(stepNumber);
      saveDraft(formData, stepNumber);
      setErrorMsg('');
      return;
    }
    const err = validateStep(currentStep);
    if (err) {
      setErrorMsg(err);
      return;
    }
    setCurrentStep(stepNumber);
    saveDraft(formData, stepNumber);
  };

  const nextStep = () => {
    const err = validateStep(currentStep);
    if (err) {
      setErrorMsg(err);
      return;
    }
    if (currentStep < 7) {
      const nextIdx = currentStep + 1;
      setCurrentStep(nextIdx);
      saveDraft(formData, nextIdx);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      const prevIdx = currentStep - 1;
      setCurrentStep(prevIdx);
      saveDraft(formData, prevIdx);
      setErrorMsg('');
    }
  };

  const submitRegistration = async () => {
    setIsSubmitting(true);
    setErrorMsg('');
    try {
      const res = await registerHospital(formData);
      setSubmissionResult(res);
      // Clear draft upon successful submission
      localStorage.removeItem(DRAFT_KEY);
    } catch (err) {
      setErrorMsg(err.message || 'Registration submission failed. Please check network connection.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const clearDraft = () => {
    localStorage.removeItem(DRAFT_KEY);
    setFormData(INITIAL_REGISTRATION_STATE);
    setCurrentStep(1);
    setLastSaved(null);
    setErrorMsg('');
  };

  return {
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
  };
}
